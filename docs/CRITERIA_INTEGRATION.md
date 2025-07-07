# Criteria System Integration Guide

## Overview

The modular trading criteria system has been fully integrated into the current sell put strategy implementation. This guide explains how to use the system with different configuration options.

## Quick Start

### 1. Delta-Only Strategy (Simplified)

Use the `sell_put_delta_only.json` configuration:

```bash
python run_backtest.py --config config/sell_put_delta_only.json
```

This configuration uses only delta criteria, which is the simplified approach you requested.

### 2. Conservative Strategy

Use the `sell_put_conservative.json` configuration:

```bash
python run_backtest.py --config config/sell_put_conservative.json
```

This configuration uses multiple criteria for more conservative trading.

### 3. Custom Strategy

Use the `sell_put_custom.json` configuration:

```bash
python run_backtest.py --config config/sell_put_custom.json
```

This configuration shows how to create custom criteria combinations.

## Configuration Options

### Available Criteria Types

1. **`delta_only`** - Only uses delta criteria (simplified approach)
2. **`conservative`** - Uses delta, market regime, volatility, and DTE criteria
3. **`aggressive`** - Uses delta and volatility criteria with relaxed thresholds
4. **`momentum_based`** - Uses delta, RSI, and trend criteria
5. **`custom`** - Allows fine-grained control over individual criteria

### Configuration Structure

```json
{
  "stocks": [
    {
      "ticker": "AAPL",
      "criteria": {
        "type": "delta_only"
      }
    }
  ]
}
```

### Custom Criteria Configuration

For fine-grained control, use the `custom` type:

```json
{
  "stocks": [
    {
      "ticker": "AAPL",
      "criteria": {
        "type": "custom",
        "delta": {
          "range": [0.3, 0.7],
          "weight": 1.0
        },
        "volatility": {
          "enabled": true,
          "max_volatility": 0.5,
          "weight": 0.8
        },
        "market_regime": {
          "enabled": true,
          "allowed_regimes": ["bullish_low_vol", "neutral_normal_vol"],
          "weight": 0.7
        },
        "rsi": {
          "enabled": true,
          "oversold": 25,
          "overbought": 75,
          "weight": 0.6
        },
        "trend": {
          "enabled": true,
          "allowed_directions": ["bullish", "neutral"],
          "weight": 0.5
        },
        "dte": {
          "enabled": true,
          "range": [21, 45],
          "weight": 0.6
        }
      }
    }
  ]
}
```

## Testing the Integration

Run the integration test to verify everything works:

```bash
python test_criteria_integration.py
```

This will test:

- Criteria presets functionality
- Criteria manager operations
- Market analyzer integration
- Configuration parsing

## How It Works

### 1. Strategy Initialization

When the strategy initializes, it:

1. Loads the configuration file
2. Creates stock managers for each stock
3. Sets up criteria managers based on configuration
4. Assigns criteria managers to each stock's market analyzer

### 2. Trade Evaluation

During trading:

1. The market analyzer evaluates market conditions
2. The criteria manager evaluates all criteria against the current context
3. If all criteria pass, the trade is allowed
4. If any criterion fails, the trade is rejected
5. Detailed logging shows which criteria passed/failed

### 3. Contract Selection

When selecting contracts:

1. The position manager filters contracts by basic criteria (expiry, delta range)
2. Each valid contract is evaluated using the criteria system
3. Contracts are scored based on criteria performance
4. The highest-scoring contract is selected

## Logging and Debugging

The system provides detailed logging:

```
AAPL: Criteria evaluation - Trade allowed by 3 criteria with score 0.850
AAPL: Contract AAPL230120P150 scored 0.920 - Delta 0.450 within range 0.250-0.750
AAPL: Contract AAPL230120P155 rejected - Volatility 0.600 above threshold 0.500
```

This helps you understand:

- Which criteria are being evaluated
- Why trades are accepted or rejected
- How contracts are scored

## Migration from Old System

### Before (Hardcoded)

The old system had hardcoded logic in the market analyzer:

```python
def _should_trade(self, volatility_data, market_regime):
    if volatility_data.regime == "high" and volatility_data.current > 0.5:
        return False
    if market_regime in [MarketRegime.BEARISH_HIGH_VOL, MarketRegime.BEARISH_NORMAL_VOL]:
        return False
    return True
```

### After (Modular)

The new system uses configurable criteria:

```json
{
  "criteria": {
    "type": "conservative"
  }
}
```

Or for custom control:

```json
{
  "criteria": {
    "type": "custom",
    "volatility": {
      "enabled": true,
      "max_volatility": 0.5
    },
    "market_regime": {
      "enabled": true,
      "allowed_regimes": ["bullish_low_vol", "neutral_normal_vol"]
    }
  }
}
```

## Benefits of the New System

1. **Configuration-Driven**: Change trading logic without code changes
2. **Modular**: Add/remove criteria independently
3. **Reusable**: Same criteria can be used across different strategies
4. **Testable**: Each criterion can be tested independently
5. **Transparent**: Clear feedback on trade decisions
6. **Scalable**: Easy to add new criteria types

## Best Practices

1. **Start Simple**: Begin with `delta_only` and add complexity gradually
2. **Test Thoroughly**: Use the integration test to verify functionality
3. **Monitor Logs**: Check the detailed logging to understand trade decisions
4. **Use Presets**: Leverage predefined presets for common strategies
5. **Customize Carefully**: Only use custom criteria when presets don't meet your needs

## Troubleshooting

### Common Issues

1. **No trades being executed**

   - Check if criteria are too restrictive
   - Review the logging for specific rejection reasons
   - Try using `delta_only` preset first

2. **Configuration errors**

   - Verify JSON syntax
   - Check that criteria types are valid
   - Ensure all required fields are present

3. **Performance issues**
   - Reduce the number of criteria if performance is slow
   - Use simpler criteria types for faster evaluation

### Getting Help

1. Run the integration test: `python test_criteria_integration.py`
2. Check the logs for detailed error messages
3. Review the configuration examples in the `config/` directory
4. Consult the main criteria system documentation: `docs/CRITERIA_SYSTEM.md`
