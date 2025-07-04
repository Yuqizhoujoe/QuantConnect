# Strategy Configuration File
# Modify these parameters to customize your options strategy

class StrategyConfig:
    # Backtest Period
    START_DATE = (2020, 1, 1)
    END_DATE = (2025, 1, 1)
    INITIAL_CASH = 100000
    
    # Asset Configuration
    TICKER = "AVGO"  # Change to any stock symbol
    RESOLUTION = Resolution.Minute
    
    # Options Filter Parameters
    MIN_STRIKE_OFFSET = -2  # Relative to current price
    MAX_STRIKE_OFFSET = +1
    MIN_DAYS_TO_EXPIRY = 20
    MAX_DAYS_TO_EXPIRY = 60
    
    # Strategy Parameters
    TARGET_DELTA_MIN = 0.44  # Minimum delta for put selection
    TARGET_DELTA_MAX = 0.50  # Maximum delta for put selection
    MAX_POSITION_SIZE = 0.05  # 5% of portfolio per trade
    MAX_PORTFOLIO_RISK = 0.20  # 20% max portfolio risk
    
    # Risk Management
    PROFIT_TARGET_PCT = 0.50  # Close at 50% of max profit
    STOP_LOSS_MULTIPLIER = 2.0  # Close at 2x max profit loss
    MIN_DAYS_BEFORE_EXPIRY = 5  # Close positions 5 days before expiry
    MIN_MARGIN_REQUIRED = 10000  # Minimum margin to enter new positions
    
    # Trading Schedule
    EVALUATION_TIME = (10, 0)  # 10:00 AM
    
    # Performance Tracking
    ENABLE_DETAILED_LOGGING = True
    TRACK_DAILY_PNL = True
    
    # Advanced Options
    USE_IMPLIED_VOLATILITY_FILTER = False
    MIN_IV = 0.20  # Minimum implied volatility
    MAX_IV = 0.80  # Maximum implied volatility
    
    # Position Sizing
    USE_FIXED_QUANTITY = False
    FIXED_QUANTITY = 1  # Use if USE_FIXED_QUANTITY is True
    
    # Market Conditions Filter
    ENABLE_MARKET_FILTERS = False
    MIN_UNDERLYING_PRICE = 50  # Minimum underlying price
    MAX_UNDERLYING_PRICE = 1000  # Maximum underlying price
    
    # Volatility Regime Filter
    ENABLE_VOLATILITY_FILTER = False
    MIN_HISTORICAL_VOL = 0.15  # Minimum 30-day historical volatility
    MAX_HISTORICAL_VOL = 0.60  # Maximum 30-day historical volatility 