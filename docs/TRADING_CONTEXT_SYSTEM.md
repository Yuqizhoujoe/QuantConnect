# TradingContext System

## Overview

The `TradingContext` system provides a well-defined, type-safe context for trading criteria evaluation. This system ensures that all required data is available and properly validated before criteria evaluation, preventing runtime errors and improving code reliability.

## Key Features

### 1. Well-Defined Data Structure

The `TradingContext` class provides a structured way to pass all required data for criteria evaluation:

```python
@dataclass
class TradingContext:
    # Option-specific data
    delta: float = 0.0
    dte: int = 0
    strike: float = 0.0
    underlying_price: float = 0.0

    # Market data
    volatility: float = 0.0
    market_regime: str = "unknown"
    rsi: float = 50.0
    trend_direction: str = "neutral"
    trend_strength: float = 0.5

    # Additional context
    contract: Optional[Any] = None
    timestamp: Optional[str] = None
```

### 2. Built-in Validation

The context system includes comprehensive validation to ensure data quality:

```python
def validate(self) -> List[str]:
    """Validate that required data is available."""
    errors = []

    # Check for required numeric data
    if self.delta == 0.0:
        errors.append("Delta is required")
    if self.dte == 0:
        errors.append("DTE is required")
    # ... more validation rules

    return errors
```

### 3. Required Fields Detection

Each criterion can specify which fields it requires:

```python
class DeltaCriterion(TradingCriterion):
    def get_required_fields(self) -> List[str]:
        return ["delta"]
```

### 4. Automatic Context Validation

The `CriteriaManager` automatically validates context before evaluation:

```python
def validate_context(self, context: TradingContext) -> List[str]:
    """Validate that context has all required fields."""
    errors = []

    # Check context validation
    errors.extend(context.validate())

    # Check required fields for criteria
    required_fields = self.get_required_fields()
    for field in required_fields:
        if not hasattr(context, field) or getattr(context, field) is None:
            errors.append(f"Required field '{field}' is missing")

    return errors
```

## Usage Examples

### 1. Creating a TradingContext

```python
# Create context with all required data
context = TradingContext(
    delta=0.3,
    dte=30,
    strike=100.0,
    underlying_price=105.0,
    volatility=0.25,
    market_regime="bullish_low_vol",
    rsi=45.0,
    trend_direction="bullish",
    trend_strength=0.7,
    timestamp="2023-01-01"
)
```

### 2. Using with Criteria Evaluation

```python
# Create criteria manager
manager = CriteriaManager()
manager.add_criterion(DeltaCriterion(target_range=(0.25, 0.75)))
manager.add_criterion(MarketRegimeCriterion(allowed_regimes=["bullish_low_vol"]))

# Evaluate criteria
should_trade, score, message = manager.should_trade(context)
```

### 3. Integration in Market Analyzer

```python
def _create_evaluation_context(self, underlying_price, trend_data, volatility_data, market_regime, rsi) -> TradingContext:
    """Create TradingContext for criteria evaluation."""
    return TradingContext(
        underlying_price=underlying_price,
        trend_direction=trend_data.direction,
        trend_strength=trend_data.strength,
        volatility=volatility_data.current,
        market_regime=market_regime.value,
        rsi=rsi,
        dte=30,  # Default DTE - will be updated by position manager
        delta=0.5,  # Default delta - will be updated by position manager
        timestamp=str(self.strategy.Time),
    )
```

### 4. Integration in Position Manager

```python
# Create TradingContext for contract evaluation
context = TradingContext(
    delta=delta,
    dte=dte,
    strike=contract.Strike,
    underlying_price=underlying_price,
    volatility=market_analysis.volatility.current if market_analysis else 0.0,
    market_regime=market_analysis.market_regime.value if market_analysis else "unknown",
    rsi=market_analysis.rsi if market_analysis else 50.0,
    trend_direction=market_analysis.trend.direction if market_analysis else "neutral",
    trend_strength=market_analysis.trend.strength if market_analysis else 0.5,
    contract=contract,
    timestamp=str(self.strategy.Time)
)

# Evaluate using criteria manager
should_trade, score, message = self.market_analyzer.criteria_manager.should_trade(context)
```

## Benefits

### 1. Type Safety

- All data fields are properly typed
- IDE support for autocomplete and error detection
- Compile-time error checking

### 2. Data Validation

- Automatic validation of required fields
- Range checking for numeric values
- Clear error messages for missing or invalid data

### 3. Required Fields Tracking

- Each criterion specifies its requirements
- Automatic detection of missing data
- Prevents evaluation with incomplete context

### 4. Backward Compatibility

- Conversion methods to/from dictionaries
- Easy migration from existing code
- Maintains existing API compatibility

### 5. Error Prevention

- Validates context before criteria evaluation
- Prevents runtime errors from missing data
- Clear error messages for debugging

## Validation Rules

The system validates the following:

### Required Fields

- `delta`: Must be provided and non-zero
- `dte`: Must be provided and non-zero
- `strike`: Must be provided and non-zero
- `underlying_price`: Must be provided and non-zero

### Range Validation

- `delta`: Must be between 0.0 and 1.0
- `dte`: Must be non-negative
- `underlying_price`: Must be non-negative
- `strike`: Must be non-negative
- `volatility`: Must be between 0.0 and 2.0
- `rsi`: Must be between 0.0 and 100.0
- `trend_strength`: Must be between 0.0 and 1.0

## Error Handling

When validation fails, the system provides clear error messages:

```python
# Example error messages
"Delta is required"
"DTE must be non-negative"
"Volatility must be between 0.0 and 2.0"
"Required field 'market_regime' is missing"
```

## Migration Guide

### From Dictionary Context

Old approach:

```python
context = {
    'delta': 0.3,
    'dte': 30,
    'market_regime': 'bullish_low_vol'
}
```

New approach:

```python
context = TradingContext(
    delta=0.3,
    dte=30,
    market_regime='bullish_low_vol'
)
```

### From Existing Code

1. Replace dictionary creation with `TradingContext` instantiation
2. Update criteria evaluation calls to use the new context
3. Add validation error handling where appropriate
4. Test with the new validation system

## Testing

The system includes comprehensive tests in `test_criteria_context.py`:

- Context creation and validation
- Criteria evaluation with context
- Required fields detection
- Error handling and validation
- Preset configurations
- Conversion methods

Run tests with:

```bash
python test_criteria_context.py
```

## Best Practices

### 1. Always Validate Context

```python
# Good: Validate before use
errors = context.validate()
if errors:
    self.strategy.Log(f"Context validation failed: {errors}")
    return False
```

### 2. Use Type Hints

```python
# Good: Use proper type hints
def evaluate(self, context: TradingContext) -> CriteriaEvaluation:
    pass
```

### 3. Handle Missing Data Gracefully

```python
# Good: Provide defaults for optional data
context = TradingContext(
    delta=delta,
    dte=dte,
    underlying_price=underlying_price,
    # Optional fields with defaults
    volatility=market_analysis.volatility.current if market_analysis else 0.0,
    market_regime=market_analysis.market_regime.value if market_analysis else "unknown"
)
```

### 4. Log Validation Errors

```python
# Good: Log validation errors for debugging
validation_errors = self.validate_context(context)
if validation_errors:
    self.strategy.Log(f"Context validation failed: {validation_errors}")
    return False, 0.0, f"Context validation failed: {', '.join(validation_errors)}"
```

## Conclusion

The `TradingContext` system provides a robust, type-safe foundation for trading criteria evaluation. It ensures data quality, prevents runtime errors, and makes the codebase more maintainable and reliable.

Key advantages:

- **Type Safety**: Compile-time error checking
- **Data Validation**: Automatic validation of required fields and ranges
- **Error Prevention**: Clear error messages and graceful handling
- **Maintainability**: Well-defined interfaces and clear documentation
- **Extensibility**: Easy to add new fields and validation rules

This system significantly improves the reliability and maintainability of the trading criteria framework.
