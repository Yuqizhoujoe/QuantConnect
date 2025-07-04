
# region imports
from AlgorithmImports import *
from data_handler import DataHandler
from position_manager import PositionManager
from trade_executor import TradeExecutor
from scheduler import Scheduler
from evaluator import Evaluator
from config_loader import ConfigLoader
from risk_manager import RiskManager
from market_analyzer import MarketAnalyzer
# endregion

class ConfigurableShortPutStrategy(QCAlgorithm):
    """
    A configurable strategy that sells short put options based on parameters
    defined in a JSON configuration file.
    
    This class is the main orchestrator of the algorithm. It initializes all the
    helper modules (like data handling, position management, etc.) and delegates
    the core logic to them.
    """

    def Initialize(self):
        """
        Initializes the algorithm, loads configuration, and sets up all components.
        This method is called once at the very beginning of the algorithm's lifecycle.
        """
        # Create the configuration loader and load parameters from config.json
        self.config_loader = ConfigLoader(self)
        self.config_loader.load_config()

        # Set up the primary equity and option subscriptions
        self.AddEquity(self.ticker, Resolution.Minute)
        self.option = self.AddOption(self.ticker, Resolution.Minute)
        
        # Set a filter for the option contracts to consider.
        # This filter selects contracts with an expiry between 14 and 45 days.
        self.option.SetFilter(-2, +1, timedelta(14), timedelta(45))

        # --- Strategy State Variables ---
        self.current_contract = None      # Holds the currently open option contract
        self.last_trade_date = None       # Tracks the date of the last trade to avoid over-trading
        self.trade_count = 0              # Counter for the total number of trades
        self.profit_loss = 0              # Running total of profit and loss
        self.trades = []                  # A list to store details of each trade
        self.daily_pnl = []               # A list to track daily profit and loss
        self.peak_portfolio_value = self.Portfolio.TotalPortfolioValue  # Track peak for drawdown calculation

        # --- Initialize Helper Modules ---
        # Each module handles a specific part of the strategy's logic.
        self.data_handler = DataHandler(self)
        self.risk_manager = RiskManager(self)
        self.market_analyzer = MarketAnalyzer(self)
        self.position_manager = PositionManager(self, self.data_handler)
        self.trade_executor = TradeExecutor(self)
        self.scheduler = Scheduler(self, self.position_manager)
        self.evaluator = Evaluator(self)

        # Set up the scheduled event to evaluate the strategy logic periodically.
        self.scheduler.setup_events()
        
        # Set the benchmark for performance comparison.
        self.SetBenchmark(self.ticker)

    def OnData(self, slice: Slice):
        """
        Event handler that is called for each new data point (tick, bar, etc.).
        This method delegates the data handling to the DataHandler module.
        
        Args:
            slice: The new data slice from the engine.
        """
        self.data_handler.on_data(slice)

    def OnEndOfAlgorithm(self):
        """
        Event handler that is called at the very end of the algorithm's execution.
        This method delegates the final evaluation and logging to the Evaluator module.
        """
        self.evaluator.on_end_of_algorithm()


class SellPutOption(ConfigurableShortPutStrategy):
    """
    Main strategy class that inherits from the configurable base strategy.
    This is the class that QuantConnect will instantiate when running the algorithm.
    """
    pass
