"""
Tests for the MarketAnalyzer class.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import numpy as np
from core.market_analyzer import MarketAnalyzer


class TestMarketAnalyzer:
    """Test cases for MarketAnalyzer."""
    
    def test_initialization(self):
        """Test MarketAnalyzer initialization."""
        algorithm = Mock()
        ticker = "AAPL"
        
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        assert analyzer.algorithm == algorithm
        assert analyzer.ticker == ticker
        assert analyzer.volatility_lookback == 20
        assert analyzer.rsi_period == 14
        assert analyzer.moving_average_period == 50
        assert analyzer.price_history == []
        assert analyzer.volatility_history == []
    
    def test_update_price_history(self):
        """Test price history update with memory management."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        # Add prices to exceed lookback
        for i in range(25):
            analyzer.update_price_history(float(i))
        
        # Should keep only the last 20 prices
        assert len(analyzer.price_history) == 20
        assert analyzer.price_history[0] == 5.0  # First price after trimming
        assert analyzer.price_history[-1] == 24.0  # Last price
    
    def test_analyze_market_conditions_insufficient_data(self):
        """Test market analysis with insufficient data."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        # Add some prices but not enough for full analysis
        for i in range(30):
            analyzer.update_price_history(float(i))
        
        result = analyzer.analyze_market_conditions(30.0)
        
        # Should return default analysis
        assert 'trend' in result
        assert 'volatility' in result
        assert 'rsi' in result
        assert 'support_resistance' in result
        assert 'market_regime' in result
        assert 'option_premium_richness' in result
    
    def test_analyze_market_conditions_sufficient_data(self):
        """Test market analysis with sufficient data."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        # Add enough prices for full analysis
        for i in range(60):
            analyzer.update_price_history(100.0 + i)  # Upward trend
        
        result = analyzer.analyze_market_conditions(160.0)
        
        # Should return full analysis
        assert 'trend' in result
        assert 'volatility' in result
        assert 'rsi' in result
        assert 'support_resistance' in result
        assert 'market_regime' in result
        assert 'option_premium_richness' in result
    
    def test_analyze_trend_bullish(self):
        """Test trend analysis for bullish market."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        # Create bullish price data (current price > MA * 1.02)
        base_price = 100.0
        for i in range(50):
            analyzer.update_price_history(base_price + i * 0.5)  # Steady upward trend
        
        # Current price is significantly above MA
        current_price = base_price + 50 * 0.5 + 10  # 10 points above trend
        trend = analyzer.analyze_trend()
        
        assert trend == 'bullish'
    
    def test_analyze_trend_bearish(self):
        """Test trend analysis for bearish market."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        # Create bearish price data (current price < MA * 0.98)
        base_price = 100.0
        for i in range(50):
            analyzer.update_price_history(base_price - i * 0.5)  # Steady downward trend
        
        # Current price is significantly below MA
        current_price = base_price - 50 * 0.5 - 10  # 10 points below trend
        trend = analyzer.analyze_trend()
        
        assert trend == 'bearish'
    
    def test_analyze_trend_neutral(self):
        """Test trend analysis for neutral market."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        # Create neutral price data (current price within 2% of MA)
        base_price = 100.0
        for i in range(50):
            analyzer.update_price_history(base_price + np.sin(i * 0.1) * 2)  # Oscillating around base
        
        trend = analyzer.analyze_trend()
        
        assert trend == 'neutral'
    
    def test_analyze_trend_insufficient_data(self):
        """Test trend analysis with insufficient data."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        # Add some prices but not enough for MA calculation
        for i in range(30):
            analyzer.update_price_history(float(i))
        
        trend = analyzer.analyze_trend()
        
        assert trend == 'neutral'
    
    def test_analyze_volatility_insufficient_data(self):
        """Test volatility analysis with insufficient data."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        # Add some prices but not enough for volatility calculation
        for i in range(5):
            analyzer.update_price_history(float(i))
        
        result = analyzer.analyze_volatility()
        
        assert result['current'] == 0.2
        assert result['historical'] == 0.2
        assert result['regime'] == 'normal'
    
    def test_analyze_volatility_normal_regime(self):
        """Test volatility analysis for normal regime."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        # Create price data with normal volatility
        base_price = 100.0
        for i in range(20):
            # Add some random variation around base price
            price = base_price + np.random.normal(0, 2)
            analyzer.update_price_history(price)
        
        result = analyzer.analyze_volatility()
        
        assert 'current' in result
        assert 'historical' in result
        assert 'regime' in result
        assert result['regime'] in ['high', 'low', 'normal']
    
    def test_analyze_volatility_high_regime(self):
        """Test volatility analysis for high volatility regime."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        # Create price data with high volatility
        base_price = 100.0
        for i in range(20):
            if i < 15:
                # Normal volatility for historical
                price = base_price + np.random.normal(0, 2)
            else:
                # High volatility for current (last 5 days)
                price = base_price + np.random.normal(0, 8)
            analyzer.update_price_history(price)
        
        result = analyzer.analyze_volatility()
        
        # Should detect high volatility regime
        assert result['regime'] == 'high'
    
    def test_calculate_rsi_insufficient_data(self):
        """Test RSI calculation with insufficient data."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        # Add some prices but not enough for RSI
        for i in range(10):
            analyzer.update_price_history(float(i))
        
        rsi = analyzer.calculate_rsi()
        
        assert rsi == 50.0  # Default neutral RSI
    
    def test_calculate_rsi_all_gains(self):
        """Test RSI calculation with all gains."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        # Create price data with all gains
        base_price = 100.0
        for i in range(20):
            analyzer.update_price_history(base_price + i)
        
        rsi = analyzer.calculate_rsi()
        
        assert rsi == 100.0  # All gains, no losses
    
    def test_calculate_rsi_mixed_moves(self):
        """Test RSI calculation with mixed price moves."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        # Create price data with mixed moves
        prices = [100, 102, 101, 103, 102, 104, 103, 105, 104, 106, 105, 107, 106, 108, 107]
        for price in prices:
            analyzer.update_price_history(price)
        
        rsi = analyzer.calculate_rsi()
        
        # RSI should be calculated and in reasonable range
        assert 0 <= rsi <= 100
    
    def test_find_support_resistance(self):
        """Test support and resistance level finding."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        # Create price data with clear levels
        prices = [100, 102, 101, 103, 102, 104, 103, 105, 104, 106, 105, 107, 106, 108, 107]
        for price in prices:
            analyzer.update_price_history(price)
        
        result = analyzer.find_support_resistance()
        
        assert 'support' in result
        assert 'resistance' in result
        assert 'current_price' in result
        assert result['current_price'] == 107.0
    
    def test_determine_market_regime_bullish_low_vol(self):
        """Test market regime determination for bullish low vol."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        # Mock trend and volatility analysis
        analyzer.analyze_trend = Mock(return_value='bullish')
        analyzer.analyze_volatility = Mock(return_value={'regime': 'low'})
        
        regime = analyzer.determine_market_regime()
        
        assert regime == 'bullish_low_vol'
    
    def test_determine_market_regime_bearish_high_vol(self):
        """Test market regime determination for bearish high vol."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        # Mock trend and volatility analysis
        analyzer.analyze_trend = Mock(return_value='bearish')
        analyzer.analyze_volatility = Mock(return_value={'regime': 'high'})
        
        regime = analyzer.determine_market_regime()
        
        assert regime == 'bearish_high_vol'
    
    def test_determine_market_regime_neutral(self):
        """Test market regime determination for neutral market."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        # Mock trend and volatility analysis
        analyzer.analyze_trend = Mock(return_value='neutral')
        analyzer.analyze_volatility = Mock(return_value={'regime': 'normal'})
        
        regime = analyzer.determine_market_regime()
        
        assert regime == 'neutral_normal_vol'
    
    def test_analyze_option_premiums_no_chain(self):
        """Test option premium analysis with no chain."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        result = analyzer.analyze_option_premiums()
        
        assert 'richness' in result
        assert 'recommendation' in result
        assert result['richness'] == 'neutral'
        assert result['recommendation'] == 'normal'
    
    def test_get_optimal_delta_range_bullish_low_vol(self):
        """Test optimal delta range for bullish low vol market."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        market_analysis = {'market_regime': 'bullish_low_vol'}
        
        delta_range = analyzer.get_optimal_delta_range(market_analysis)
        
        assert len(delta_range) == 2
        assert 0.2 <= delta_range[0] <= 0.4  # Lower bound
        assert 0.6 <= delta_range[1] <= 0.8  # Upper bound
    
    def test_get_optimal_delta_range_bearish_high_vol(self):
        """Test optimal delta range for bearish high vol market."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        market_analysis = {'market_regime': 'bearish_high_vol'}
        
        delta_range = analyzer.get_optimal_delta_range(market_analysis)
        
        assert len(delta_range) == 2
        assert 0.1 <= delta_range[0] <= 0.3  # Lower bound
        assert 0.4 <= delta_range[1] <= 0.6  # Upper bound
    
    def test_get_optimal_dte_range_bullish_low_vol(self):
        """Test optimal DTE range for bullish low vol market."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        market_analysis = {'market_regime': 'bullish_low_vol'}
        
        dte_range = analyzer.get_optimal_dte_range(market_analysis)
        
        assert len(dte_range) == 2
        assert 30 <= dte_range[0] <= 45  # Lower bound
        assert 60 <= dte_range[1] <= 90  # Upper bound
    
    def test_get_optimal_dte_range_bearish_high_vol(self):
        """Test optimal DTE range for bearish high vol market."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        market_analysis = {'market_regime': 'bearish_high_vol'}
        
        dte_range = analyzer.get_optimal_dte_range(market_analysis)
        
        assert len(dte_range) == 2
        assert 7 <= dte_range[0] <= 14  # Lower bound
        assert 21 <= dte_range[1] <= 30  # Upper bound
    
    def test_should_avoid_trading_bearish_high_vol(self):
        """Test trading avoidance for bearish high vol market."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        market_analysis = {'market_regime': 'bearish_high_vol'}
        
        should_avoid = analyzer.should_avoid_trading(market_analysis)
        
        assert should_avoid is True
    
    def test_should_avoid_trading_bullish_low_vol(self):
        """Test trading allowance for bullish low vol market."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        market_analysis = {'market_regime': 'bullish_low_vol'}
        
        should_avoid = analyzer.should_avoid_trading(market_analysis)
        
        assert should_avoid is False
    
    def test_get_default_analysis(self):
        """Test default analysis when insufficient data."""
        algorithm = Mock()
        ticker = "AAPL"
        analyzer = MarketAnalyzer(algorithm, ticker)
        
        result = analyzer.get_default_analysis()
        
        assert 'trend' in result
        assert 'volatility' in result
        assert 'rsi' in result
        assert 'support_resistance' in result
        assert 'market_regime' in result
        assert 'option_premium_richness' in result
        assert result['trend'] == 'neutral'
        assert result['volatility']['regime'] == 'normal'
        assert result['rsi'] == 50.0
        assert result['market_regime'] == 'neutral_normal_vol' 