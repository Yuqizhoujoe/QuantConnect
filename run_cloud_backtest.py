# type: ignore
"""
QuantConnect Cloud Backtest Entry Point

This file is specifically designed for QuantConnect cloud backtesting.
It uses hardcoded configuration to avoid file loading issues in the cloud environment.

Features:
- Hardcoded configuration (no external files needed)
- Same strategy as regular backtest (SellPutOptionStrategy)
- 2020-2024 backtest period
- Comprehensive logging for debugging
- Robust error handling
- Position management and risk controls
"""

from AlgorithmImports import *  # type: ignore
from strategies.sell_put.sell_put_strategy import SellPutOptionStrategy
from config.common_config_loader import Config
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class CloudConfig:
    """
    Hardcoded configuration for QuantConnect cloud backtesting.
    """
    # Portfolio settings - much looser for easier trading
    total_cash: int = 100000
    max_stocks: int = 1
    max_portfolio_risk: float = 0.05  # Was 0.02 - much higher
    max_drawdown: float = 0.20  # Was 0.15 - more tolerant
    correlation_threshold: float = 0.7

    # Stock configurations - much looser delta ranges
    stocks: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "ticker": "AAPL",
            "weight": 1.0,
            "target_delta_min": 0.15,  # Was 0.25 - much lower
            "target_delta_max": 0.85,  # Was 0.75 - much higher
            "max_position_size": 0.30,  # Was 0.20 - larger positions
            "option_frequency": "any",  # Was "monthly" - trade anytime
            "enabled": True,
            "criteria": {
                "type": "delta_only",
                "config": {
                    "delta": {
                        "target_min": 0.15,  # Was 0.25 - much lower
                        "target_max": 0.85,  # Was 0.75 - much higher
                        "weight": 1.0
                    }
                }
            }
        }
    ])

    # Risk management settings - more tolerant
    volatility_lookback: int = 20
    volatility_threshold: float = 0.6  # Was 0.4 - more tolerant
    correlation_lookback: int = 60

    # Market analysis settings
    rsi_period: int = 14
    moving_average_period: int = 50
    market_volatility_lookback: int = 20

    # Legacy single-stock settings (for backward compatibility) - updated to match
    ticker: str = "AAPL"
    target_delta_min: float = 0.15  # Was 0.25 - much lower
    target_delta_max: float = 0.85  # Was 0.75 - much higher
    max_position_size: float = 0.30  # Was 0.20 - larger positions
    option_frequency: str = "any"  # Was "monthly" - trade anytime
    start_date: str = "2020-01-01"
    end_date: str = "2024-12-31"


class CloudSellPutStrategy(SellPutOptionStrategy):  # type: ignore
    """
    Cloud version of the sell put strategy with hardcoded configuration.
    Inherits from the same SellPutOptionStrategy but uses hardcoded config.
    """

    def Initialize(self) -> None:
        """
        Initialize the algorithm with hardcoded configuration.
        """
        from datetime import datetime

        # Set backtest period
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        # Create hardcoded config object
        cloud_config = CloudConfig()
        
        # Convert to Config object that the strategy expects
        config = Config(
            # Portfolio settings
            total_cash=cloud_config.total_cash,
            max_stocks=cloud_config.max_stocks,
            max_portfolio_risk=cloud_config.max_portfolio_risk,
            max_drawdown=cloud_config.max_drawdown,
            correlation_threshold=cloud_config.correlation_threshold,
            # Stocks configuration
            stocks=cloud_config.stocks,
            # Risk management settings
            volatility_lookback=cloud_config.volatility_lookback,
            volatility_threshold=cloud_config.volatility_threshold,
            correlation_lookback=cloud_config.correlation_lookback,
            # Market analysis settings
            rsi_period=cloud_config.rsi_period,
            moving_average_period=cloud_config.moving_average_period,
            market_volatility_lookback=cloud_config.market_volatility_lookback,
            # Legacy single-stock settings
            ticker=cloud_config.ticker,
            target_delta_min=cloud_config.target_delta_min,
            target_delta_max=cloud_config.target_delta_max,
            max_position_size=cloud_config.max_position_size,
            option_frequency=cloud_config.option_frequency,
            start_date=cloud_config.start_date,
            end_date=cloud_config.end_date,
        )
        
        # Store the config in the strategy
        self.config = config
        
        # Log configuration
        self.Log("=== CLOUD SELL PUT STRATEGY INITIALIZED ===")
        self.Log(f"Backtest Period: {start_date.date()} to {end_date.date()}")
        self.Log(f"Initial Cash: ${self.config.total_cash:,}")
        self.Log(f"Max Stocks: {self.config.max_stocks}")
        self.Log(f"Stocks Configured: {len(self.config.stocks)}")
        
        for i, stock in enumerate(self.config.stocks):
            self.Log(f"Stock {i+1}: {stock['ticker']} (enabled: {stock['enabled']})")

        # Set up equity and option subscriptions for all configured stocks
        self.option_symbols: Dict[str, Any] = {}
        self.stock_symbols: Dict[str, Any] = {}

        for stock_config in self.config.stocks:
            ticker: str = stock_config["ticker"]
            if stock_config.get("enabled", True):
                try:
                    # Add equity subscription
                    self.stock_symbols[ticker] = self.AddEquity(ticker, Resolution.Minute)  # type: ignore
                    self.Log(f"Added equity subscription for {ticker}")

                    # Add option subscription
                    option: Any = self.AddOption(ticker, Resolution.Minute)  # type: ignore
                    self.option_symbols[ticker] = option.Symbol

                    # Set option filter for each stock using constants
                    from shared.utils.constants import (
                        DEFAULT_DAYS_TO_EXPIRATION_MIN,
                        DEFAULT_DAYS_TO_EXPIRATION_MAX,
                        DEFAULT_STRIKES_BELOW,
                        DEFAULT_STRIKES_ABOVE,
                    )
                    from datetime import timedelta
                    
                    option.SetFilter(
                        DEFAULT_STRIKES_BELOW,
                        DEFAULT_STRIKES_ABOVE,
                        timedelta(DEFAULT_DAYS_TO_EXPIRATION_MIN),
                        timedelta(DEFAULT_DAYS_TO_EXPIRATION_MAX),
                    )

                    self.Log(f"Added option subscription for {ticker}")
                except Exception as e:
                    self.Log(f"Error adding subscriptions for {ticker}: {str(e)}")

        # --- Portfolio State Variables ---
        # Note: All portfolio tracking is now handled by the PortfolioManager
        # These variables are kept for compatibility with existing components
        self.peak_portfolio_value: float = self.Portfolio.TotalPortfolioValue

        # --- Initialize Portfolio Management ---
        from strategies.sell_put.components.portfolio_manager import PortfolioManager
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
        from strategies.sell_put.components.scheduler import Scheduler
        from strategies.sell_put.components.evaluator import Evaluator
        
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
        
        from shared.utils.constants import SUCCESS_STRATEGY_INITIALIZED
        self.Log(SUCCESS_STRATEGY_INITIALIZED)
        
        self.Log("Cloud strategy initialization complete")

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
