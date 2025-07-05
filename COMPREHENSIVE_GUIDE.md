# 🚀 Comprehensive Guide: Advanced Short Put Option Strategy

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture & Components](#architecture--components)
3. [Quick Start Guide](#quick-start-guide)
4. [Configuration](#configuration)
5. [Core Strategy Logic](#core-strategy-logic)
6. [Risk Management](#risk-management)
7. [Market Analysis](#market-analysis)
8. [Multi-Stock Portfolio Management](#multi-stock-portfolio-management)
9. [Performance Monitoring](#performance-monitoring)
10. [Troubleshooting](#troubleshooting)
11. [Advanced Features](#advanced-features)

---

## 🎯 System Overview

This is a sophisticated short put option strategy that has evolved from a basic single-stock system to a comprehensive multi-stock portfolio management platform. The system combines advanced risk management, market analysis, and intelligent trade selection to optimize returns while maintaining strict risk controls.

### Key Features

- **Single & Multi-Stock Support**: Trade one stock or multiple stocks simultaneously with portfolio-level coordination
- **Advanced Risk Management**: Kelly Criterion, volatility adjustments, and portfolio protection
- **Market Analysis**: Technical indicators, regime detection, and dynamic parameter adjustment
- **Smart Trade Selection**: Multi-criteria contract selection and optimal timing
- **Real-time Monitoring**: Comprehensive performance tracking and risk metrics
- **Flexible Configuration**: Easy parameter tuning without code changes
- **CLI Interface**: Command-line tools for easy strategy execution

---

## 🏗️ Architecture & Components

### Project Structure

```
quantconnet/
├── config/                           # Configuration files
│   ├── sell_put.json                 # Single stock config
│   ├── sell_put_multi_stock.json     # Multi-stock config
│   ├── sell_put_backup.json          # Backup config
│   ├── __init__.py
│   └── common_config_loader.py       # Config loading utilities
├── core/                            # Shared across all strategies
│   ├── __init__.py
│   ├── data_handler.py              # Data processing & plotting
│   ├── market_analyzer.py           # Technical analysis
│   ├── risk_manager.py              # Risk management
│   ├── correlation_manager.py       # Portfolio correlation
│   └── scheduler.py                 # Event scheduling
├── strategies/
│   ├── __init__.py
│   ├── sell_put/                    # Sell Put Strategy
│   │   ├── __init__.py
│   │   ├── main.py                  # Single stock strategy
│   │   ├── main_multi_stock.py      # Multi-stock strategy
│   │   ├── portfolio_manager.py     # Portfolio coordination
│   │   ├── position_manager.py      # Trade decision logic
│   │   ├── stock_manager.py         # Individual stock management
│   │   ├── trade_executor.py        # Trade execution
│   │   └── evaluator.py             # Performance evaluation
│   └── covered_call/                # Future: Covered Call Strategy
├── cli/
│   └── run_strategy.py              # CLI entry point
├── tests/                           # Test suite
└── research/                        # Research notebooks
```

### Core Files

| File                      | Purpose                           | Key Features                                 |
| ------------------------- | --------------------------------- | -------------------------------------------- |
| `main.py`                 | Single-stock strategy entry point | Basic short put implementation               |
| `main_multi_stock.py`     | Multi-stock strategy entry point  | Portfolio-level coordination                 |
| `portfolio_manager.py`    | Portfolio coordination            | Multi-stock management, correlation analysis |
| `stock_manager.py`        | Individual stock management       | Per-stock trade logic and risk controls      |
| `position_manager.py`     | Trade decision logic              | Contract selection, entry/exit criteria      |
| `risk_manager.py`         | Risk management                   | Kelly Criterion, volatility adjustments      |
| `market_analyzer.py`      | Market analysis                   | Technical indicators, regime detection       |
| `data_handler.py`         | Data management                   | Performance tracking, metrics calculation    |
| `common_config_loader.py` | Configuration management          | Parameter loading and validation             |
| `evaluator.py`            | Performance evaluation            | Statistics, reporting, analysis              |
| `run_strategy.py`         | CLI interface                     | Command-line strategy execution              |

### System Flow - How the Code Actually Works

#### 1. **Initialization Phase** (When strategy starts)

```
main.py/main_multi_stock.py
    ↓
common_config_loader.py → Loads config.json/config_multi_stock.json
    ↓
portfolio_manager.py → Creates stock_manager for each stock
    ↓
scheduler.py → Sets up daily/weekly trading events
```

#### 2. **Daily Trading Cycle** (What happens every day)

```
OnData() event (new market data arrives)
    ↓
portfolio_manager.update_portfolio_data()
    ↓
For each stock:
    stock_manager.manage_positions()
        ↓
    position_manager.should_enter_trade()
        ↓
    market_analyzer.analyze_market() → Check RSI, volatility, trend
        ↓
    risk_manager.calculate_position_size() → Kelly Criterion + volatility
        ↓
    position_manager.select_best_contract() → Score options by strike/delta/DTE
        ↓
    If trade conditions met:
        trade_executor.execute_trade()
        data_handler.record_trade()
```

#### 3. **Trade Decision Logic** (The decision tree)

```
Is it time to trade? (scheduler check)
    ↓
Do we have market data? (data availability)
    ↓
Are market conditions favorable? (market_analyzer)
    ↓
Is risk within limits? (risk_manager)
    ↓
Can we find a good contract? (position_manager)
    ↓
EXECUTE TRADE or SKIP
```

#### 4. **Contract Selection Process** (How options are chosen)

```
Get all available put options
    ↓
Filter by delta range (e.g., 0.25-0.75)
    ↓
Filter by DTE range (14-45 days)
    ↓
Score each contract:
    - Strike score: How close to current price
    - Delta score: How close to target delta
    - DTE score: How close to optimal days
    ↓
Select highest scoring contract
```

#### 5. **Risk Management Flow** (Protection layers)

```
Layer 1: Portfolio Risk Check
    - Is total portfolio risk < 2%?
    ↓
Layer 2: Individual Position Check
    - Is this position size < max allowed?
    ↓
Layer 3: Volatility Adjustment
    - Reduce size if volatility is high
    ↓
Layer 4: Kelly Criterion
    - Calculate optimal size based on win rate
    ↓
Layer 5: Final Validation
    - Check drawdown limits
    - Check consecutive loss limits
```

---

## 🔍 Code Walkthrough - Step by Step

### What Happens When You Run the Strategy

#### **Step 1: Strategy Starts** (`main.py` or `main_multi_stock.py`)

```python
# 1. Load configuration
self.config_loader = ConfigLoader(self)
self.config_loader.load_config('config_multi_stock.json')

# 2. Set up stock subscriptions
for stock_config in self.parameters.get('stocks', []):
    ticker = stock_config['ticker']
    self.stock_symbols[ticker] = self.AddEquity(ticker)
    option = self.AddOption(ticker)
    option.SetFilter(-2, +1, timedelta(14), timedelta(45))

# 3. Create portfolio manager
self.portfolio_manager = PortfolioManager(self, portfolio_config)
self.portfolio_manager.initialize_stocks(stocks_config)
```

**What this does:**

- Loads your stock list from config file
- Sets up data feeds for each stock and its options
- Creates a manager for each stock to handle trading logic

#### **Step 2: Every Day at Market Open** (`scheduler.py`)

```python
# Schedule daily evaluation
self.Schedule.On(self.DateRules.EveryDay(),
                self.TimeRules.At(9, 30),
                self.evaluate_strategy)
```

**What this does:**

- Runs the strategy evaluation every day at 9:30 AM
- Checks if it's time to enter new trades
- Manages existing positions

#### **Step 3: Strategy Evaluation** (`portfolio_manager.py`)

```python
def evaluate_strategy(self):
    # For each stock in your portfolio
    for stock_manager in self.stock_managers:
        if stock_manager.should_evaluate():
            stock_manager.evaluate_trading_opportunity()
```

**What this does:**

- Goes through each stock you configured
- Checks if it's time to trade that stock
- Evaluates if conditions are right for a trade

#### **Step 4: Market Analysis** (`market_analyzer.py`)

```python
def analyze_market(self, symbol):
    # Calculate RSI
    rsi = self.calculate_rsi(symbol, 14)

    # Check volatility
    current_vol = self.calculate_volatility(symbol)
    historical_vol = self.get_historical_volatility(symbol)

    # Determine market regime
    if rsi < 30 and current_vol < historical_vol * 0.8:
        return "bullish_low_vol"  # Good for short puts
    elif rsi > 70 and current_vol > historical_vol * 1.2:
        return "bearish_high_vol"  # Bad for short puts
```

**What this does:**

- Calculates technical indicators (RSI, volatility)
- Determines if market conditions are favorable
- Returns "bullish_low_vol" = good for short puts
- Returns "bearish_high_vol" = bad for short puts

#### **Step 5: Risk Check** (`risk_manager.py`)

```python
def calculate_position_size(self, symbol, market_regime):
    # Kelly Criterion calculation
    win_rate = self.get_win_rate(symbol)
    avg_win = self.get_average_win(symbol)
    avg_loss = self.get_average_loss(symbol)

    kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win

    # Volatility adjustment
    if market_regime == "bearish_high_vol":
        kelly_fraction *= 0.7  # Reduce size in bad conditions

    # Portfolio risk check
    max_risk = self.portfolio_value * 0.02  # 2% max risk
    position_size = min(kelly_fraction, max_risk)

    return position_size
```

**What this does:**

- Calculates optimal position size using Kelly Criterion
- Reduces size if market conditions are bad
- Ensures total risk never exceeds 2% of portfolio

#### **Step 6: Contract Selection** (`position_manager.py`)

```python
def select_best_contract(self, symbol, target_delta_range):
    contracts = self.get_available_puts(symbol)

    best_contract = None
    best_score = 0

    for contract in contracts:
        # Score based on strike distance
        strike_score = 1 - min(abs(contract.strike - current_price) / current_price, 0.1) / 0.1

        # Score based on delta
        target_mid = (target_delta_range[0] + target_delta_range[1]) / 2
        delta_score = 1 - abs(contract.delta - target_mid) / target_mid

        # Score based on days to expiration
        dte_score = 1 - abs(contract.dte - 30) / 30  # Prefer 30 days

        total_score = strike_score * 0.4 + delta_score * 0.4 + dte_score * 0.2

        if total_score > best_score:
            best_score = total_score
            best_contract = contract

    return best_contract
```

**What this does:**

- Gets all available put options for the stock
- Scores each option based on:
  - How close the strike is to current price
  - How close the delta is to your target
  - How close the expiration is to 30 days
- Picks the option with the highest score

#### **Step 7: Trade Execution** (`trade_executor.py`)

```python
def execute_trade(self, contract, position_size):
    # Calculate number of contracts
    contract_value = contract.strike * 100  # Each contract = 100 shares
    num_contracts = int(position_size / contract_value)

    if num_contracts > 0:
        # Sell the put option
        self.Sell(contract.symbol, num_contracts)
        self.Log(f"Sold {num_contracts} {contract.symbol} puts")

        # Record the trade
        self.record_trade(contract, num_contracts, "SELL")
```

**What this does:**

- Calculates how many contracts to sell based on position size
- Executes the trade by selling put options
- Records the trade details for tracking

#### **Step 8: Position Management** (Ongoing)

```python
def manage_positions(self):
    for position in self.portfolio.positions:
        if position.symbol.type == SecurityType.Option:
            # Check if option is close to expiration
            if position.symbol.dte < 5:
                self.close_position(position)

            # Check if profit target reached
            if position.unrealized_profit_percent > 0.8:  # 80% profit
                self.close_position(position)
```

**What this does:**

- Monitors existing positions
- Closes positions that are close to expiration
- Takes profits when targets are reached
- Manages risk on open positions

### Key Decision Points

| Decision           | When                       | What Happens                      |
| ------------------ | -------------------------- | --------------------------------- |
| **Trade or Skip**  | Daily at 9:30 AM           | Market analysis + risk check      |
| **Which Stock**    | Multiple stocks available  | Pick the one with best conditions |
| **Which Contract** | Multiple options available | Score and pick the best one       |
| **Position Size**  | Before each trade          | Kelly Criterion + risk limits     |
| **Close Position** | Ongoing monitoring         | Profit target or expiration       |

---

## 🚀 Quick Start Guide

### Step 1: Choose Your Strategy

**Single Stock (Simple)**: Use `main.py` with `config/sell_put.json`
**Multi-Stock (Advanced)**: Use `main_multi_stock.py` with `config/sell_put_multi_stock.json`

### Step 2: Setup with uv

```bash
# Clone and setup
git clone <repository-url>
cd quantconnet

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Configure Your Strategy

#### Single Stock Configuration (`config/sell_put.json`)

```json
{
  "parameters": {
    "ticker": "AVGO",
    "target_delta_min": 0.25,
    "target_delta_max": 0.75,
    "max_position_size": 0.2,
    "option_frequency": "monthly",
    "risk_management": {
      "max_portfolio_risk": 0.02,
      "max_drawdown": 0.15
    }
  }
}
```

#### Multi-Stock Configuration (`config/sell_put_multi_stock.json`)

```json
{
  "parameters": {
    "portfolio": {
      "total_cash": 100000,
      "max_stocks": 5,
      "max_portfolio_risk": 0.02,
      "max_drawdown": 0.15
    },
    "stocks": [
      {
        "ticker": "AVGO",
        "weight": 0.5,
        "target_delta_min": 0.25,
        "target_delta_max": 0.75,
        "max_position_size": 0.2,
        "option_frequency": "monthly",
        "enabled": true
      },
      {
        "ticker": "AAPL",
        "weight": 0.5,
        "target_delta_min": 0.2,
        "target_delta_max": 0.6,
        "max_position_size": 0.15,
        "option_frequency": "monthly",
        "enabled": true
      }
    ]
  }
}
```

### Step 4: Run the Strategy

#### Using CLI (Recommended)

```bash
# Run single stock strategy
python cli/run_strategy.py sell-put --config config/sell_put.json

# Run multi-stock strategy
python cli/run_strategy.py sell-put --config config/sell_put_multi_stock.json

# List available configurations
python cli/run_strategy.py --list-configs
```

#### Using QuantConnect Directly

```python
# Single stock strategy
from strategies.sell_put import SellPutOption

# Multi-stock strategy
from strategies.sell_put import SellPutMultiStock
```

---

## ⚙️ Configuration

### Portfolio Settings

| Parameter            | Description             | Default | Range              |
| -------------------- | ----------------------- | ------- | ------------------ |
| `total_cash`         | Starting capital        | 100000  | Any positive value |
| `max_stocks`         | Maximum stocks to trade | 5       | 1-10               |
| `max_portfolio_risk` | Max risk per trade      | 0.02    | 0.01-0.05          |
| `max_drawdown`       | Max portfolio loss      | 0.15    | 0.10-0.25          |

### Stock Settings

| Parameter           | Description          | Default   | Range               |
| ------------------- | -------------------- | --------- | ------------------- |
| `ticker`            | Stock symbol         | -         | Valid ticker        |
| `weight`            | Portfolio allocation | 1.0       | 0.0-1.0             |
| `target_delta_min`  | Minimum delta        | 0.25      | 0.10-0.40           |
| `target_delta_max`  | Maximum delta        | 0.75      | 0.50-0.90           |
| `max_position_size` | Max position size    | 0.20      | 0.10-0.50           |
| `option_frequency`  | Trading frequency    | "monthly" | "weekly", "monthly" |
| `enabled`           | Enable/disable stock | true      | true/false          |

### Risk Management Settings

| Parameter                | Description                   | Default | Range      |
| ------------------------ | ----------------------------- | ------- | ---------- |
| `volatility_lookback`    | Volatility calculation period | 20      | 10-50      |
| `kelly_criterion`        | Use Kelly Criterion           | true    | true/false |
| `consecutive_loss_limit` | Max consecutive losses        | 3       | 2-5        |

---

## 🧠 Core Strategy Logic

### Short Put Strategy Overview

The strategy sells out-of-the-money put options to collect premium income. When the underlying stock price stays above the strike price, the option expires worthless and the premium is kept as profit.

### Trade Selection Process

1. **Market Condition Check**

   - Analyze current market regime (bullish/bearish, volatility)
   - Check if conditions are favorable for short puts

2. **Risk Assessment**

   - Calculate optimal position size using Kelly Criterion
   - Check portfolio risk limits
   - Validate drawdown constraints

3. **Contract Selection**

   - Find options within target delta range
   - Score contracts based on strike, delta, and DTE
   - Select highest-scoring contract

4. **Entry Decision**
   - Multi-layer validation process
   - Market data availability check
   - Final risk confirmation

### Contract Scoring System

```python
# Multi-criteria scoring
strike_score = 1 - min(distance_to_current, 0.1) / 0.1
delta_score = 1 - abs(delta - target_mid) / target_mid
dte_score = 1 - abs(dte - optimal_dte) / optimal_dte

total_score = strike_score * 0.4 + delta_score * 0.4 + dte_score * 0.2
```

---

## 🛡️ Risk Management

### Kelly Criterion Position Sizing

The system uses Kelly Criterion to optimize position sizes based on historical performance:

```python
kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
position_size = min(kelly_fraction, max_position_size)
```

### Volatility Adjustments

Position sizes are adjusted based on market volatility:

```python
if current_volatility > historical_volatility * 1.5:
    position_size *= 0.7  # Reduce size in high volatility
```

### Portfolio Risk Limits

- **Maximum Risk per Trade**: 2% of portfolio value
- **Maximum Drawdown**: 15% of peak portfolio value
- **Consecutive Loss Limit**: Stop trading after 3 consecutive losses

### Circuit Breakers

The system includes automatic circuit breakers:

1. **Drawdown Protection**: Stop trading if portfolio loss exceeds 15%
2. **Consecutive Loss Limit**: Pause trading after 3 consecutive losses
3. **Volatility Spike**: Reduce position sizes during high volatility periods

---

## 📊 Market Analysis

### Technical Indicators

The system analyzes multiple technical indicators:

1. **RSI (Relative Strength Index)**

   - Period: 14 days
   - Used for overbought/oversold conditions

2. **Moving Averages**

   - 50-day moving average for trend analysis
   - Price relative to MA determines trend direction

3. **Volatility Analysis**
   - Historical volatility calculation
   - Current vs. historical volatility comparison

### Market Regime Detection

The system classifies market conditions into regimes:

| Regime           | Trend | Volatility | Strategy                            |
| ---------------- | ----- | ---------- | ----------------------------------- |
| Bullish Low Vol  | Up    | Low        | Aggressive (delta 0.15-0.35)        |
| Bullish High Vol | Up    | High       | Moderate (delta 0.20-0.40)          |
| Bearish Low Vol  | Down  | Low        | Conservative (delta 0.10-0.25)      |
| Bearish High Vol | Down  | High       | Very Conservative (delta 0.05-0.15) |

### Dynamic Parameter Adjustment

Parameters adjust based on market conditions:

```python
if regime == 'bullish_low_vol':
    return (0.15, 0.35)  # More aggressive delta range
elif regime == 'bearish_high_vol':
    return (0.05, 0.15)  # More conservative delta range
```

---

## 📈 Multi-Stock Portfolio Management

### Portfolio Coordination

The multi-stock system coordinates trades across multiple stocks:

1. **Smart Trade Selection**: Choose the best stock to trade at any given time
2. **Correlation Analysis**: Consider correlations between stocks
3. **Portfolio Risk Management**: Overall risk limits across all positions
4. **Dynamic Allocation**: Adjust weights based on performance

### Correlation Management

The system analyzes correlations between stocks:

```python
# Calculate correlation matrix
correlation_matrix = returns.corr()

# Adjust position sizes based on correlations
if correlation > 0.7:
    reduce_position_size()  # High correlation = reduce risk
```

### Weight Optimization

Stock weights can be optimized based on performance:

```json
"stocks": [
    {"ticker": "AVGO", "weight": 0.40},  // Best performer
    {"ticker": "AAPL", "weight": 0.30},  // Good performer
    {"ticker": "MSFT", "weight": 0.20},  // Average
    {"ticker": "GOOGL", "weight": 0.10}  // Poor performer
]
```

### Benefits of Multi-Stock Strategy

1. **Diversification**: Spread risk across multiple stocks
2. **More Opportunities**: 4 stocks = 4x more trading chances
3. **Better Timing**: Always trade the best opportunity
4. **Risk Reduction**: Portfolio-level risk controls

---

## 📊 Performance Monitoring

### Key Metrics

The system tracks comprehensive performance metrics:

1. **Return Metrics**

   - Total Return
   - Annualized Return
   - Sharpe Ratio
   - Maximum Drawdown

2. **Risk Metrics**

   - Volatility
   - Value at Risk (VaR)
   - Beta
   - Correlation Matrix

3. **Trade Metrics**
   - Win Rate
   - Profit Factor
   - Average Win/Loss
   - Trade Duration

### Real-time Monitoring

The system provides real-time monitoring through:

1. **Risk Dashboard**: Live risk metrics and portfolio status
2. **Performance Charts**: Visual representation of returns and drawdown
3. **Trade Logs**: Detailed trade information and reasoning
4. **Alert System**: Notifications for risk limit breaches

### Performance Evaluation

The `evaluator.py` module provides comprehensive analysis:

```python
# Risk-adjusted metrics
sharpe_ratio = np.mean(returns) / np.std(returns)
profit_factor = abs(avg_win / avg_loss)

# Trade analysis
avg_duration = np.mean(durations)
max_drawdown = (peak_value - final_value) / peak_value
```

---

## 🔧 Troubleshooting

### Common Issues

#### "No trades happening"

**Possible Causes:**

- Stocks not enabled in configuration
- Market conditions unfavorable
- Risk limits preventing trades
- Option chains unavailable

**Solutions:**

1. Check `"enabled": true` in stock configuration
2. Review market analysis parameters
3. Adjust risk management settings
4. Verify option data availability

#### "Performance different than expected"

**Possible Causes:**

- Configuration changes
- Market regime shifts
- Risk parameter adjustments

**Solutions:**

1. Compare with historical performance
2. Review configuration changes
3. Check market analysis outputs
4. Adjust parameters gradually

#### "Too many/few trades"

**Possible Causes:**

- Incorrect frequency settings
- Risk limits too restrictive/loose
- Market condition filters

**Solutions:**

1. Adjust `option_frequency` setting
2. Review risk management parameters
3. Check market analysis thresholds
4. Monitor trade logs for patterns

### Debug Mode

Enable detailed logging by setting:

```python
self.Debug = True  # In Initialize method
```

### Performance Analysis

Use the evaluator to analyze performance:

```bash
# Run tests to verify functionality
uv run pytest tests/sell_put/

# Check configuration
python cli/run_strategy.py --list-configs
```

---

## 🚀 Advanced Features

### Dynamic Parameter Adjustment

The system can automatically adjust parameters based on:

1. **Market Conditions**: Delta ranges adjust to volatility
2. **Performance**: Position sizes adjust based on win rate
3. **Risk Levels**: Frequency adjusts based on drawdown

### Hedging Capabilities

Advanced hedging features include:

1. **Delta Hedging**: Dynamic hedging based on position delta
2. **Correlation Hedging**: Hedge correlated positions
3. **Volatility Hedging**: Hedge against volatility spikes

### Machine Learning Integration

The system supports ML-based enhancements:

1. **Predictive Models**: Forecast market regimes
2. **Optimization**: ML-based parameter optimization
3. **Pattern Recognition**: Identify optimal trading patterns

### Backtesting Framework

Comprehensive backtesting capabilities:

1. **Historical Analysis**: Test strategies on historical data
2. **Parameter Optimization**: Find optimal parameters
3. **Risk Analysis**: Comprehensive risk assessment
4. **Performance Comparison**: Compare different strategies

---

## 📚 Technical Details

### Risk Management Formulas

**Kelly Criterion:**

```
f = (bp - q) / b
where:
- f = optimal fraction of capital
- b = odds received on bet
- p = probability of winning
- q = probability of losing (1-p)
```

**Volatility Adjustment:**

```
position_size *= volatility_factor
where:
volatility_factor = min(1.0, historical_vol / current_vol)
```

**Portfolio Risk:**

```
max_risk = portfolio_value * risk_percentage
position_size = min(max_risk / contract_risk, max_position_size)
```

### Market Analysis Indicators

**RSI Calculation:**

```
RS = average_gain / average_loss
RSI = 100 - (100 / (1 + RS))
```

**Volatility Calculation:**

```
volatility = std(returns) * sqrt(252)
```

**Trend Analysis:**

```
trend = current_price / moving_average
if trend > 1.0: bullish
if trend < 1.0: bearish
```

### Contract Scoring Algorithm

**Strike Score:**

```
strike_score = 1 - min(distance_to_current, 0.1) / 0.1
```

**Delta Score:**

```
delta_score = 1 - abs(delta - target_mid) / target_mid
```

**DTE Score:**

```
dte_score = 1 - abs(dte - optimal_dte) / optimal_dte
```

**Total Score:**

```
total_score = strike_score * 0.4 + delta_score * 0.4 + dte_score * 0.2
```

---

## 🎯 Success Metrics

You'll know the strategy is working when:

- ✅ Consistent positive returns with controlled drawdowns
- ✅ Risk-adjusted returns (Sharpe ratio) > 1.0
- ✅ Win rate > 60% with positive profit factor
- ✅ Portfolio risk stays within defined limits
- ✅ System adapts to changing market conditions
- ✅ Multi-stock performance exceeds single-stock results

---

## 📈 Next Steps

1. **Start Simple**: Begin with single-stock strategy
2. **Test Thoroughly**: Use backtesting to validate performance
3. **Scale Gradually**: Add stocks one by one
4. **Optimize Parameters**: Fine-tune based on results
5. **Monitor Continuously**: Track performance and adjust as needed
6. **Consider Enhancements**: Add advanced features as needed

This comprehensive system provides a sophisticated foundation for short put option trading with advanced risk management, market analysis, and portfolio coordination capabilities.
