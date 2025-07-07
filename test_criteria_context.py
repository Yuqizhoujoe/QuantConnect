#!/usr/bin/env python3
"""
Test script for the new TradingContext system.

This script tests the well-defined context system that ensures all required
data is available and properly typed for criteria evaluation.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared.utils.trading_criteria import (
    TradingContext,
    CriteriaManager,
    DeltaCriterion,
    MarketRegimeCriterion,
    VolatilityCriterion,
    DTECriterion,
    RSICriterion,
    TrendCriterion,
    CriteriaPresets,
    CriteriaResult,
)


def test_trading_context_creation():
    """Test creating TradingContext with various data combinations."""
    print("Testing TradingContext creation...")
    
    # Test basic creation
    context = TradingContext(
        delta=0.3,
        dte=30,
        strike=100.0,
        underlying_price=105.0,
        volatility=0.25,
        market_regime="bullish_low_vol",
        rsi=45.0,
        trend_direction="bullish",
        trend_strength=0.7
    )
    
    assert context.delta == 0.3
    assert context.dte == 30
    assert context.strike == 100.0
    assert context.underlying_price == 105.0
    assert context.volatility == 0.25
    assert context.market_regime == "bullish_low_vol"
    assert context.rsi == 45.0
    assert context.trend_direction == "bullish"
    assert context.trend_strength == 0.7
    
    print("✓ Basic TradingContext creation works")
    
    # Test with defaults
    default_context = TradingContext()
    assert default_context.delta == 0.0
    assert default_context.dte == 0
    assert default_context.market_regime == "unknown"
    assert default_context.rsi == 50.0
    
    print("✓ Default TradingContext creation works")


def test_trading_context_validation():
    """Test TradingContext validation."""
    print("\nTesting TradingContext validation...")
    
    # Test valid context
    valid_context = TradingContext(
        delta=0.3,
        dte=30,
        strike=100.0,
        underlying_price=105.0,
        volatility=0.25,
        market_regime="bullish_low_vol",
        rsi=45.0,
        trend_direction="bullish",
        trend_strength=0.7
    )
    
    errors = valid_context.validate()
    assert len(errors) == 0, f"Valid context should have no errors: {errors}"
    print("✓ Valid context passes validation")
    
    # Test invalid contexts
    invalid_contexts = [
        # Missing delta
        TradingContext(dte=30, strike=100.0, underlying_price=105.0),
        # Invalid delta range
        TradingContext(delta=1.5, dte=30, strike=100.0, underlying_price=105.0),
        # Invalid DTE
        TradingContext(delta=0.3, dte=-5, strike=100.0, underlying_price=105.0),
        # Invalid volatility
        TradingContext(delta=0.3, dte=30, strike=100.0, underlying_price=105.0, volatility=3.0),
        # Invalid RSI
        TradingContext(delta=0.3, dte=30, strike=100.0, underlying_price=105.0, rsi=150.0),
        # Invalid trend strength
        TradingContext(delta=0.3, dte=30, strike=100.0, underlying_price=105.0, trend_strength=1.5),
    ]
    
    for i, context in enumerate(invalid_contexts):
        errors = context.validate()
        assert len(errors) > 0, f"Invalid context {i} should have validation errors"
        print(f"✓ Invalid context {i} correctly caught: {errors[0]}")


def test_criteria_with_context():
    """Test criteria evaluation with TradingContext."""
    print("\nTesting criteria evaluation with TradingContext...")
    
    # Create a valid context
    context = TradingContext(
        delta=0.3,
        dte=30,
        strike=100.0,
        underlying_price=105.0,
        volatility=0.25,
        market_regime="bullish_low_vol",
        rsi=45.0,
        trend_direction="bullish",
        trend_strength=0.7
    )
    
    # Test DeltaCriterion
    delta_criterion = DeltaCriterion(target_range=(0.25, 0.75))
    evaluation = delta_criterion.evaluate(context)
    assert evaluation.result == CriteriaResult.PASS
    assert evaluation.score > 0.0
    print(f"✓ DeltaCriterion: {evaluation.message}")
    
    # Test MarketRegimeCriterion
    regime_criterion = MarketRegimeCriterion(allowed_regimes=["bullish_low_vol", "neutral_normal_vol"])
    evaluation = regime_criterion.evaluate(context)
    assert evaluation.result == CriteriaResult.PASS
    assert evaluation.score == 1.0
    print(f"✓ MarketRegimeCriterion: {evaluation.message}")
    
    # Test VolatilityCriterion
    vol_criterion = VolatilityCriterion(max_volatility=0.5)
    evaluation = vol_criterion.evaluate(context)
    assert evaluation.result == CriteriaResult.PASS
    assert evaluation.score > 0.0
    print(f"✓ VolatilityCriterion: {evaluation.message}")
    
    # Test DTECriterion
    dte_criterion = DTECriterion(min_dte=14, max_dte=45)
    evaluation = dte_criterion.evaluate(context)
    assert evaluation.result == CriteriaResult.PASS
    assert evaluation.score > 0.0
    print(f"✓ DTECriterion: {evaluation.message}")
    
    # Test RSICriterion
    rsi_criterion = RSICriterion(oversold=30, overbought=70)
    evaluation = rsi_criterion.evaluate(context)
    assert evaluation.result == CriteriaResult.PASS
    assert evaluation.score > 0.0
    print(f"✓ RSICriterion: {evaluation.message}")
    
    # Test TrendCriterion
    trend_criterion = TrendCriterion(allowed_directions=["bullish", "neutral"])
    evaluation = trend_criterion.evaluate(context)
    assert evaluation.result == CriteriaResult.PASS
    assert evaluation.score > 0.0
    print(f"✓ TrendCriterion: {evaluation.message}")


def test_criteria_manager_with_context():
    """Test CriteriaManager with TradingContext."""
    print("\nTesting CriteriaManager with TradingContext...")
    
    # Create a criteria manager
    manager = CriteriaManager()
    manager.add_criterion(DeltaCriterion(target_range=(0.25, 0.75)))
    manager.add_criterion(MarketRegimeCriterion(allowed_regimes=["bullish_low_vol", "neutral_normal_vol"]))
    manager.add_criterion(VolatilityCriterion(max_volatility=0.5))
    
    # Test with valid context
    valid_context = TradingContext(
        delta=0.3,
        dte=30,
        strike=100.0,
        underlying_price=105.0,
        volatility=0.25,
        market_regime="bullish_low_vol",
        rsi=45.0,
        trend_direction="bullish",
        trend_strength=0.7
    )
    
    should_trade, score, message = manager.should_trade(valid_context)
    assert should_trade == True
    assert score > 0.0
    print(f"✓ Valid context allows trade: {message}")
    
    # Test with invalid context (wrong market regime)
    invalid_context = TradingContext(
        delta=0.3,
        dte=30,
        strike=100.0,
        underlying_price=105.0,
        volatility=0.25,
        market_regime="bearish_high_vol",  # Not in allowed regimes
        rsi=45.0,
        trend_direction="bullish",
        trend_strength=0.7
    )
    
    should_trade, score, message = manager.should_trade(invalid_context)
    assert should_trade == False
    assert score == 0.0
    print(f"✓ Invalid context blocks trade: {message}")
    
    # Test with missing required fields
    incomplete_context = TradingContext(
        delta=0.3,
        # Missing dte, strike, underlying_price
        volatility=0.25,
        market_regime="bullish_low_vol"
    )
    
    should_trade, score, message = manager.should_trade(incomplete_context)
    assert should_trade == False
    assert "validation failed" in message.lower()
    print(f"✓ Incomplete context blocked: {message}")


def test_required_fields():
    """Test required fields detection."""
    print("\nTesting required fields detection...")
    
    # Test individual criteria
    delta_criterion = DeltaCriterion(target_range=(0.25, 0.75))
    assert "delta" in delta_criterion.get_required_fields()
    print("✓ DeltaCriterion requires 'delta'")
    
    regime_criterion = MarketRegimeCriterion(allowed_regimes=["bullish_low_vol"])
    assert "market_regime" in regime_criterion.get_required_fields()
    print("✓ MarketRegimeCriterion requires 'market_regime'")
    
    vol_criterion = VolatilityCriterion(max_volatility=0.5)
    assert "volatility" in vol_criterion.get_required_fields()
    print("✓ VolatilityCriterion requires 'volatility'")
    
    dte_criterion = DTECriterion(min_dte=14, max_dte=45)
    assert "dte" in dte_criterion.get_required_fields()
    print("✓ DTECriterion requires 'dte'")
    
    rsi_criterion = RSICriterion(oversold=30, overbought=70)
    assert "rsi" in rsi_criterion.get_required_fields()
    print("✓ RSICriterion requires 'rsi'")
    
    trend_criterion = TrendCriterion(allowed_directions=["bullish"])
    required_fields = trend_criterion.get_required_fields()
    assert "trend_direction" in required_fields
    assert "trend_strength" in required_fields
    print("✓ TrendCriterion requires 'trend_direction' and 'trend_strength'")
    
    # Test criteria manager
    manager = CriteriaManager()
    manager.add_criterion(delta_criterion)
    manager.add_criterion(regime_criterion)
    manager.add_criterion(vol_criterion)
    
    required_fields = manager.get_required_fields()
    assert "delta" in required_fields
    assert "market_regime" in required_fields
    assert "volatility" in required_fields
    print(f"✓ CriteriaManager requires: {required_fields}")


def test_presets_with_context():
    """Test predefined presets with TradingContext."""
    print("\nTesting predefined presets with TradingContext...")
    
    # Test delta_only preset
    delta_only_manager = CriteriaPresets.delta_only()
    context = TradingContext(
        delta=0.4,
        dte=30,
        strike=100.0,
        underlying_price=105.0
    )
    
    should_trade, score, message = delta_only_manager.should_trade(context)
    assert should_trade == True
    print(f"✓ Delta-only preset: {message}")
    
    # Test conservative preset
    conservative_manager = CriteriaPresets.conservative()
    context = TradingContext(
        delta=0.3,
        dte=30,
        strike=100.0,
        underlying_price=105.0,
        volatility=0.25,
        market_regime="bullish_low_vol",
        rsi=45.0,
        trend_direction="bullish",
        trend_strength=0.7
    )
    
    should_trade, score, message = conservative_manager.should_trade(context)
    assert should_trade == True
    print(f"✓ Conservative preset: {message}")
    
    # Test aggressive preset
    aggressive_manager = CriteriaPresets.aggressive()
    context = TradingContext(
        delta=0.5,
        dte=30,
        strike=100.0,
        underlying_price=105.0,
        volatility=0.4
    )
    
    should_trade, score, message = aggressive_manager.should_trade(context)
    assert should_trade == True
    print(f"✓ Aggressive preset: {message}")
    
    # Test momentum_based preset
    momentum_manager = CriteriaPresets.momentum_based()
    context = TradingContext(
        delta=0.4,
        dte=30,
        strike=100.0,
        underlying_price=105.0,
        rsi=45.0,
        trend_direction="bullish",
        trend_strength=0.7
    )
    
    should_trade, score, message = momentum_manager.should_trade(context)
    assert should_trade == True
    print(f"✓ Momentum-based preset: {message}")


def test_context_conversion():
    """Test TradingContext conversion methods."""
    print("\nTesting TradingContext conversion methods...")
    
    # Create context
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
    
    # Test to_dict
    context_dict = context.to_dict()
    assert context_dict['delta'] == 0.3
    assert context_dict['dte'] == 30
    assert context_dict['market_regime'] == "bullish_low_vol"
    assert context_dict['timestamp'] == "2023-01-01"
    print("✓ to_dict() works correctly")
    
    # Test from_dict
    new_context = TradingContext.from_dict(context_dict)
    assert new_context.delta == 0.3
    assert new_context.dte == 30
    assert new_context.market_regime == "bullish_low_vol"
    print("✓ from_dict() works correctly")


def main():
    """Run all tests."""
    print("Testing TradingContext System")
    print("=" * 50)
    
    try:
        test_trading_context_creation()
        test_trading_context_validation()
        test_criteria_with_context()
        test_criteria_manager_with_context()
        test_required_fields()
        test_presets_with_context()
        test_context_conversion()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! TradingContext system is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 