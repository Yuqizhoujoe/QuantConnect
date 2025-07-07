from AlgorithmImports import *  # type: ignore
from config.common_config_loader import ConfigLoader, Config
from typing import Dict, Any
from datetime import timedelta
from shared.utils.constants import (
    DEFAULT_DAYS_TO_EXPIRATION_MIN,
    DEFAULT_DAYS_TO_EXPIRATION_MAX,
    DEFAULT_STRIKES_BELOW,
    DEFAULT_STRIKES_ABOVE,
    SUCCESS_STRATEGY_INITIALIZED,
)

from .components.portfolio_manager import PortfolioManager
from .components.scheduler import Scheduler
from .components.evaluator import Evaluator


class SellPutOptionStrategy(QCAlgorithm):  # type: ignore
    """
    A unified strategy that sells short put options across single or multiple stocks.

    This strategy supports:
    - Single stock trading (just add one stock to the list)
    - Multiple stocks with individual configurations
    - Portfolio-level risk management
    - Smart trade selection across stocks
    - Comprehensive performance tracking

    The strategy uses the same codebase for both single and multi-stock scenarios,
    making it easier to maintain and extend.
    """

    def Initialize(self, start_date, end_date, config_path) -> None:
        """
        Initializes the algorithm, loads configuration, and sets up all components.
        This method is called once at the very beginning of the algorithm's lifecycle.
        """
        # Set backtest start and end dates
        self.SetStartDate(start_date)
        self.SetEndDate(end_date)

        # Load configuration from config file
        self.config: Config = ConfigLoader.load_config(config_path)
        self.Log(f"Configuration loaded - {len(self.config.stocks)} stocks configured")

        # Set up equity and option subscriptions for all configured stocks
        self.option_symbols: Dict[str, Any] = {}
        self.stock_symbols: Dict[str, Any] = {}

        for stock_config in self.config.stocks:
            ticker: str = stock_config["ticker"]
            if stock_config.get("enabled", True):
                # Add equity subscription
                self.stock_symbols[ticker] = self.AddEquity(ticker, Resolution.Minute)  # type: ignore

                # Add option subscription
                option: Any = self.AddOption(ticker, Resolution.Minute)  # type: ignore
                self.option_symbols[ticker] = option.Symbol

                # Set option filter for each stock using constants
                option.SetFilter(
                    DEFAULT_STRIKES_BELOW,
                    DEFAULT_STRIKES_ABOVE,
                    timedelta(DEFAULT_DAYS_TO_EXPIRATION_MIN),
                    timedelta(DEFAULT_DAYS_TO_EXPIRATION_MAX),
                )

                self.Log(f"Added subscriptions for {ticker}")

        # --- Portfolio State Variables ---
        # Note: All portfolio tracking is now handled by the PortfolioManager
        # These variables are kept for compatibility with existing components
        self.peak_portfolio_value: float = self.Portfolio.TotalPortfolioValue

        # --- Initialize Portfolio Management ---
        self.portfolio_manager: PortfolioManager = PortfolioManager(
            strategy=self,
            stock_managers={},
            total_trades=0,
            portfolio_pnl=0.0,
            peak_portfolio_value=self.Portfolio.TotalPortfolioValue,
            daily_portfolio_pnl=[],
            max_stocks=self.config.max_stocks or 1,
            max_portfolio_risk=self.config.max_portfolio_risk or 0.02,
            max_drawdown=self.config.max_drawdown or 0.15,
            portfolio_returns=[],
            portfolio_volatility=[],
        )

        # Initialize stock managers (includes criteria manager setup)
        self.portfolio_manager.initialize_stocks(self.config.stocks)
        self.Log(f"Stock managers initialized: {len(self.portfolio_manager.stock_managers)}")

        # --- Initialize Helper Modules ---
        self.scheduler: Scheduler = Scheduler(strategy=self)
        self.evaluator: Evaluator = Evaluator(strategy=self)

        # Set up the scheduled event to evaluate the strategy logic periodically
        self.scheduler.setup_events()

        # Set the benchmark (use first stock or SPY)
        benchmark_ticker: str = (
            self.config.stocks[0]["ticker"] if self.config.stocks else "SPY"
        )
        self.SetBenchmark(benchmark_ticker)

        # Set up minimal essential plotting for cloud backtesting
        self.Plot("Strategy", "Portfolio Value", self.Portfolio.TotalPortfolioValue)

        stock_count = len(self.portfolio_manager.stock_managers)
        strategy_type = "single-stock" if stock_count == 1 else "multi-stock"
        self.Log(f"{strategy_type.title()} strategy initialized with {stock_count} stock(s)")
        self.Log(SUCCESS_STRATEGY_INITIALIZED)

    def OnData(self, slice: Slice) -> None:  # type: ignore
        """
        Event handler that is called for each new data point.
        This method delegates data handling to the PortfolioManager.

        Args:
            slice: The new data slice from the engine.
        """
        # Update portfolio data
        self.portfolio_manager.update_portfolio_data(slice)

        # Manage positions across all stocks
        self.portfolio_manager.manage_positions()

        # Update essential portfolio plot (only once per day to save data points)
        if self.Time.hour == 9 and self.Time.minute == 30:  # Market open
            self.Plot("Strategy", "Portfolio Value", self.Portfolio.TotalPortfolioValue)

    def OnEndOfAlgorithm(self) -> None:
        """
        Event handler that is called at the very end of the algorithm's execution.
        This method delegates the final evaluation and logging to the Evaluator module.
        """
        self.evaluator.on_end_of_algorithm()



