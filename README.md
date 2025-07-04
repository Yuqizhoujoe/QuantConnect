# QuantConnet - Short Put Options Trading Strategy

A quantitative trading system built on QuantConnect's LEAN engine that implements a configurable short put options strategy. This project provides a modular, well-structured approach to options trading with comprehensive risk management and performance tracking.

## 🎯 Strategy Overview

The QuantConnet system implements a **short put options strategy** that:

- **Sells put options** on specified underlying securities (default: AVGO)
- **Targets specific delta ranges** (default: 0.30-0.50) for optimal risk/reward
- **Manages position sizing** based on portfolio value and margin requirements
- **Implements automatic rolling** before expiration to avoid assignment risk
- **Provides comprehensive backtesting** and performance analysis

### Key Features

- ✅ **Modular Architecture**: Separated concerns across multiple Python modules
- ✅ **Configuration-Driven**: Easy parameter tuning via JSON config files
- ✅ **Risk Management**: Built-in position sizing and margin controls
- ✅ **Performance Tracking**: Detailed trade logging and P&L analysis
- ✅ **Flexible Scheduling**: Support for monthly, weekly, or custom option frequencies
- ✅ **Backtesting Framework**: Comprehensive historical performance analysis

## 📁 Project Structure

```
quantconnet/
├── sell put option/           # Main strategy implementation
│   ├── main.py               # Entry point and algorithm orchestration
│   ├── config.json           # Strategy configuration parameters
│   ├── config_loader.py      # Configuration management
│   ├── data_handler.py       # Market data processing
│   ├── position_manager.py   # Position entry/exit logic
│   ├── trade_executor.py     # Order execution
│   ├── scheduler.py          # Event scheduling
│   ├── evaluator.py          # Performance evaluation
│   ├── backtests/            # Backtest results storage
│   └── research.ipynb        # Research and analysis notebook
├── data/                     # Market data storage
├── storage/                  # LEAN engine storage
├── backup/                   # Backup files
└── lean.json                 # LEAN engine configuration
```

## 🚀 Quick Start

### Prerequisites

1. **QuantConnect LEAN CLI** installed
2. **Python 3.8+** with required dependencies
3. **Market data access** (free tier available)

### Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd quantconnet
   ```

2. **Install LEAN CLI** (if not already installed):

   ```bash
   pip install lean-cli
   ```

3. **Login to QuantConnect**:
   ```bash
   lean login
   ```

### Configuration

1. **Edit strategy parameters** in `sell put option/config.json`:

   ```json
   {
     "parameters": {
       "ticker": "AVGO",
       "target_delta_min": 0.3,
       "target_delta_max": 0.5,
       "max_position_size": 0.2,
       "option_frequency": "monthly",
       "start_date": "2020-01-01",
       "end_date": "2025-01-01",
       "cash": 100000
     }
   }
   ```

2. **Configure LEAN settings** in `lean.json` (brokerage, data providers, etc.)

### Running the Strategy

#### Backtesting

```bash
lean backtest "sell put option" --output-dir backtests
```

#### Paper Trading

```bash
lean live "sell put option" --environment paper
```

#### Live Trading

```bash
lean live "sell put option" --environment live
```

## ⚙️ Configuration Parameters

### Strategy Parameters

| Parameter           | Default      | Description                             |
| ------------------- | ------------ | --------------------------------------- |
| `ticker`            | "AVGO"       | Underlying security symbol              |
| `target_delta_min`  | 0.30         | Minimum target delta for put options    |
| `target_delta_max`  | 0.50         | Maximum target delta for put options    |
| `max_position_size` | 0.20         | Maximum position size as % of portfolio |
| `option_frequency`  | "monthly"    | Option expiration frequency             |
| `start_date`        | "2020-01-01" | Backtest start date                     |
| `end_date`          | "2025-01-01" | Backtest end date                       |
| `cash`              | 100000       | Initial portfolio cash                  |

### Option Frequencies

- **`monthly`**: Third Friday of each month
- **`weekly`**: Every Friday
- **`any`**: No frequency filter

## 🏗️ Architecture

### Core Modules

#### `main.py` - Algorithm Orchestrator

- Initializes all components
- Sets up equity and option subscriptions
- Manages strategy state variables
- Delegates logic to specialized modules

#### `config_loader.py` - Configuration Management

- Loads parameters from JSON files
- Provides fallback to embedded configuration
- Applies settings to algorithm instance
- Supports both file-based and code-based configuration

#### `data_handler.py` - Market Data Processing

- Processes incoming market data slices
- Extracts option chain information
- Calculates option Greeks (delta, gamma, theta, vega)
- Maintains latest data state

#### `position_manager.py` - Position Logic

- Determines when to enter/exit positions
- Filters option contracts based on criteria
- Calculates optimal position sizes
- Manages rolling logic before expiration

#### `trade_executor.py` - Order Execution

- Executes buy/sell orders
- Manages order tracking
- Handles order fills and updates
- Implements risk controls

#### `scheduler.py` - Event Scheduling

- Sets up periodic evaluation events
- Manages trading schedule
- Coordinates position management calls

#### `evaluator.py` - Performance Analysis

- Tracks trade performance
- Calculates P&L metrics
- Generates performance reports
- Logs final results

## 📊 Strategy Logic

### Entry Criteria

1. **No existing position** in underlying or options
2. **Sufficient margin** available (>$10,000)
3. **No recent trades** on the same day
4. **Valid option contracts** available within delta range

### Position Selection

1. **Filter put options** by expiration frequency
2. **Target delta range** (default: 0.30-0.50)
3. **Expiry window** (30-60 days from current date)
4. **Select strike** closest to underlying price

### Exit Criteria

1. **Near expiration** (≤14 days to expiry)
2. **Automatic rolling** to avoid assignment risk
3. **Manual intervention** if needed

### Risk Management

- **Position sizing** based on portfolio value
- **Margin requirements** calculation
- **Maximum position size** limits
- **Automatic rolling** before expiration

## 📈 Performance Analysis

### Backtest Results

Backtest results are stored in `sell put option/backtests/` with timestamps:

- Performance metrics
- Trade logs
- Equity curves
- Risk statistics

### Key Metrics Tracked

- **Total Return**: Overall strategy performance
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Average Trade**: Mean P&L per trade

## 🔧 Customization

### Adding New Underlying Securities

1. Update `ticker` in `config.json`
2. Ensure data availability for the symbol
3. Adjust delta ranges if needed

### Modifying Strategy Parameters

1. Edit `config.json` for file-based configuration
2. Or modify `StrategyConfig` class in `config_loader.py`
3. Re-run backtests to validate changes

### Extending Functionality

- Add new modules following the existing pattern
- Implement additional risk management rules
- Create custom indicators or signals
- Add alternative exit strategies

## 🛠️ Development

### Adding New Features

1. **Create new module** following existing patterns
2. **Update main.py** to initialize new components
3. **Add configuration** parameters if needed
4. **Test thoroughly** with backtests

### Debugging

- Use `self.algorithm.Log()` for general logging
- Use `self.algorithm.Debug()` for detailed debugging
- Check backtest logs in output directory
- Review trade execution in real-time

### Best Practices

- **Modular design**: Keep concerns separated
- **Configuration-driven**: Avoid hardcoded values
- **Error handling**: Implement robust error handling
- **Documentation**: Comment complex logic
- **Testing**: Validate changes with backtests

## 📚 Resources

### QuantConnect Documentation

- [LEAN Engine Guide](https://www.quantconnect.com/docs/v2/lean-engine)
- [Algorithm Development](https://www.quantconnect.com/docs/v2/lean-engine/algorithm-development)
- [Options Trading](https://www.quantconnect.com/docs/v2/lean-engine/securities/asset-classes/equity-options)

### Strategy References

- [Short Put Options Strategy](https://www.investopedia.com/terms/s/short-put.asp)
- [Options Greeks](https://www.investopedia.com/terms/g/greeks.asp)
- [Risk Management](https://www.investopedia.com/terms/r/riskmanagement.asp)

## ⚠️ Risk Disclaimer

This software is for educational and research purposes only. Options trading involves substantial risk and is not suitable for all investors. Past performance does not guarantee future results. Always:

- **Understand the risks** before trading options
- **Start with paper trading** to test strategies
- **Use proper position sizing** and risk management
- **Consult with financial advisors** for personalized advice
- **Never risk more than you can afford to lose**

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests and documentation**
5. **Submit a pull request**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions or issues:

- Check the [QuantConnect Community](https://www.quantconnect.com/forum)
- Review the [LEAN Documentation](https://www.quantconnect.com/docs/v2/lean-engine)
- Open an issue in this repository

---

**Happy Trading! 📈**
