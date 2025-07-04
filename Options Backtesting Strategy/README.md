# Options Backtesting Strategy - LEAN Project

This LEAN project contains a comprehensive options backtesting strategy for QuantConnect, specifically designed for short put strategies.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- QuantConnect account with options data access
- LEAN CLI installed

### Installation

1. **Install LEAN CLI** (if not already installed):

   ```bash
   pip install lean
   ```

2. **Initialize LEAN** (if not already done):

   ```bash
   lean init
   ```

3. **Install project dependencies**:
   ```bash
   cd "Options Backtesting Strategy"
   pip install -r requirements.txt
   ```

## 📁 Project Structure

```
Options Backtesting Strategy/
├── main.py                 # Main algorithm file
├── enhanced_broadcom_strategy.py  # Enhanced strategy implementation
├── strategy_config.py      # Configuration parameters
├── requirements.txt        # Python dependencies
├── setup.py               # Package setup
├── config.json            # LEAN project configuration
├── research.ipynb         # Research notebook
└── README.md              # This file
```

## 🎯 Strategy Overview

The strategy implements a **short put options strategy** with the following characteristics:

- **Target Delta Range**: 0.44-0.50 (slightly OTM puts)
- **Expiration Range**: 20-60 days
- **Position Sizing**: 5% of portfolio per trade
- **Risk Management**: Profit targets and stop losses
- **Market Filters**: Optional volatility and price range filters

## 🏃‍♂️ Running the Strategy

### Local Backtest

```bash
# From the project root directory
lean backtest "Options Backtesting Strategy"
```

### Cloud Backtest

```bash
# Push to cloud and run
lean cloud push "Options Backtesting Strategy"
lean cloud backtest "Options Backtesting Strategy"
```

### Live Trading

```bash
# Deploy to live trading
lean cloud live "Options Backtesting Strategy"
```

## ⚙️ Configuration

### Basic Parameters (in main.py)

```python
self.config.START_DATE = (2020, 1, 1)
self.config.END_DATE = (2024, 12, 31)
self.config.INITIAL_CASH = 100000
self.config.TICKER = "AVGO"  # Change to any stock
```

### Strategy Parameters

```python
self.config.MAX_POSITION_SIZE = 0.05  # 5% per trade
self.config.TARGET_DELTA_MIN = 0.44
self.config.TARGET_DELTA_MAX = 0.50
self.config.MIN_DAYS_TO_EXPIRY = 20
self.config.MAX_DAYS_TO_EXPIRY = 60
```

### Risk Management

```python
self.config.PROFIT_TARGET_PCT = 0.50  # Close at 50% profit
self.config.STOP_LOSS_MULTIPLIER = 2.0  # Stop loss at 2x max profit
self.config.MIN_DAYS_BEFORE_EXPIRY = 5  # Close 5 days before expiry
```

## 🔧 Customization

### Changing the Underlying Stock

Modify the `TICKER` parameter in `main.py`:

```python
self.config.TICKER = "AAPL"  # For Apple
self.config.TICKER = "TSLA"  # For Tesla
self.config.TICKER = "SPY"   # For SPDR S&P 500 ETF
```

### Adjusting Risk Parameters

```python
# More conservative
self.config.MAX_POSITION_SIZE = 0.03  # 3% per trade
self.config.STOP_LOSS_MULTIPLIER = 1.5  # Tighter stop loss

# More aggressive
self.config.MAX_POSITION_SIZE = 0.10  # 10% per trade
self.config.STOP_LOSS_MULTIPLIER = 3.0  # Wider stop loss
```

### Modifying Delta Range

```python
# More OTM (lower probability of profit)
self.config.TARGET_DELTA_MIN = 0.30
self.config.TARGET_DELTA_MAX = 0.40

# More ATM (higher probability of profit)
self.config.TARGET_DELTA_MIN = 0.45
self.config.TARGET_DELTA_MAX = 0.55
```

## 📊 Performance Metrics

The strategy tracks and reports:

- Total number of trades
- Win rate
- Average win/loss
- Total P&L
- Maximum drawdown
- Total return

## 🛡️ Risk Management Features

1. **Position Sizing**: Limits exposure per trade
2. **Profit Targets**: Takes profits at predetermined levels
3. **Stop Losses**: Limits downside risk
4. **Expiration Management**: Avoids holding to expiration
5. **Margin Monitoring**: Ensures sufficient margin for new positions
6. **Market Filters**: Optional filters for volatility and price ranges

## 🔍 Research and Development

### Using the Research Notebook

```bash
# Open the research notebook
jupyter notebook research.ipynb
```

### Adding Custom Analysis

Create new analysis in the research notebook:

```python
# Example: Analyze strategy performance
from enhanced_broadcom_strategy import EnhancedBroadcomShortPutStrategy
import pandas as pd

# Load backtest results
results = pd.read_csv('backtest_results.csv')
print(results.head())
```

## 🚨 Important Notes

### Data Requirements

- **Options Data**: Ensure your QuantConnect account has access to options data
- **Historical Data**: The strategy requires historical options data for backtesting
- **Real-time Data**: For live trading, ensure real-time data feeds are available

### Risk Warnings

- **Options Trading**: Involves substantial risk and is not suitable for all investors
- **Leverage**: Options provide leverage which can amplify both gains and losses
- **Complexity**: Options strategies are complex and require understanding of options mechanics
- **Past Performance**: Does not guarantee future results

### Technical Considerations

- **Margin Requirements**: The strategy includes simplified margin calculations
- **Greeks Data**: Strategy relies on option Greeks (Delta) for contract selection
- **Liquidity**: Consider bid-ask spreads and liquidity when selecting contracts
- **Execution**: Market orders may not fill at expected prices

## 🐛 Troubleshooting

### Common Issues

1. **No Options Data Available**

   - Ensure your QuantConnect account has options data access
   - Check if the ticker has options available
   - Verify the date range has options data

2. **No Contracts Found**

   - Adjust the delta range in configuration
   - Modify the expiration range
   - Check if the underlying stock has options

3. **Margin Errors**

   - Reduce position size in configuration
   - Increase initial cash amount
   - Check margin requirements for the specific options

4. **Greeks Not Available**
   - Some options may not have Greeks data
   - Check if the options have sufficient liquidity
   - Verify the options data feed

### Debug Mode

Enable detailed logging by setting:

```python
self.config.ENABLE_DETAILED_LOGGING = True
```

## 📚 Additional Resources

- [QuantConnect Documentation](https://www.quantconnect.com/docs/)
- [LEAN CLI Documentation](https://www.lean.io/docs/v2/lean-cli/)
- [Options Trading Guide](https://www.quantconnect.com/learning/articles/introduction-to-options/)
- [QuantConnect Community](https://www.quantconnect.com/forum/)

## 📄 License

This project is for educational and backtesting purposes only. Please consult with a financial advisor before implementing any trading strategy.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review QuantConnect documentation
3. Post questions in the QuantConnect community forum
4. Create an issue in this repository

---

**Disclaimer**: This strategy is for educational and backtesting purposes only. Options trading involves substantial risk and is not suitable for all investors. Past performance does not guarantee future results. Always consult with a financial advisor before implementing any trading strategy.
