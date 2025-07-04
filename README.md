# QuantConnet - Enhanced Short Put Options Trading Strategy

A sophisticated quantitative trading system built on QuantConnect's LEAN engine that implements an advanced short put options strategy with comprehensive risk management, market analysis, and dynamic parameter adjustment. This project provides a modular, well-structured approach to options trading with intelligent risk controls and adaptive performance optimization.

## 🎯 Strategy Overview

The QuantConnet system implements an **enhanced short put options strategy** that:

- **Sells put options** on specified underlying securities (default: AVGO)
- **Uses dynamic delta ranges** that adapt to market conditions (0.20-0.60)
- **Implements Kelly Criterion position sizing** with volatility adjustments
- **Performs comprehensive market analysis** using technical indicators
- **Applies intelligent risk management** with circuit breakers and drawdown protection
- **Adapts trading parameters** based on market regimes (bullish/bearish, high/low volatility)
- **Provides real-time risk monitoring** and performance tracking
- **Implements automatic rolling** before expiration to avoid assignment risk

### Key Features

- ✅ **Advanced Risk Management**: Kelly Criterion position sizing, volatility adjustments, portfolio risk limits
- ✅ **Market Analysis Engine**: Technical indicators (RSI, moving averages), market regime detection, volatility analysis
- ✅ **Dynamic Parameter Adjustment**: Delta and DTE ranges that adapt to market conditions
- ✅ **Intelligent Contract Selection**: Multi-criteria scoring system for optimal option selection
- ✅ **Real-time Risk Monitoring**: Drawdown tracking, win rate analysis, volatility factor monitoring
- ✅ **Circuit Breakers**: Automatic trading stops for extreme market conditions
- ✅ **Modular Architecture**: Separated concerns across multiple Python modules
- ✅ **Configuration-Driven**: Easy parameter tuning via JSON config files
- ✅ **Performance Analytics**: Comprehensive metrics including Sharpe ratio, profit factor, and risk-adjusted returns
- ✅ **Flexible Scheduling**: Support for monthly, weekly, or custom option frequencies
- ✅ **Backtesting Framework**: Comprehensive historical performance analysis

## 📁 Project Structure

```
quantconnet/
├── sell put option/           # Main strategy implementation
│   ├── main.py               # Entry point and algorithm orchestration
│   ├── config.json           # Strategy configuration parameters
│   ├── config_loader.py      # Configuration management
│   ├── data_handler.py       # Market data processing and risk monitoring
│   ├── position_manager.py   # Enhanced position logic with market analysis
│   ├── trade_executor.py     # Order execution
│   ├── scheduler.py          # Event scheduling
│   ├── evaluator.py          # Enhanced performance evaluation
│   ├── risk_manager.py       # Advanced risk management and position sizing
│   ├── market_analyzer.py    # Market analysis and technical indicators
│   ├── IMPROVEMENTS_GUIDE.md # Comprehensive improvements documentation
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
       "target_delta_min": 0.2,
       "target_delta_max": 0.6,
       "max_position_size": 0.2,
       "option_frequency": "monthly",
       "start_date": "2020-01-01",
       "end_date": "2025-01-01",
       "cash": 100000,
       "risk_management": {
         "max_portfolio_risk": 0.02,
         "max_drawdown": 0.15,
         "volatility_lookback": 20,
         "volatility_threshold": 0.4
       },
       "market_analysis": {
         "rsi_period": 14,
         "moving_average_period": 50,
         "volatility_lookback": 20
       }
     }
   }
   ```

2. **Configure LEAN settings** in `lean.json` (brokerage, data providers, etc.)

### Running the Strategy

#### Backtesting

```bash
# Standard configuration with plotting
lean backtest "sell put option" --output-dir backtests

# Minimal configuration without plotting (avoids charting limits)
lean backtest "sell put option" --config config_minimal.json --output-dir backtests
```

#### Paper Trading

```bash
lean live "sell put option" --environment paper
```

#### Live Trading

```bash
lean live "sell put option" --environment live
```

**Note:** If you encounter charting limit warnings, use `config_minimal.json` or disable plotting in your configuration.

## ⚙️ Configuration Parameters

### Strategy Parameters

| Parameter           | Default      | Description                             |
| ------------------- | ------------ | --------------------------------------- |
| `ticker`            | "AVGO"       | Underlying security symbol              |
| `target_delta_min`  | 0.20         | Minimum target delta for put options    |
| `target_delta_max`  | 0.60         | Maximum target delta for put options    |
| `max_position_size` | 0.20         | Maximum position size as % of portfolio |
| `option_frequency`  | "monthly"    | Option expiration frequency             |
| `start_date`        | "2020-01-01" | Backtest start date                     |
| `end_date`          | "2025-01-01" | Backtest end date                       |
| `cash`              | 100000       | Initial portfolio cash                  |

### Risk Management Parameters

| Parameter              | Default | Description                             |
| ---------------------- | ------- | --------------------------------------- |
| `max_portfolio_risk`   | 0.02    | Maximum 2% portfolio risk per trade     |
| `max_drawdown`         | 0.15    | Maximum 15% drawdown before stopping    |
| `volatility_lookback`  | 20      | Days for volatility calculation         |
| `volatility_threshold` | 0.4     | Threshold for high volatility detection |

### Market Analysis Parameters

| Parameter               | Default | Description                  |
| ----------------------- | ------- | ---------------------------- |
| `rsi_period`            | 14      | Period for RSI calculation   |
| `moving_average_period` | 50      | Period for trend analysis    |
| `volatility_lookback`   | 20      | Days for volatility analysis |

### Plotting Parameters

| Parameter           | Default | Description                                |
| ------------------- | ------- | ------------------------------------------ |
| `enabled`           | true    | Enable/disable all plotting                |
| `plot_frequency`    | 50      | Plot every N data points to respect limits |
| `max_plot_points`   | 3500    | Maximum data points per chart series       |
| `plot_risk_metrics` | true    | Enable risk metrics plotting               |
| `plot_pnl`          | true    | Enable P&L plotting                        |

### Option Frequencies

- **`monthly`**: Third Friday of each month
- **`weekly`**: Every Friday
- **`any`**: No frequency filter

## 🏗️ Architecture

### Core Modules

#### `main.py` - Algorithm Orchestrator

- Initializes all components including risk and market analysis modules
- Sets up equity and option subscriptions
- Manages strategy state variables and peak portfolio tracking
- Delegates logic to specialized modules
- Integrates risk management and market analysis

#### `config_loader.py` - Configuration Management

- Loads parameters from JSON files with enhanced risk and market analysis settings
- Provides fallback to embedded configuration
- Applies settings to algorithm instance
- Supports both file-based and code-based configuration

#### `data_handler.py` - Enhanced Market Data Processing

- Processes incoming market data slices
- Extracts option chain information
- Calculates option Greeks (delta, gamma, theta, vega)
- Maintains latest data state
- **NEW**: Tracks portfolio performance metrics and drawdown
- **NEW**: Provides real-time risk monitoring and visualization

#### `position_manager.py` - Enhanced Position Logic

- **NEW**: Integrates risk management and market analysis
- **NEW**: Implements multi-criteria contract selection
- **NEW**: Applies dynamic parameter adjustment based on market conditions
- Determines when to enter/exit positions with enhanced filtering
- Filters option contracts based on multiple criteria
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

#### `evaluator.py` - Enhanced Performance Analysis

- **NEW**: Calculates risk-adjusted returns (Sharpe ratio, profit factor)
- **NEW**: Analyzes trade patterns and durations
- **NEW**: Provides comprehensive performance statistics
- Tracks trade performance
- Generates detailed performance reports
- Logs final results with enhanced metrics

### New Enhanced Modules

#### `risk_manager.py` - Advanced Risk Management

- **Kelly Criterion position sizing** for optimal returns
- **Dynamic volatility adjustments** based on market conditions
- **Portfolio risk limits** (2% max per trade)
- **Drawdown protection** (15% max before stopping)
- **Consecutive loss monitoring** and circuit breakers
- **Historical performance analysis** for position sizing

#### `market_analyzer.py` - Market Analysis Engine

- **Technical indicators**: RSI, moving averages, volatility analysis
- **Market regime detection**: bullish/bearish, high/low volatility
- **Support and resistance levels** identification
- **Option premium analysis** using implied volatility
- **Dynamic parameter recommendations** based on market conditions
- **Trading filters** to avoid unfavorable conditions

## 📊 Enhanced Strategy Logic

### Entry Criteria

1. **No existing position** in underlying or options
2. **Sufficient margin** available (>$10,000)
3. **No recent trades** on the same day
4. **Risk management validation** (drawdown, consecutive losses)
5. **Market condition analysis** (avoid unfavorable regimes)
6. **Valid option contracts** available within dynamic delta range

### Position Selection

1. **Market analysis** to determine optimal parameters
2. **Dynamic delta range** based on market regime (0.20-0.60)
3. **Dynamic DTE range** based on volatility conditions (21-90 days)
4. **Multi-criteria contract scoring**:
   - Strike proximity to current price (40% weight)
   - Delta alignment with target range (40% weight)
   - Days to expiration optimization (20% weight)
   - Market regime adjustments

### Exit Criteria

1. **Near expiration** (≤14 days to expiry)
2. **Automatic rolling** to avoid assignment risk
3. **Risk management triggers** (drawdown limits, consecutive losses)
4. **Market condition changes** (extreme volatility, regime shifts)

### Advanced Risk Management

- **Kelly Criterion position sizing** for optimal returns
- **Dynamic volatility adjustments** (reduce size in high volatility)
- **Portfolio risk limits** (2% max per trade)
- **Drawdown protection** (15% max before stopping)
- **Circuit breakers** (stop after 3 consecutive losses)
- **Real-time risk monitoring** and visualization

### Market Analysis Integration

- **Technical indicators**: RSI, moving averages, volatility analysis
- **Market regime detection**: bullish/bearish, high/low volatility
- **Trading filters**: avoid overbought/oversold conditions
- **Dynamic parameter adjustment**: adapt to market conditions

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
- **Profit Factor**: Ratio of average win to average loss
- **Volatility Factor**: Market volatility adjustment factor
- **Kelly Criterion**: Optimal position sizing percentage
- **Market Regime Performance**: Returns by market condition
- **Risk-Adjusted Metrics**: Comprehensive risk analysis

## 🔧 Customization

### Adding New Underlying Securities

1. Update `ticker` in `config.json`
2. Ensure data availability for the symbol
3. Adjust delta ranges if needed
4. Consider market characteristics for risk parameters

### Modifying Strategy Parameters

1. Edit `config.json` for file-based configuration
2. Adjust risk management parameters based on risk tolerance
3. Fine-tune market analysis parameters for different securities
4. Configure plotting settings to respect QuantConnect limits
5. Re-run backtests to validate changes

### Plotting Configuration

The strategy includes intelligent plotting controls to respect QuantConnect's charting limits (4000 points per series):

**To avoid charting limit warnings:**

- Use `config_minimal.json` (plotting disabled)
- Or set `"enabled": false` in the plotting section
- Or increase `plot_frequency` to reduce data points

**To enable selective plotting:**

- Set `plot_risk_metrics: false` to disable risk charts
- Set `plot_pnl: false` to disable P&L charts
- Adjust `plot_frequency` to control update rate

### Risk Management Customization

1. **Adjust portfolio risk limits**: Modify `max_portfolio_risk` (default: 2%)
2. **Change drawdown protection**: Modify `max_drawdown` (default: 15%)
3. **Volatility sensitivity**: Adjust `volatility_threshold` (default: 0.4)
4. **Kelly Criterion limits**: Modify position sizing bounds in `risk_manager.py`

### Market Analysis Customization

1. **Technical indicators**: Adjust periods in `market_analyzer.py`
2. **Market regime thresholds**: Modify regime detection logic
3. **Trading filters**: Customize conditions for avoiding trades
4. **Dynamic parameters**: Adjust delta and DTE ranges for different conditions

### Extending Functionality

- Add new technical indicators to `market_analyzer.py`
- Implement additional risk management rules in `risk_manager.py`
- Create custom market regime classifications
- Add alternative exit strategies based on market conditions
- Implement hedging strategies for extreme market conditions

## 🛠️ Development

### Adding New Features

1. **Create new module** following existing patterns
2. **Update main.py** to initialize new components
3. **Add configuration** parameters if needed
4. **Test thoroughly** with backtests
5. **Validate risk management** integration
6. **Check market analysis** compatibility

### Debugging

- Use `self.algorithm.Log()` for general logging
- Use `self.algorithm.Debug()` for detailed debugging
- Check backtest logs in output directory
- Review trade execution in real-time
- Monitor risk metrics and market analysis outputs
- Use the enhanced performance evaluation for detailed analysis

### Best Practices

- **Modular design**: Keep concerns separated across risk, market analysis, and execution
- **Configuration-driven**: Avoid hardcoded values, especially for risk parameters
- **Error handling**: Implement robust error handling with circuit breakers
- **Documentation**: Comment complex logic, especially risk management formulas
- **Testing**: Validate changes with backtests and risk scenario analysis
- **Risk-first approach**: Always consider risk implications of new features
- **Market adaptation**: Ensure new features work across different market regimes

## 📚 Resources

### QuantConnect Documentation

- [LEAN Engine Guide](https://www.quantconnect.com/docs/v2/lean-engine)
- [Algorithm Development](https://www.quantconnect.com/docs/v2/lean-engine/algorithm-development)
- [Options Trading](https://www.quantconnect.com/docs/v2/lean-engine/securities/asset-classes/equity-options)

### Strategy References

- [Short Put Options Strategy](https://www.investopedia.com/terms/s/short-put.asp)
- [Options Greeks](https://www.investopedia.com/terms/g/greeks.asp)
- [Risk Management](https://www.investopedia.com/terms/r/riskmanagement.asp)
- [Kelly Criterion](https://www.investopedia.com/terms/k/kellycriterion.asp)
- [Technical Analysis](https://www.investopedia.com/terms/t/technicalanalysis.asp)
- [Market Regime Analysis](https://www.investopedia.com/terms/m/marketregime.asp)

## ⚠️ Risk Disclaimer

This software is for educational and research purposes only. Options trading involves substantial risk and is not suitable for all investors. The enhanced risk management features do not eliminate the inherent risks of options trading. Past performance does not guarantee future results. Always:

- **Understand the risks** before trading options
- **Start with paper trading** to test strategies
- **Use proper position sizing** and risk management
- **Monitor risk metrics** and adjust parameters as needed
- **Understand Kelly Criterion** and volatility adjustments
- **Consult with financial advisors** for personalized advice
- **Never risk more than you can afford to lose**
- **Test thoroughly** across different market conditions

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests and documentation**
5. **Validate risk management integration**
6. **Test across different market conditions**
7. **Submit a pull request**

### Contribution Guidelines

- **Risk-first approach**: All new features must consider risk implications
- **Market analysis integration**: New features should work with market analysis
- **Comprehensive testing**: Test across different market regimes
- **Documentation**: Update both code comments and README
- **Performance validation**: Ensure new features improve or maintain performance

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔧 Troubleshooting

### Charting Limit Warnings

If you see warnings like "Exceeded maximum data points per series":

**Solution 1: Use minimal configuration**

```bash
lean backtest "sell put option" --config config_minimal.json --output-dir backtests
```

**Solution 2: Disable plotting in config.json**

```json
"plotting": {
    "enabled": false
}
```

**Solution 3: Increase plot frequency**

```json
"plotting": {
    "plot_frequency": 100
}
```

### Performance Issues

- **High memory usage**: Reduce `volatility_lookback` and `moving_average_period`
- **Slow execution**: Disable plotting or increase `plot_frequency`
- **Risk metrics errors**: Check if sufficient trade history exists

### Configuration Issues

- **JSON parsing errors**: Validate your config.json syntax
- **Missing parameters**: Use embedded configuration as fallback
- **Invalid dates**: Ensure dates are in YYYY-MM-DD format

## 📞 Support

For questions or issues:

- Check the [QuantConnect Community](https://www.quantconnect.com/forum)
- Review the [LEAN Documentation](https://www.quantconnect.com/docs/v2/lean-engine)
- Open an issue in this repository

## 🚀 What's New in This Version

### Major Enhancements

- **🛡️ Advanced Risk Management**: Kelly Criterion position sizing, volatility adjustments, portfolio risk limits
- **📊 Market Analysis Engine**: Technical indicators, market regime detection, dynamic parameter adjustment
- **🎛️ Intelligent Contract Selection**: Multi-criteria scoring system for optimal option selection
- **📈 Enhanced Performance Tracking**: Real-time risk monitoring, comprehensive metrics, drawdown protection
- **⚙️ Dynamic Configuration**: Risk management and market analysis parameters

### Performance Improvements

- **Better Risk Control**: Reduced drawdowns and more consistent performance
- **Adaptive Trading**: Strategy adjusts to changing market conditions
- **Improved Returns**: Better option selection and timing
- **Enhanced Monitoring**: Real-time risk metrics and performance tracking

### Technical Features

- **Kelly Criterion**: Optimal position sizing based on historical performance
- **Volatility Analysis**: Dynamic position size adjustments
- **Market Regime Detection**: Bullish/bearish, high/low volatility classification
- **Technical Indicators**: RSI, moving averages, volatility analysis
- **Circuit Breakers**: Automatic trading stops for extreme conditions

---

**Happy Trading! 📈**
