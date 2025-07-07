"""
Example: Using the Modular Trading Criteria System

This example demonstrates how to use the new criteria system to create
different trading strategies with varying levels of complexity.
"""

from shared.utils.trading_criteria import (
    CriteriaManager,
    CriteriaPresets,
    DeltaCriterion,
    MarketRegimeCriterion,
    VolatilityCriterion,
    DTECriterion,
    RSICriterion,
    TrendCriterion,
)


def example_delta_only_strategy():
    """Example: Strategy using only delta criteria."""
    print("=== Delta-Only Strategy ===")
    
    # Use the predefined delta-only preset
    criteria_manager = CriteriaPresets.delta_only()
    print(criteria_manager.get_criteria_summary())
    
    # Test with different delta values
    test_contexts = [
        {'delta': 0.3, 'dte': 30},  # Good delta
        {'delta': 0.8, 'dte': 30},  # Too high delta
        {'delta': 0.1, 'dte': 30},  # Too low delta
    ]
    
    for context in test_contexts:
        should_trade, score, message = criteria_manager.should_trade(context)
        print(f"Delta {context['delta']}: {message} (Score: {score:.3f})")
    print()


def example_conservative_strategy():
    """Example: Conservative strategy with multiple criteria."""
    print("=== Conservative Strategy ===")
    
    # Use the predefined conservative preset
    criteria_manager = CriteriaPresets.conservative()
    print(criteria_manager.get_criteria_summary())
    
    # Test with different market conditions
    test_contexts = [
        {
            'delta': 0.4, 'dte': 30, 'market_regime': 'bullish_low_vol',
            'volatility': 0.2, 'rsi': 55, 'trend_direction': 'bullish'
        },  # Good conditions
        {
            'delta': 0.4, 'dte': 30, 'market_regime': 'bearish_high_vol',
            'volatility': 0.6, 'rsi': 25, 'trend_direction': 'bearish'
        },  # Bad conditions
    ]
    
    for context in test_contexts:
        should_trade, score, message = criteria_manager.should_trade(context)
        print(f"Conditions: {context['market_regime']}, Vol: {context['volatility']}")
        print(f"Result: {message} (Score: {score:.3f})")
    print()


def example_custom_strategy():
    """Example: Custom strategy with specific criteria."""
    print("=== Custom Strategy ===")
    
    # Create a custom criteria manager
    criteria_manager = CriteriaManager()
    
    # Add specific criteria with custom weights
    criteria_manager.add_criterion(DeltaCriterion(target_range=(0.3, 0.7), weight=1.0))
    criteria_manager.add_criterion(VolatilityCriterion(max_volatility=0.5, weight=0.8))
    criteria_manager.add_criterion(RSICriterion(oversold=20, overbought=80, weight=0.6))
    criteria_manager.add_criterion(TrendCriterion(
        allowed_directions=['bullish', 'neutral'], 
        weight=0.7
    ))
    
    print(criteria_manager.get_criteria_summary())
    
    # Test the custom criteria
    test_context = {
        'delta': 0.5, 'dte': 30, 'market_regime': 'bullish_normal_vol',
        'volatility': 0.3, 'rsi': 60, 'trend_direction': 'bullish'
    }
    
    should_trade, score, message = criteria_manager.should_trade(test_context)
    print(f"Custom criteria result: {message} (Score: {score:.3f})")
    print()


def example_dynamic_criteria_adjustment():
    """Example: Dynamically adjusting criteria based on market conditions."""
    print("=== Dynamic Criteria Adjustment ===")
    
    # Start with basic criteria
    criteria_manager = CriteriaManager()
    criteria_manager.add_criterion(DeltaCriterion(target_range=(0.25, 0.75)))
    
    print("Initial criteria:")
    print(criteria_manager.get_criteria_summary())
    
    # Simulate market conditions changing
    market_conditions = [
        {'volatility': 0.2, 'market_regime': 'bullish_low_vol'},  # Low vol, bullish
        {'volatility': 0.6, 'market_regime': 'bearish_high_vol'},  # High vol, bearish
    ]
    
    for condition in market_conditions:
        print(f"\nMarket condition: {condition['market_regime']}, Vol: {condition['volatility']}")
        
        # Adjust criteria based on market conditions
        if condition['volatility'] > 0.5:
            # High volatility - add volatility criterion
            criteria_manager.add_criterion(VolatilityCriterion(max_volatility=0.6))
            print("Added volatility criterion for high volatility market")
        else:
            # Low volatility - remove volatility criterion if exists
            criteria_manager.remove_criterion("Volatility")
            print("Removed volatility criterion for low volatility market")
        
        print("Updated criteria:")
        print(criteria_manager.get_criteria_summary())
        
        # Test with same context
        test_context = {'delta': 0.4, 'dte': 30, **condition}
        should_trade, score, message = criteria_manager.should_trade(test_context)
        print(f"Result: {message} (Score: {score:.3f})")
    print()


def example_strategy_comparison():
    """Example: Comparing different strategy presets."""
    print("=== Strategy Comparison ===")
    
    strategies = {
        'Delta Only': CriteriaPresets.delta_only(),
        'Conservative': CriteriaPresets.conservative(),
        'Aggressive': CriteriaPresets.aggressive(),
        'Momentum Based': CriteriaPresets.momentum_based(),
    }
    
    # Test context
    test_context = {
        'delta': 0.45, 'dte': 30, 'market_regime': 'bullish_normal_vol',
        'volatility': 0.35, 'rsi': 65, 'trend_direction': 'bullish'
    }
    
    print("Test context:", test_context)
    print()
    
    for strategy_name, criteria_manager in strategies.items():
        print(f"--- {strategy_name} ---")
        print(criteria_manager.get_criteria_summary())
        
        should_trade, score, message = criteria_manager.should_trade(test_context)
        print(f"Result: {message} (Score: {score:.3f})")
        print()


if __name__ == "__main__":
    print("Modular Trading Criteria System Examples")
    print("=" * 50)
    
    example_delta_only_strategy()
    example_conservative_strategy()
    example_custom_strategy()
    example_dynamic_criteria_adjustment()
    example_strategy_comparison()
    
    print("Examples completed!") 