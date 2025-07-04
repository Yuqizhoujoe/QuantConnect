# region imports
from AlgorithmImports import *
from enhanced_broadcom_strategy import EnhancedBroadcomShortPutStrategy
# endregion

class OptionsBacktestingStrategy(EnhancedBroadcomShortPutStrategy):
    """
    Main options backtesting strategy class.
    Inherits from EnhancedBroadcomShortPutStrategy for all functionality.
    """
    
    def Initialize(self):
        """
        Initialize the strategy with custom configuration.
        Override this method to customize parameters.
        """
        # Load configuration
        self.config = StrategyConfig()
        
        # Customize parameters for this specific backtest
        self.config.START_DATE = (2020, 1, 1)
        self.config.END_DATE = (2024, 12, 31)
        self.config.INITIAL_CASH = 100000
        self.config.TICKER = "AVGO"  # Broadcom
        
        # Strategy parameters
        self.config.MAX_POSITION_SIZE = 0.05  # 5% per trade
        self.config.TARGET_DELTA_MIN = 0.44
        self.config.TARGET_DELTA_MAX = 0.50
        self.config.MIN_DAYS_TO_EXPIRY = 20
        self.config.MAX_DAYS_TO_EXPIRY = 60
        
        # Risk management
        self.config.PROFIT_TARGET_PCT = 0.50
        self.config.STOP_LOSS_MULTIPLIER = 2.0
        self.config.MIN_DAYS_BEFORE_EXPIRY = 5
        
        # Enable detailed logging
        self.config.ENABLE_DETAILED_LOGGING = True
        self.config.TRACK_DAILY_PNL = True
        
        # Call parent Initialize to set up the strategy
        super().Initialize()
