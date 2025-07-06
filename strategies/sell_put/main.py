
# region imports
from AlgorithmImports import *
from typing import Dict, List, Any
from datetime import timedelta
from .portfolio_manager import PortfolioManager
from config.common_config_loader import ConfigLoader
from core.scheduler import Scheduler
from .evaluator import Evaluator
# endregion

class ConfigurableShortPutStrategy(QCAlgorithm):
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

    def Initialize(self) -> None:
        """
        Initializes the algorithm, loads configuration, and sets up all components.
        This method is called once at the very beginning of the algorithm's lifecycle.
        """
        # Initialize parameters attribute
        self.parameters = {}
        
        # Create the configuration loader and load parameters from config file
        self.config_loader: ConfigLoader = ConfigLoader(self)
        self.config_loader.load_config('sell_put_multi_stock.json')

        # Set up equity and option subscriptions for all configured stocks
        self.option_symbols: Dict[str, Any] = {}
        self.stock_symbols: Dict[str, Any] = {}
        
        for stock_config in self.parameters.get('stocks', []):
            ticker: str = stock_config['ticker']
            if stock_config.get('enabled', True):
                # Add equity subscription
                self.stock_symbols[ticker] = self.AddEquity(ticker, Resolution.Minute)
                
                # Add option subscription
                option: Any = self.AddOption(ticker, Resolution.Minute)
                self.option_symbols[ticker] = option.Symbol
                
                # Set option filter for each stock (14-45 days, 2 strikes below, 1 above)
                option.SetFilter(-2, +1, timedelta(14), timedelta(45))
                
                self.Log(f"Added subscriptions for {ticker}")

        # --- Portfolio State Variables ---
        # Note: All portfolio tracking is now handled by the PortfolioManager
        # These variables are kept for compatibility but not actively used
        self.peak_portfolio_value: float = self.Portfolio.TotalPortfolioValue

        # --- Initialize Portfolio Management ---
        portfolio_config: Dict[str, Any] = self.parameters.get('portfolio', {})
        self.portfolio_manager: PortfolioManager = PortfolioManager(self, portfolio_config)
        
        # Initialize stock managers
        stocks_config: List[Dict[str, Any]] = self.parameters.get('stocks', [])
        self.portfolio_manager.initialize_stocks(stocks_config)

        # --- Initialize Helper Modules ---
        self.scheduler: Scheduler = Scheduler(self, self.portfolio_manager)
        self.evaluator: Evaluator = Evaluator(self)

        # Set up the scheduled event to evaluate the strategy logic periodically
        self.scheduler.setup_events()
        
        # Set the benchmark (use first stock or SPY)
        benchmark_ticker: str = stocks_config[0]['ticker'] if stocks_config else "SPY"
        self.SetBenchmark(benchmark_ticker)
        
        # Set up minimal essential plotting for cloud backtesting
        self.Plot("Strategy", "Portfolio Value", self.Portfolio.TotalPortfolioValue)
        
        stock_count = len(self.portfolio_manager.stock_managers)
        strategy_type = "single-stock" if stock_count == 1 else "multi-stock"
        self.Log(f"{strategy_type.title()} strategy initialized with {stock_count} stock(s)")

    def OnData(self, slice: Slice) -> None:
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


class SellPutOption(ConfigurableShortPutStrategy):
    """
    Main strategy class that inherits from the multi-stock base strategy.
    This is the class that QuantConnect will instantiate when running the algorithm.
    """
    pass
