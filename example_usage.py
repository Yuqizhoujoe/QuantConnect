# Example Usage Script for Options Backtesting Strategy
# This file demonstrates how to modify the strategy for different use cases

from AlgorithmImports import *
from enhanced_broadcom_strategy import EnhancedBroadcomShortPutStrategy
from strategy_config import StrategyConfig

# Example 1: Conservative Strategy for Apple
class ConservativeAppleStrategy(EnhancedBroadcomShortPutStrategy):
    def Initialize(self):
        # Override configuration for conservative Apple strategy
        self.config = StrategyConfig()
        self.config.TICKER = "AAPL"
        self.config.MAX_POSITION_SIZE = 0.03  # 3% per trade
        self.config.TARGET_DELTA_MIN = 0.30   # More OTM
        self.config.TARGET_DELTA_MAX = 0.40
        self.config.STOP_LOSS_MULTIPLIER = 1.5  # Tighter stop loss
        self.config.ENABLE_VOLATILITY_FILTER = True
        self.config.MIN_HISTORICAL_VOL = 0.20
        self.config.MAX_HISTORICAL_VOL = 0.50
        
        # Call parent Initialize
        super().Initialize()

# Example 2: Aggressive Tesla Strategy
class AggressiveTeslaStrategy(EnhancedBroadcomShortPutStrategy):
    def Initialize(self):
        # Override configuration for aggressive Tesla strategy
        self.config = StrategyConfig()
        self.config.TICKER = "TSLA"
        self.config.MAX_POSITION_SIZE = 0.08  # 8% per trade
        self.config.TARGET_DELTA_MIN = 0.45   # More ATM
        self.config.TARGET_DELTA_MAX = 0.55
        self.config.STOP_LOSS_MULTIPLIER = 3.0  # Wider stop loss
        self.config.ENABLE_MARKET_FILTERS = True
        self.config.MIN_UNDERLYING_PRICE = 100
        self.config.MAX_UNDERLYING_PRICE = 500
        
        # Call parent Initialize
        super().Initialize()

# Example 3: SPY ETF Strategy with High Frequency
class SPYHighFrequencyStrategy(EnhancedBroadcomShortPutStrategy):
    def Initialize(self):
        # Override configuration for SPY strategy
        self.config = StrategyConfig()
        self.config.TICKER = "SPY"
        self.config.MAX_POSITION_SIZE = 0.05  # 5% per trade
        self.config.MIN_DAYS_TO_EXPIRY = 7    # Shorter expiration
        self.config.MAX_DAYS_TO_EXPIRY = 30
        self.config.PROFIT_TARGET_PCT = 0.30  # Take profits earlier
        self.config.USE_FIXED_QUANTITY = True
        self.config.FIXED_QUANTITY = 1
        
        # Call parent Initialize
        super().Initialize()

# Example 4: Custom Strategy with Multiple Filters
class CustomFilteredStrategy(EnhancedBroadcomShortPutStrategy):
    def Initialize(self):
        # Override configuration for custom strategy
        self.config = StrategyConfig()
        self.config.TICKER = "NVDA"  # NVIDIA
        self.config.MAX_POSITION_SIZE = 0.04  # 4% per trade
        self.config.TARGET_DELTA_MIN = 0.40
        self.config.TARGET_DELTA_MAX = 0.50
        self.config.ENABLE_VOLATILITY_FILTER = True
        self.config.MIN_HISTORICAL_VOL = 0.25
        self.config.MAX_HISTORICAL_VOL = 0.70
        self.config.ENABLE_MARKET_FILTERS = True
        self.config.MIN_UNDERLYING_PRICE = 200
        self.config.MAX_UNDERLYING_PRICE = 800
        self.config.USE_IMPLIED_VOLATILITY_FILTER = True
        self.config.MIN_IV = 0.25
        self.config.MAX_IV = 0.75
        
        # Call parent Initialize
        super().Initialize()

# Example 5: Income Strategy (Higher Delta, Longer Expiration)
class IncomeStrategy(EnhancedBroadcomShortPutStrategy):
    def Initialize(self):
        # Override configuration for income generation
        self.config = StrategyConfig()
        self.config.TICKER = "MSFT"  # Microsoft
        self.config.MAX_POSITION_SIZE = 0.06  # 6% per trade
        self.config.TARGET_DELTA_MIN = 0.50   # ATM to slightly ITM
        self.config.TARGET_DELTA_MAX = 0.60
        self.config.MIN_DAYS_TO_EXPIRY = 30   # Longer expiration
        self.config.MAX_DAYS_TO_EXPIRY = 90
        self.config.PROFIT_TARGET_PCT = 0.70  # Hold longer for more profit
        self.config.STOP_LOSS_MULTIPLIER = 2.5
        
        # Call parent Initialize
        super().Initialize()

# Example 6: Quick Scalping Strategy
class ScalpingStrategy(EnhancedBroadcomShortPutStrategy):
    def Initialize(self):
        # Override configuration for quick scalping
        self.config = StrategyConfig()
        self.config.TICKER = "QQQ"  # Invesco QQQ Trust
        self.config.MAX_POSITION_SIZE = 0.03  # Smaller positions
        self.config.TARGET_DELTA_MIN = 0.35   # OTM for quick decay
        self.config.TARGET_DELTA_MAX = 0.45
        self.config.MIN_DAYS_TO_EXPIRY = 5    # Very short expiration
        self.config.MAX_DAYS_TO_EXPIRY = 14
        self.config.PROFIT_TARGET_PCT = 0.25  # Quick profit taking
        self.config.STOP_LOSS_MULTIPLIER = 1.5  # Tight stop loss
        
        # Call parent Initialize
        super().Initialize()

# Example 7: Defensive Strategy for Market Downturns
class DefensiveStrategy(EnhancedBroadcomShortPutStrategy):
    def Initialize(self):
        # Override configuration for defensive strategy
        self.config = StrategyConfig()
        self.config.TICKER = "SPY"  # S&P 500 ETF
        self.config.MAX_POSITION_SIZE = 0.02  # Very small positions
        self.config.TARGET_DELTA_MIN = 0.25   # Far OTM
        self.config.TARGET_DELTA_MAX = 0.35
        self.config.MIN_DAYS_TO_EXPIRY = 45   # Longer expiration
        self.config.MAX_DAYS_TO_EXPIRY = 120
        self.config.PROFIT_TARGET_PCT = 0.80  # Hold for maximum profit
        self.config.STOP_LOSS_MULTIPLIER = 4.0  # Very wide stop loss
        self.config.ENABLE_VOLATILITY_FILTER = True
        self.config.MIN_HISTORICAL_VOL = 0.15  # Only trade in low volatility
        
        # Call parent Initialize
        super().Initialize()

# Example 8: Momentum Strategy
class MomentumStrategy(EnhancedBroadcomShortPutStrategy):
    def Initialize(self):
        # Override configuration for momentum-based strategy
        self.config = StrategyConfig()
        self.config.TICKER = "AMD"  # Advanced Micro Devices
        self.config.MAX_POSITION_SIZE = 0.07  # Larger positions
        self.config.TARGET_DELTA_MIN = 0.40
        self.config.TARGET_DELTA_MAX = 0.50
        self.config.MIN_DAYS_TO_EXPIRY = 10   # Short expiration
        self.config.MAX_DAYS_TO_EXPIRY = 30
        self.config.PROFIT_TARGET_PCT = 0.40
        self.config.STOP_LOSS_MULTIPLIER = 2.0
        self.config.ENABLE_VOLATILITY_FILTER = True
        self.config.MIN_HISTORICAL_VOL = 0.30  # Higher volatility required
        self.config.MAX_HISTORICAL_VOL = 0.80
        
        # Call parent Initialize
        super().Initialize()

# Usage Instructions:
# 1. Choose the strategy class that best fits your requirements
# 2. Copy the chosen class to your QuantConnect project
# 3. Modify the parameters as needed
# 4. Run the backtest

# Example of how to modify parameters for your specific needs:
def create_custom_strategy():
    """
    Example function showing how to create a custom strategy
    """
    class MyCustomStrategy(EnhancedBroadcomShortPutStrategy):
        def Initialize(self):
            # Start with default configuration
            self.config = StrategyConfig()
            
            # Modify parameters for your specific needs
            self.config.TICKER = "GOOGL"  # Google
            self.config.START_DATE = (2022, 1, 1)
            self.config.END_DATE = (2024, 12, 31)
            self.config.INITIAL_CASH = 50000
            
            # Strategy parameters
            self.config.MAX_POSITION_SIZE = 0.04
            self.config.TARGET_DELTA_MIN = 0.35
            self.config.TARGET_DELTA_MAX = 0.45
            self.config.MIN_DAYS_TO_EXPIRY = 15
            self.config.MAX_DAYS_TO_EXPIRY = 45
            
            # Risk management
            self.config.PROFIT_TARGET_PCT = 0.60
            self.config.STOP_LOSS_MULTIPLIER = 2.5
            
            # Enable filters
            self.config.ENABLE_VOLATILITY_FILTER = True
            self.config.MIN_HISTORICAL_VOL = 0.20
            self.config.MAX_HISTORICAL_VOL = 0.60
            
            # Call parent Initialize
            super().Initialize()
    
    return MyCustomStrategy

# To use this in QuantConnect:
# 1. Copy the create_custom_strategy() function
# 2. Modify the parameters as needed
# 3. Use the returned class as your main strategy class 