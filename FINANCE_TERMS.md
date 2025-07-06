# Finance Terms Glossary

This document explains the key finance and options trading terms used throughout the QuantConnect options trading system.

## Options Basics

### **Option**

A financial derivative that gives the holder the right, but not the obligation, to buy or sell an underlying asset at a specified price (strike price) on or before a specified date (expiration date).

### **Call Option**

An option that gives the holder the right to buy the underlying asset at the strike price.

### **Put Option**

An option that gives the holder the right to sell the underlying asset at the strike price.

### **Strike Price**

The predetermined price at which the option holder can buy (call) or sell (put) the underlying asset.

### **Expiration Date**

The date on which the option contract expires and becomes worthless if not exercised.

### **DTE (Days to Expiration)**

The number of days remaining until the option expires.

## Options Greeks

### **Delta (Δ)**

- **Definition**: Measures the rate of change in the option's price relative to a $1 change in the underlying asset's price
- **Range**: 0 to 1 for calls, -1 to 0 for puts
- **Usage in Project**: Used to select options with specific risk profiles (e.g., `target_delta_min: 0.25`, `target_delta_max: 0.75`)

### **Gamma (Γ)**

- **Definition**: Measures the rate of change in delta relative to a $1 change in the underlying asset's price
- **Significance**: Higher gamma means delta changes more rapidly with stock price movements

### **Theta (Θ)**

- **Definition**: Measures the rate of decline in the option's value due to the passage of time
- **Significance**: Time decay - options lose value as expiration approaches

### **Vega (ν)**

- **Definition**: Measures the rate of change in the option's price relative to a 1% change in implied volatility
- **Significance**: Higher vega means the option is more sensitive to volatility changes

## Options Strategies

### **Sell Put Strategy**

- **Description**: Selling put options to generate income (premium)
- **Risk**: Obligation to buy the underlying stock if assigned
- **Profit**: Limited to the premium received
- **Loss**: Potentially unlimited if stock price falls significantly
- **Best For**: Bullish or neutral market outlook

### **Covered Call Strategy**

- **Description**: Selling call options against owned stock positions
- **Risk**: Limited upside potential if stock price rises significantly
- **Profit**: Premium received + any stock appreciation up to strike price
- **Loss**: Stock price decline (unlimited)
- **Best For**: Neutral or slightly bullish market outlook

## Risk Management Terms

### **Position Size**

- **Definition**: The amount of capital allocated to a single trade or position
- **Usage**: `max_position_size: 0.20` means maximum 20% of portfolio in one position

### **Portfolio Risk**

- **Definition**: The maximum percentage of portfolio value that can be at risk
- **Usage**: `max_portfolio_risk: 0.02` means maximum 2% portfolio risk per trade

### **Drawdown**

- **Definition**: The peak-to-trough decline in portfolio value
- **Usage**: `max_drawdown: 0.15` means maximum 15% drawdown allowed

### **Correlation Threshold**

- **Definition**: Maximum correlation allowed between positions to avoid over-concentration
- **Usage**: `correlation_threshold: 0.7` means positions with >70% correlation are avoided

### **Volatility Threshold**

- **Definition**: Minimum volatility level required for option trading
- **Usage**: `volatility_threshold: 0.4` means 40% minimum implied volatility

## Market Analysis Terms

### **RSI (Relative Strength Index)**

- **Definition**: Momentum oscillator that measures speed and magnitude of price changes
- **Range**: 0 to 100
- **Usage**: `rsi_period: 14` means 14-day RSI calculation
- **Interpretation**:
  - RSI > 70: Overbought (potential sell signal)
  - RSI < 30: Oversold (potential buy signal)

### **Moving Average**

- **Definition**: Average price over a specified period, used to identify trends
- **Usage**: `moving_average_period: 50` means 50-day moving average
- **Types**: Simple Moving Average (SMA), Exponential Moving Average (EMA)

### **Volatility Lookback**

- **Definition**: Number of days used to calculate historical volatility
- **Usage**: `volatility_lookback: 20` means 20-day volatility calculation

### **Market Volatility**

- **Definition**: Measure of price variability in the market
- **Types**: Historical volatility (past price movements), Implied volatility (market expectations)

## Trading Terms

### **Premium**

- **Definition**: The price paid for an option contract
- **Usage**: When selling options, premium is income received

### **Assignment**

- **Definition**: When an option holder exercises their right, forcing the option seller to fulfill the contract
- **Risk**: Put sellers may be forced to buy stock, call sellers may be forced to sell stock

### **Exercise**

- **Definition**: The act of using an option to buy or sell the underlying asset
- **Types**: American (anytime before expiration), European (only at expiration)

### **In-the-Money (ITM)**

- **Definition**: Option with intrinsic value
- **Call**: Stock price > Strike price
- **Put**: Stock price < Strike price

### **Out-of-the-Money (OTM)**

- **Definition**: Option with no intrinsic value, only time value
- **Call**: Stock price < Strike price
- **Put**: Stock price > Strike price

### **At-the-Money (ATM)**

- **Definition**: Option where stock price equals strike price

## Performance Metrics

### **P&L (Profit and Loss)**

- **Definition**: The net profit or loss from trading activities
- **Calculation**: Total gains - Total losses

### **Sharpe Ratio**

- **Definition**: Risk-adjusted return measure
- **Formula**: (Return - Risk-free rate) / Standard deviation
- **Interpretation**: Higher is better, >1 is good

### **Sortino Ratio**

- **Definition**: Risk-adjusted return measure using downside deviation
- **Formula**: (Return - Risk-free rate) / Downside deviation
- **Advantage**: Only penalizes downside volatility

### **Maximum Drawdown**

- **Definition**: Largest peak-to-trough decline in portfolio value
- **Usage**: Risk management and performance evaluation

### **Win Rate**

- **Definition**: Percentage of profitable trades
- **Formula**: (Winning trades / Total trades) × 100

### **Profit-Loss Ratio**

- **Definition**: Average winning trade / Average losing trade
- **Target**: >1.5 for profitable strategies

## Configuration Terms

### **Option Frequency**

- **Definition**: How often to trade options
- **Values**: `monthly`, `weekly`, `daily`
- **Usage**: `option_frequency: "monthly"`

### **Target Delta Range**

- **Definition**: Preferred delta range for option selection
- **Usage**: `target_delta_min: 0.25`, `target_delta_max: 0.75`
- **Interpretation**:
  - 0.25 delta: 25% chance of being ITM at expiration
  - 0.75 delta: 75% chance of being ITM at expiration

### **Correlation Lookback**

- **Definition**: Number of days used to calculate correlation between assets
- **Usage**: `correlation_lookback: 60` means 60-day correlation

### **Volatility Lookback**

- **Definition**: Number of days used to calculate volatility
- **Usage**: `volatility_lookback: 20` means 20-day volatility

## Technical Indicators

### **Bollinger Bands**

- **Definition**: Volatility indicator with upper and lower bands around a moving average
- **Usage**: Identify overbought/oversold conditions

### **MACD (Moving Average Convergence Divergence)**

- **Definition**: Trend-following momentum indicator
- **Components**: MACD line, Signal line, Histogram
- **Usage**: Identify trend changes and momentum

### **Stochastic Oscillator**

- **Definition**: Momentum indicator comparing closing price to price range
- **Range**: 0 to 100
- **Usage**: Identify overbought/oversold conditions

## Risk Metrics

### **Beta**

- **Definition**: Measure of systematic risk relative to the market
- **Interpretation**:
  - β > 1: More volatile than market
  - β < 1: Less volatile than market
  - β = 1: Same volatility as market

### **Alpha**

- **Definition**: Excess return relative to expected return based on beta
- **Interpretation**: Positive alpha indicates outperformance

### **Information Ratio**

- **Definition**: Active return per unit of active risk
- **Formula**: (Portfolio return - Benchmark return) / Tracking error

### **Tracking Error**

- **Definition**: Standard deviation of excess returns relative to benchmark
- **Usage**: Measure of active risk

## Portfolio Management

### **Diversification**

- **Definition**: Spreading investments across different assets to reduce risk
- **Usage**: `max_stocks: 5` limits concentration in single stocks

### **Rebalancing**

- **Definition**: Adjusting portfolio weights to maintain target allocation
- **Frequency**: Can be time-based or threshold-based

### **Position Sizing**

- **Definition**: Determining the appropriate size for each trade
- **Methods**: Fixed percentage, Kelly criterion, volatility-based

### **Stop Loss**

- **Definition**: Automatic exit order to limit losses
- **Usage**: Close position when loss reaches predetermined level

### **Take Profit**

- **Definition**: Automatic exit order to secure gains
- **Usage**: Close position when profit reaches predetermined level

## Market Conditions

### **Bull Market**

- **Definition**: Rising market with optimistic sentiment
- **Strategy Impact**: Favorable for sell put strategies

### **Bear Market**

- **Definition**: Declining market with pessimistic sentiment
- **Strategy Impact**: Challenging for most option selling strategies

### **Sideways Market**

- **Definition**: Market moving within a range
- **Strategy Impact**: Ideal for option selling strategies (time decay)

### **Volatile Market**

- **Definition**: Market with large price swings
- **Strategy Impact**: Higher option premiums but increased risk

## Time Decay Concepts

### **Theta Decay**

- **Definition**: Accelerating time decay as expiration approaches
- **Impact**: Options lose value faster as expiration nears

### **Weekend Effect**

- **Definition**: Accelerated time decay over weekends
- **Impact**: Options lose 3 days of time value over weekend

### **Earnings Effect**

- **Definition**: Increased volatility around earnings announcements
- **Impact**: Higher option premiums but increased assignment risk

## Liquidity Terms

### **Bid-Ask Spread**

- **Definition**: Difference between highest bid and lowest ask prices
- **Impact**: Wider spreads increase trading costs

### **Open Interest**

- **Definition**: Number of outstanding option contracts
- **Usage**: Measure of liquidity and market activity

### **Volume**

- **Definition**: Number of contracts traded in a period
- **Usage**: Measure of market activity and liquidity

This glossary covers the essential finance and options trading terms used in the QuantConnect options trading system. Understanding these terms is crucial for effective strategy development and risk management.
