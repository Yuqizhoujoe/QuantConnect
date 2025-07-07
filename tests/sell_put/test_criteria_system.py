"""
Test for the Modular Trading Criteria System.

This test verifies that the criteria system works correctly for different
strategies and can be easily extended.
"""

import unittest
from unittest.mock import Mock
from shared.utils.trading_criteria import (
    CriteriaManager,
    CriteriaPresets,
    DeltaCriterion,
    MarketRegimeCriterion,
    VolatilityCriterion,
    DTECriterion,
    RSICriterion,
    TrendCriterion,
    CriteriaResult,
)


class TestCriteriaSystem(unittest.TestCase):
    """Test the modular criteria system."""

    def setUp(self):
        """Set up test fixtures."""
        pass

    def test_delta_criterion(self):
        """Test delta criterion evaluation."""
        criterion = DeltaCriterion(target_range=(0.25, 0.75))
        
        # Test good delta
        result = criterion.evaluate({'delta': 0.5})
        self.assertEqual(result.result, CriteriaResult.PASS)
        self.assertGreater(result.score, 0.8)
        
        # Test delta too high
        result = criterion.evaluate({'delta': 0.8})
        self.assertEqual(result.result, CriteriaResult.FAIL)
        self.assertEqual(result.score, 0.0)
        
        # Test delta too low
        result = criterion.evaluate({'delta': 0.1})
        self.assertEqual(result.result, CriteriaResult.FAIL)
        self.assertEqual(result.score, 0.0)

    def test_market_regime_criterion(self):
        """Test market regime criterion evaluation."""
        criterion = MarketRegimeCriterion(allowed_regimes=['bullish_low_vol', 'neutral_normal_vol'])
        
        # Test allowed regime
        result = criterion.evaluate({'market_regime': 'bullish_low_vol'})
        self.assertEqual(result.result, CriteriaResult.PASS)
        self.assertEqual(result.score, 1.0)
        
        # Test disallowed regime
        result = criterion.evaluate({'market_regime': 'bearish_high_vol'})
        self.assertEqual(result.result, CriteriaResult.FAIL)
        self.assertEqual(result.score, 0.0)

    def test_volatility_criterion(self):
        """Test volatility criterion evaluation."""
        criterion = VolatilityCriterion(max_volatility=0.5)
        
        # Test low volatility
        result = criterion.evaluate({'volatility': 0.2})
        self.assertEqual(result.result, CriteriaResult.PASS)
        self.assertGreater(result.score, 0.5)
        
        # Test high volatility
        result = criterion.evaluate({'volatility': 0.6})
        self.assertEqual(result.result, CriteriaResult.FAIL)
        self.assertEqual(result.score, 0.0)

    def test_dte_criterion(self):
        """Test DTE criterion evaluation."""
        criterion = DTECriterion(min_dte=14, max_dte=45)
        
        # Test good DTE
        result = criterion.evaluate({'dte': 30})
        self.assertEqual(result.result, CriteriaResult.PASS)
        self.assertGreater(result.score, 0.8)
        
        # Test DTE too low
        result = criterion.evaluate({'dte': 10})
        self.assertEqual(result.result, CriteriaResult.FAIL)
        self.assertEqual(result.score, 0.0)
        
        # Test DTE too high
        result = criterion.evaluate({'dte': 60})
        self.assertEqual(result.result, CriteriaResult.FAIL)
        self.assertEqual(result.score, 0.0)

    def test_rsi_criterion(self):
        """Test RSI criterion evaluation."""
        criterion = RSICriterion(oversold=30, overbought=70)
        
        # Test good RSI
        result = criterion.evaluate({'rsi': 50})
        self.assertEqual(result.result, CriteriaResult.PASS)
        self.assertGreater(result.score, 0.8)
        
        # Test oversold RSI
        result = criterion.evaluate({'rsi': 20})
        self.assertEqual(result.result, CriteriaResult.FAIL)
        self.assertEqual(result.score, 0.0)
        
        # Test overbought RSI
        result = criterion.evaluate({'rsi': 80})
        self.assertEqual(result.result, CriteriaResult.FAIL)
        self.assertEqual(result.score, 0.0)

    def test_trend_criterion(self):
        """Test trend criterion evaluation."""
        criterion = TrendCriterion(allowed_directions=['bullish', 'neutral'])
        
        # Test allowed trend
        result = criterion.evaluate({'trend_direction': 'bullish', 'trend_strength': 0.7})
        self.assertEqual(result.result, CriteriaResult.PASS)
        self.assertEqual(result.score, 0.7)
        
        # Test disallowed trend
        result = criterion.evaluate({'trend_direction': 'bearish', 'trend_strength': 0.8})
        self.assertEqual(result.result, CriteriaResult.FAIL)
        self.assertEqual(result.score, 0.0)

    def test_criteria_manager_basic(self):
        """Test basic criteria manager functionality."""
        manager = CriteriaManager()
        
        # Test empty manager
        should_trade, score, message = manager.should_trade({})
        self.assertTrue(should_trade)
        self.assertEqual(score, 1.0)
        
        # Add a criterion
        manager.add_criterion(DeltaCriterion(target_range=(0.25, 0.75)))
        
        # Test with good delta
        should_trade, score, message = manager.should_trade({'delta': 0.5})
        self.assertTrue(should_trade)
        self.assertGreater(score, 0.8)
        
        # Test with bad delta
        should_trade, score, message = manager.should_trade({'delta': 0.1})
        self.assertFalse(should_trade)
        self.assertEqual(score, 0.0)

    def test_criteria_manager_multiple_criteria(self):
        """Test criteria manager with multiple criteria."""
        manager = CriteriaManager()
        manager.add_criterion(DeltaCriterion(target_range=(0.25, 0.75), weight=1.0))
        manager.add_criterion(VolatilityCriterion(max_volatility=0.5, weight=0.5))
        
        # Test with all criteria passing
        context = {'delta': 0.5, 'volatility': 0.3}
        should_trade, score, message = manager.should_trade(context)
        self.assertTrue(should_trade)
        self.assertGreater(score, 0.7)
        
        # Test with one criterion failing
        context = {'delta': 0.5, 'volatility': 0.6}
        should_trade, score, message = manager.should_trade(context)
        self.assertFalse(should_trade)
        self.assertEqual(score, 0.0)

    def test_criteria_presets(self):
        """Test predefined criteria presets."""
        # Test delta-only preset
        delta_only = CriteriaPresets.delta_only()
        should_trade, score, message = delta_only.should_trade({'delta': 0.5})
        self.assertTrue(should_trade)
        
        # Test conservative preset
        conservative = CriteriaPresets.conservative()
        context = {
            'delta': 0.4, 'dte': 30, 'market_regime': 'bullish_low_vol',
            'volatility': 0.2
        }
        should_trade, score, message = conservative.should_trade(context)
        self.assertTrue(should_trade)
        
        # Test aggressive preset
        aggressive = CriteriaPresets.aggressive()
        context = {'delta': 0.5, 'volatility': 0.4}
        should_trade, score, message = aggressive.should_trade(context)
        self.assertTrue(should_trade)
        
        # Test momentum-based preset
        momentum = CriteriaPresets.momentum_based()
        context = {
            'delta': 0.5, 'rsi': 60, 'trend_direction': 'bullish'
        }
        should_trade, score, message = momentum.should_trade(context)
        self.assertTrue(should_trade)

    def test_criteria_manager_remove_criterion(self):
        """Test removing criteria from manager."""
        manager = CriteriaManager()
        manager.add_criterion(DeltaCriterion(target_range=(0.25, 0.75)))
        manager.add_criterion(VolatilityCriterion(max_volatility=0.5))
        
        # Verify both criteria are present
        self.assertEqual(len(manager.criteria), 2)
        
        # Remove volatility criterion
        manager.remove_criterion("Volatility")
        self.assertEqual(len(manager.criteria), 1)
        self.assertEqual(manager.criteria[0].name, "Delta")
        
        # Test that only delta criterion is evaluated
        context = {'delta': 0.5, 'volatility': 0.6}
        should_trade, score, message = manager.should_trade(context)
        self.assertTrue(should_trade)  # Should pass because volatility criterion was removed

    def test_criteria_manager_weighted_scoring(self):
        """Test weighted scoring in criteria manager."""
        manager = CriteriaManager()
        manager.add_criterion(DeltaCriterion(target_range=(0.25, 0.75), weight=2.0))
        manager.add_criterion(VolatilityCriterion(max_volatility=0.5, weight=1.0))
        
        # Test with both criteria passing but different scores
        context = {'delta': 0.5, 'volatility': 0.4}
        should_trade, score, message = manager.should_trade(context)
        self.assertTrue(should_trade)
        
        # The weighted score should be: (delta_score * 2 + vol_score * 1) / 3
        # where delta_score and vol_score are both high since both criteria pass

    def test_criteria_evaluation_details(self):
        """Test that criteria evaluation provides detailed information."""
        criterion = DeltaCriterion(target_range=(0.25, 0.75))
        result = criterion.evaluate({'delta': 0.5})
        
        self.assertIsNotNone(result.details)
        self.assertIn('delta', result.details)
        self.assertIn('target_range', result.details)
        self.assertEqual(result.details['delta'], 0.5)
        self.assertEqual(result.details['target_range'], (0.25, 0.75))


if __name__ == "__main__":
    unittest.main() 