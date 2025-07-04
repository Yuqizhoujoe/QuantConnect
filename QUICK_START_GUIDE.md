# 🚀 QuantConnect CLI & Options Backtesting - Quick Start Guide

This guide will walk you through setting up and using the QuantConnect CLI (LEAN) with our comprehensive options backtesting strategy.

## 📋 Prerequisites

- **Python 3.8+** installed
- **QuantConnect account** with options data access
- **Basic understanding** of options trading concepts

## 🛠️ Installation & Setup

### Step 1: Install QuantConnect CLI (LEAN)

```bash
# Install LEAN CLI
pip install lean

# Verify installation
lean --version
```

### Step 2: Initialize LEAN Environment

```bash
# Initialize LEAN in your project directory
lean init

# This will:
# - Create lean.json configuration file
# - Download sample data
# - Set up data directory
# - Ask for your QuantConnect credentials
```

### Step 3: Set Up the Options Backtesting Project

```bash
# Create the project
lean create-project "Options Backtesting Strategy"

# Copy our strategy files (already done in this setup)
# The project is now ready to use!
```

## 🎯 Project Structure

```
quantconnet/
├── lean.json                           # LEAN configuration
├── data/                               # Market data directory
├── setup_project.sh                    # Quick setup script
├── QUICK_START_GUIDE.md               # This file
└── Options Backtesting Strategy/       # Main project directory
    ├── main.py                         # Main algorithm
    ├── enhanced_broadcom_strategy.py   # Strategy implementation
    ├── strategy_config.py              # Configuration parameters
    ├── requirements.txt                # Python dependencies
    ├── manage.py                       # Management script
    ├── setup.py                        # Package setup
    ├── config.json                     # Project configuration
    ├── research.ipynb                  # Research notebook
    └── README.md                       # Project documentation
```

## 🏃‍♂️ Quick Start Commands

### Option 1: Automated Setup (Recommended)

```bash
# Run the automated setup script
./setup_project.sh
```

This script will:

- ✅ Check prerequisites
- ✅ Install dependencies
- ✅ Validate project structure
- ✅ Show project information
- ✅ Offer to run a backtest

### Option 2: Manual Setup

```bash
# Navigate to project directory
cd "Options Backtesting Strategy"

# Install dependencies
pip install -r requirements.txt

# Validate project
python manage.py validate

# Show project info
python manage.py info
```

## 🎮 Using the Management Script

The `manage.py` script provides convenient commands for common tasks:

```bash
# Show project information
python manage.py info

# Validate project structure
python manage.py validate

# Run local backtest
python manage.py backtest

# Run cloud backtest
python manage.py cloud-backtest

# Sync with QuantConnect cloud
python manage.py sync

# Create a new strategy variant
python manage.py create-variant --name "Apple Strategy" --ticker AAPL
```

## 📊 Running Backtests

### Local Backtest

```bash
# From project root
lean backtest "Options Backtesting Strategy"

# Or using management script
cd "Options Backtesting Strategy"
python manage.py backtest
```

### Cloud Backtest

```bash
# Push to cloud and run backtest
lean cloud push "Options Backtesting Strategy"
lean cloud backtest "Options Backtesting Strategy"

# Or using management script
python manage.py cloud-backtest
```

### Live Trading

```bash
# Deploy to live trading (use with caution!)
lean cloud live "Options Backtesting Strategy"
```

## ⚙️ Configuration

### Basic Configuration (main.py)

```python
# Modify these parameters in main.py
self.config.START_DATE = (2020, 1, 1)      # Backtest start date
self.config.END_DATE = (2024, 12, 31)      # Backtest end date
self.config.INITIAL_CASH = 100000          # Starting capital
self.config.TICKER = "AVGO"                # Underlying stock
```

### Strategy Parameters

```python
# Risk management
self.config.MAX_POSITION_SIZE = 0.05       # 5% per trade
self.config.TARGET_DELTA_MIN = 0.44        # Minimum delta
self.config.TARGET_DELTA_MAX = 0.50        # Maximum delta
self.config.MIN_DAYS_TO_EXPIRY = 20        # Min days to expiration
self.config.MAX_DAYS_TO_EXPIRY = 60        # Max days to expiration

# Exit conditions
self.config.PROFIT_TARGET_PCT = 0.50       # Take profit at 50%
self.config.STOP_LOSS_MULTIPLIER = 2.0     # Stop loss at 2x max profit
```

## 🔧 Customization Examples

### Change Underlying Stock

```python
# In main.py, change the TICKER
self.config.TICKER = "AAPL"    # Apple
self.config.TICKER = "TSLA"    # Tesla
self.config.TICKER = "SPY"     # S&P 500 ETF
```

### Adjust Risk Parameters

```python
# More conservative
self.config.MAX_POSITION_SIZE = 0.03       # 3% per trade
self.config.STOP_LOSS_MULTIPLIER = 1.5     # Tighter stop loss

# More aggressive
self.config.MAX_POSITION_SIZE = 0.10       # 10% per trade
self.config.STOP_LOSS_MULTIPLIER = 3.0     # Wider stop loss
```

### Create Strategy Variants

```bash
# Create Apple strategy
python manage.py create-variant --name "Apple Strategy" --ticker AAPL

# Create Tesla strategy with different delta
python manage.py create-variant --name "Tesla Strategy" --ticker TSLA --delta-min 0.35 --delta-max 0.45
```

## 📈 Understanding the Strategy

### What It Does

- **Sells put options** on the underlying stock
- **Targets delta range** of 0.44-0.50 (slightly OTM)
- **Manages risk** with position sizing and stop losses
- **Takes profits** at 50% of maximum profit
- **Avoids expiration** by closing 5 days before expiry

### Key Features

- ✅ **Risk Management**: Position sizing, stop losses, profit targets
- ✅ **Market Filters**: Optional volatility and price range filters
- ✅ **Performance Tracking**: Detailed metrics and trade logging
- ✅ **Flexible Configuration**: Easy parameter modification
- ✅ **Multiple Assets**: Works with any stock that has options

## 🚨 Important Notes

### Data Requirements

- **Options Data**: Your QuantConnect account must have options data access
- **Historical Data**: Required for backtesting
- **Real-time Data**: Required for live trading

### Risk Warnings

- ⚠️ **Options Trading**: Involves substantial risk
- ⚠️ **Leverage**: Can amplify both gains and losses
- ⚠️ **Complexity**: Requires understanding of options mechanics
- ⚠️ **Past Performance**: Does not guarantee future results

### Technical Considerations

- **Margin Requirements**: Strategy includes simplified calculations
- **Greeks Data**: Relies on option Greeks for contract selection
- **Liquidity**: Consider bid-ask spreads when selecting contracts
- **Execution**: Market orders may not fill at expected prices

## 🐛 Troubleshooting

### Common Issues

1. **"No Options Data Available"**

   ```bash
   # Check your QuantConnect account has options data access
   # Verify the ticker has options available
   # Check the date range has options data
   ```

2. **"No Contracts Found"**

   ```python
   # Adjust delta range in main.py
   self.config.TARGET_DELTA_MIN = 0.30
   self.config.TARGET_DELTA_MAX = 0.60

   # Or modify expiration range
   self.config.MIN_DAYS_TO_EXPIRY = 10
   self.config.MAX_DAYS_TO_EXPIRY = 90
   ```

3. **"Margin Errors"**

   ```python
   # Reduce position size
   self.config.MAX_POSITION_SIZE = 0.03

   # Or increase initial cash
   self.config.INITIAL_CASH = 200000
   ```

4. **"Greeks Not Available"**
   ```python
   # Some options may not have Greeks data
   # Check if options have sufficient liquidity
   # Verify the options data feed
   ```

### Debug Mode

Enable detailed logging:

```python
self.config.ENABLE_DETAILED_LOGGING = True
```

## 📚 Additional Resources

- [QuantConnect Documentation](https://www.quantconnect.com/docs/)
- [LEAN CLI Documentation](https://www.lean.io/docs/v2/lean-cli/)
- [Options Trading Guide](https://www.quantconnect.com/learning/articles/introduction-to-options/)
- [QuantConnect Community](https://www.quantconnect.com/forum/)

## 🎯 Next Steps

1. **Run a backtest** to see the strategy in action
2. **Modify parameters** to suit your risk tolerance
3. **Test different stocks** to find the best opportunities
4. **Analyze results** using the research notebook
5. **Consider live trading** (with proper risk management)

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review QuantConnect documentation
3. Post questions in the QuantConnect community forum
4. Create an issue in this repository

---

**Disclaimer**: This strategy is for educational and backtesting purposes only. Options trading involves substantial risk and is not suitable for all investors. Past performance does not guarantee future results. Always consult with a financial advisor before implementing any trading strategy.

**Happy Backtesting! 🎉**
