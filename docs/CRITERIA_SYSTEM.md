# Modular Trading Criteria System

## Overview

The Modular Trading Criteria System provides a flexible framework for implementing trading criteria that can be easily added, removed, or scaled across different strategies. This system replaces the previous hardcoded trading logic with a modular approach that allows for dynamic strategy configuration.

## Key Features

- **Modular Design**: Each criterion is implemented as a separate class
- **Easy Extension**: Add new criteria by implementing the `TradingCriterion` interface
- **Weighted Scoring**: Each criterion can have different weights
- **Predefined Presets**: Common strategy configurations are available out-of-the-box
- **Dynamic Adjustment**: Criteria can be added/removed at runtime
- **Detailed Evaluation**: Each criterion provides detailed feedback and scoring

## Architecture

### Core Components

1. **TradingCriterion** (Abstract Base Class)

   - Base class for all trading criteria
   - Defines the `evaluate()` method interface
   - Supports weighted scoring

2. **CriteriaManager**

   - Manages multiple criteria
   - Combines results from all criteria
   - Provides overall trade decision

3. **CriteriaPresets**
   - Predefined configurations for common strategies
   - Easy to use starting points

### Available Criteria

#### DeltaCriterion

Evaluates option delta values against a target range.

```python
criterion = DeltaCriterion(target_range=(0.25, 0.75), weight=1.0)
```

#### MarketRegimeCriterion

Evaluates market regime against allowed regimes.

```python
criterion = MarketRegimeCriterion(
    allowed_regimes=['bullish_low_vol', 'neutral_normal_vol'],
    weight=0.8
)
```

#### VolatilityCriterion

Evaluates market volatility against a maximum threshold.

```python
criterion = VolatilityCriterion(max_volatility=0.5, weight=0.7)
```

#### DTECriterion

Evaluates days to expiration against a target range.

```python
criterion = DTECriterion(min_dte=14, max_dte=45, weight=0.6)
```

#### RSICriterion

Evaluates RSI momentum indicator against oversold/overbought levels.

```python
criterion = RSICriterion(oversold=30, overbought=70, weight=0.8)
```

#### TrendCriterion

Evaluates price trend direction and strength.

```python
criterion = TrendCriterion(
    allowed_directions=['bullish', 'neutral'],
    weight=0.7
)
```

## Usage Examples

### Basic Usage

```python
from shared.utils.trading_criteria import CriteriaManager, DeltaCriterion

# Create a criteria manager
manager = CriteriaManager()

# Add a delta criterion
manager.add_criterion(DeltaCriterion(target_range=(0.25, 0.75)))

# Evaluate a trade
context = {'delta': 0.5, 'dte': 30}
should_trade, score, message = manager.should_trade(context)
print(f"Should trade: {should_trade}, Score: {score:.3f}")
print(f"Message: {message}")
```

### Using Presets

```python
from shared.utils.trading_criteria import CriteriaPresets

# Use predefined presets
delta_only = CriteriaPresets.delta_only()
conservative = CriteriaPresets.conservative()
aggressive = CriteriaPresets.aggressive()
momentum_based = CriteriaPresets.momentum_based()

# Evaluate with different presets
context = {'delta': 0.5, 'volatility': 0.3, 'rsi': 60}
should_trade, score, message = conservative.should_trade(context)
```

### Custom Strategy

```python
from shared.utils.trading_criteria import (
    CriteriaManager, DeltaCriterion, VolatilityCriterion, RSICriterion
)

# Create custom criteria manager
manager = CriteriaManager()

# Add multiple criteria with custom weights
manager.add_criterion(DeltaCriterion(target_range=(0.3, 0.7), weight=1.0))
manager.add_criterion(VolatilityCriterion(max_volatility=0.5, weight=0.8))
manager.add_criterion(RSICriterion(oversold=25, overbought=75, weight=0.6))

# Evaluate trade
context = {
    'delta': 0.5, 'volatility': 0.3, 'rsi': 60,
    'dte': 30, 'market_regime': 'bullish_normal_vol'
}
should_trade, score, message = manager.should_trade(context)
```

### Dynamic Criteria Adjustment

```python
# Start with basic criteria
manager = CriteriaManager()
manager.add_criterion(DeltaCriterion(target_range=(0.25, 0.75)))

# Add volatility criterion when market becomes volatile
if market_volatility > 0.5:
    manager.add_criterion(VolatilityCriterion(max_volatility=0.6))
    print("Added volatility criterion for high volatility market")

# Remove criteria when conditions improve
if market_volatility < 0.3:
    manager.remove_criterion("Volatility")
    print("Removed volatility criterion for low volatility market")
```

## Integration with Existing Code

### Market Analyzer Integration

The `MarketAnalyzer` class has been updated to use the criteria system:

```python
# Set custom criteria for a market analyzer
analyzer = MarketAnalyzer(strategy=strategy, ticker="AAPL")
analyzer.set_criteria(CriteriaPresets.conservative())

# The analyzer will now use the criteria system for trade decisions
analysis = analyzer.analyze_market_conditions(underlying_price)
```

### Position Manager Integration

The `PositionManager` uses criteria for contract selection:

```python
# The position manager automatically uses the criteria system
# when selecting contracts, if a criteria manager is available
position_manager.find_and_enter_position()
```

## Creating Custom Criteria

To create a new criterion, implement the `TradingCriterion` interface:

```python
from shared.utils.trading_criteria import TradingCriterion, CriteriaEvaluation, CriteriaResult

class CustomCriterion(TradingCriterion):
    def __init__(self, threshold: float, weight: float = 1.0):
        super().__init__("Custom", weight)
        self.threshold = threshold

    def evaluate(self, context: Dict[str, Any]) -> CriteriaEvaluation:
        value = context.get('custom_value', 0.0)

        if value <= self.threshold:
            return CriteriaEvaluation(
                criterion_name=self.name,
                result=CriteriaResult.PASS,
                score=1.0 - (value / self.threshold),
                message=f"Custom value {value:.3f} below threshold {self.threshold:.3f}",
                details={"custom_value": value, "threshold": self.threshold}
            )
        else:
            return CriteriaEvaluation(
                criterion_name=self.name,
                result=CriteriaResult.FAIL,
                score=0.0,
                message=f"Custom value {value:.3f} above threshold {self.threshold:.3f}",
                details={"custom_value": value, "threshold": self.threshold}
            )
```

## Context Dictionary

The criteria system expects a context dictionary with the following keys:

- `delta`: Option delta value (float)
- `dte`: Days to expiration (int)
- `volatility`: Market volatility (float)
- `market_regime`: Market regime string (str)
- `rsi`: RSI value (float)
- `trend_direction`: Trend direction (str)
- `trend_strength`: Trend strength (float)
- `underlying_price`: Underlying asset price (float)
- `strike`: Option strike price (float)
- `contract`: Option contract object (Any)

## Scoring System

Each criterion returns a score between 0.0 and 1.0:

- **0.0**: Worst possible score (criterion failed)
- **1.0**: Best possible score (criterion passed perfectly)

The overall score is calculated as a weighted average of all criteria scores.

## Migration from Old System

### Before (Hardcoded Logic)

```python
def _should_trade(self, volatility_data, market_regime):
    if volatility_data.regime == "high" and volatility_data.current > 0.5:
        return False
    if market_regime in [MarketRegime.BEARISH_HIGH_VOL, MarketRegime.BEARISH_NORMAL_VOL]:
        return False
    return True
```

### After (Modular Criteria)

```python
# Create criteria manager
manager = CriteriaManager()
manager.add_criterion(VolatilityCriterion(max_volatility=0.5))
manager.add_criterion(MarketRegimeCriterion(
    allowed_regimes=['bullish_low_vol', 'bullish_normal_vol', 'neutral_normal_vol']
))

# Evaluate trade
context = {'volatility': volatility_data.current, 'market_regime': market_regime.value}
should_trade, score, message = manager.should_trade(context)
```

## Benefits

1. **Flexibility**: Easy to add/remove criteria without code changes
2. **Reusability**: Criteria can be shared across different strategies
3. **Testability**: Each criterion can be tested independently
4. **Maintainability**: Clear separation of concerns
5. **Scalability**: Easy to extend with new criteria types
6. **Transparency**: Detailed feedback on why trades are accepted/rejected

## Best Practices

1. **Start Simple**: Begin with delta-only criteria and add complexity gradually
2. **Use Presets**: Leverage predefined presets for common strategies
3. **Weight Appropriately**: Give higher weights to more important criteria
4. **Test Thoroughly**: Test each criterion independently before combining
5. **Monitor Performance**: Track which criteria are most effective
6. **Document Changes**: Keep track of criteria changes and their impact

## Future Enhancements

- **Machine Learning Integration**: Use ML to optimize criterion weights
- **Backtesting Framework**: Automated testing of different criteria combinations
- **Visualization Tools**: Charts showing criteria performance over time
- **Configuration Files**: JSON/YAML configuration for criteria sets
- **Real-time Adjustment**: Dynamic criteria adjustment based on market conditions
