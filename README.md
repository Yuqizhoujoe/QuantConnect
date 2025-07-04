# Options Backtesting Strategy for QuantConnect

This repository contains comprehensive options trading strategies for backtesting on QuantConnect, specifically designed for short put strategies on Broadcom (AVGO) and other stocks.

## Files Overview

### 1. `broadcom_short_put_strategy.py`

Basic implementation of a short put strategy with essential risk management features.

### 2. `enhanced_broadcom_strategy.py`

Advanced implementation with additional features including:

- Volatility filters
- Market condition checks
- Enhanced risk management
- Performance tracking
- Configuration-driven parameters

### 3. `strategy_config.py`

Configuration file to easily modify strategy parameters without changing the main algorithm code.

## Strategy Overview

The strategy implements a **short put options strategy** with the following characteristics:

- **Target Delta Range**: 0.44-0.50 (slightly OTM puts)
- **Expiration Range**: 20-60 days
- **Position Sizing**: 5% of portfolio per trade
- **Risk Management**: Profit targets and stop losses
- **Market Filters**: Optional volatility and price range filters

## How to Use

### 1. Basic Strategy

1. Copy `broadcom_short_put_strategy.py` to your QuantConnect project
2. Upload the file to QuantConnect
3. Run the backtest

### 2. Enhanced Strategy

1. Copy both `enhanced_broadcom_strategy.py` and `strategy_config.py` to your QuantConnect project
2. Upload both files to QuantConnect
3. Modify parameters in `strategy_config.py` as needed
4. Run the backtest

## Configuration Options

### Basic Parameters

```python
# Backtest Period
START_DATE = (2020, 1, 1)
END_DATE = (2025, 1, 1)
INITIAL_CASH = 100000

# Asset Configuration
TICKER = "AVGO"  # Change to any stock symbol
```

### Strategy Parameters

```python
# Options Filter
TARGET_DELTA_MIN = 0.44  # Minimum delta for put selection
TARGET_DELTA_MAX = 0.50  # Maximum delta for put selection
MIN_DAYS_TO_EXPIRY = 20
MAX_DAYS_TO_EXPIRY = 60

# Risk Management
MAX_POSITION_SIZE = 0.05  # 5% of portfolio per trade
PROFIT_TARGET_PCT = 0.50  # Close at 50% of max profit
STOP_LOSS_MULTIPLIER = 2.0  # Close at 2x max profit loss
```

### Advanced Filters

```python
# Volatility Filter
ENABLE_VOLATILITY_FILTER = False
MIN_HISTORICAL_VOL = 0.15
MAX_HISTORICAL_VOL = 0.60

# Market Conditions Filter
ENABLE_MARKET_FILTERS = False
MIN_UNDERLYING_PRICE = 50
MAX_UNDERLYING_PRICE = 1000
```

## Strategy Logic

### Entry Conditions

1. No existing positions
2. Sufficient margin available
3. Options with delta in target range (0.44-0.50)
4. Expiration between 20-60 days
5. Market conditions meet filter criteria (if enabled)

### Exit Conditions

1. **Profit Target**: Close when 50% of maximum profit is reached
2. **Stop Loss**: Close when loss reaches 2x the maximum profit
3. **Expiration**: Close positions 5 days before expiration
4. **Market Conditions**: Close if market conditions deteriorate

### Position Sizing

- Maximum 5% of portfolio per trade
- Based on margin requirements
- Respects available margin limits

## Performance Metrics

The strategy tracks and reports:

- Total number of trades
- Win rate
- Average win/loss
- Total P&L
- Maximum drawdown
- Total return

## Risk Management Features

1. **Position Sizing**: Limits exposure per trade
2. **Profit Targets**: Takes profits at predetermined levels
3. **Stop Losses**: Limits downside risk
4. **Expiration Management**: Avoids holding to expiration
5. **Margin Monitoring**: Ensures sufficient margin for new positions
6. **Market Filters**: Optional filters for volatility and price ranges

## Customization

### Changing the Underlying Stock

Modify the `TICKER` parameter in `strategy_config.py`:

```python
TICKER = "AAPL"  # For Apple
TICKER = "TSLA"  # For Tesla
TICKER = "SPY"   # For SPDR S&P 500 ETF
```

### Adjusting Risk Parameters

```python
# More conservative
MAX_POSITION_SIZE = 0.03  # 3% per trade
STOP_LOSS_MULTIPLIER = 1.5  # Tighter stop loss

# More aggressive
MAX_POSITION_SIZE = 0.10  # 10% per trade
STOP_LOSS_MULTIPLIER = 3.0  # Wider stop loss
```

### Modifying Delta Range

```python
# More OTM (lower probability of profit)
TARGET_DELTA_MIN = 0.30
TARGET_DELTA_MAX = 0.40

# More ATM (higher probability of profit)
TARGET_DELTA_MIN = 0.45
TARGET_DELTA_MAX = 0.55
```

## Important Notes

1. **Options Data**: Ensure your QuantConnect account has access to options data
2. **Margin Requirements**: The strategy includes simplified margin calculations
3. **Greeks**: Strategy relies on option Greeks (Delta) for contract selection
4. **Liquidity**: Consider bid-ask spreads and liquidity when selecting contracts
5. **Tax Implications**: Consult with a tax advisor regarding options trading

## Troubleshooting

### Common Issues

1. **No Options Data**: Ensure your QuantConnect account has options data access
2. **No Contracts Found**: Adjust the delta range or expiration range
3. **Margin Errors**: Reduce position size or increase initial cash
4. **Greeks Not Available**: Some options may not have Greeks data

### Debug Mode

Enable detailed logging by setting:

```python
ENABLE_DETAILED_LOGGING = True
```

## Disclaimer

This strategy is for educational and backtesting purposes only. Options trading involves substantial risk and is not suitable for all investors. Past performance does not guarantee future results. Always consult with a financial advisor before implementing any trading strategy.

## References

- [QuantConnect Options API Documentation](https://www.quantconnect.com/learning/articles/introduction-to-options/quantconnect-options-api)
- [Options Backtesting Repository](https://github.com/RupertDodkins/options_backtest)
