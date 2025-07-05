"""
Tests for the RiskManager class.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import numpy as np
from core.risk_manager import RiskManager


class TestRiskManager:
    """Test cases for RiskManager."""
    
    def test_initialization(self):
        """Test RiskManager initialization."""
        algorithm = Mock()
        ticker = "AAPL"
        
        manager = RiskManager(algorithm, ticker)
        
        assert manager.algorithm == algorithm
        assert manager.ticker == ticker
        assert manager.max_portfolio_risk == 0.02
        assert manager.max_drawdown == 0.15
        assert manager.volatility_lookback == 20
        assert manager.volatility_threshold == 0.4
    
    def test_calculate_position_size_kelly_criterion(self):
        """Test position size calculation using Kelly Criterion."""
        algorithm = Mock()
        algorithm.Portfolio.TotalPortfolioValue = 100000.0
        algorithm.daily_pnl = [1000, -500, 800, -300, 1200]  # Some historical PnL
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        # Mock contract
        contract = Mock()
        contract.Strike = 150.0
        
        underlying_price = 160.0
        
        # Mock historical data methods
        manager.get_historical_win_rate = Mock(return_value=0.6)
        manager.get_average_win = Mock(return_value=1000.0)
        manager.get_average_loss = Mock(return_value=400.0)
        manager.get_volatility_adjustment = Mock(return_value=1.0)
        manager.calculate_portfolio_risk_size = Mock(return_value=10)
        manager.calculate_margin_based_size = Mock(return_value=15)
        
        size = manager.calculate_position_size(contract, underlying_price)
        
        # Should return a positive integer
        assert isinstance(size, int)
        assert size >= 1
        assert size <= 10  # Should be limited by portfolio risk size
    
    def test_calculate_position_size_conservative_fallback(self):
        """Test position size calculation with conservative fallback."""
        algorithm = Mock()
        algorithm.Portfolio.TotalPortfolioValue = 100000.0
        algorithm.max_position_size = 0.20
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        # Mock contract
        contract = Mock()
        contract.Strike = 150.0
        
        underlying_price = 160.0
        
        # Mock no historical data (avg_loss = 0)
        manager.get_average_loss = Mock(return_value=0)
        
        size = manager.calculate_position_size(contract, underlying_price)
        
        # Should use conservative sizing
        assert isinstance(size, int)
        assert size >= 1
    
    def test_calculate_portfolio_risk_size(self):
        """Test portfolio risk-based position sizing."""
        algorithm = Mock()
        algorithm.Portfolio.TotalPortfolioValue = 100000.0
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        # Mock contract
        contract = Mock()
        contract.Strike = 150.0
        
        underlying_price = 160.0
        
        # Mock max loss calculation
        manager.calculate_max_loss = Mock(return_value=5000.0)  # $5000 max loss per contract
        
        size = manager.calculate_portfolio_risk_size(contract, underlying_price)
        
        # Max risk amount = 100000 * 0.02 = 2000
        # Number of contracts = 2000 / 5000 = 0.4, should round to 1
        assert size == 1
    
    def test_calculate_portfolio_risk_size_large_max_loss(self):
        """Test portfolio risk sizing with large max loss."""
        algorithm = Mock()
        algorithm.Portfolio.TotalPortfolioValue = 100000.0
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        # Mock contract
        contract = Mock()
        contract.Strike = 150.0
        
        underlying_price = 160.0
        
        # Mock large max loss
        manager.calculate_max_loss = Mock(return_value=10000.0)  # $10000 max loss per contract
        
        size = manager.calculate_portfolio_risk_size(contract, underlying_price)
        
        # Max risk amount = 100000 * 0.02 = 2000
        # Number of contracts = 2000 / 10000 = 0.2, should round to 1
        assert size == 1
    
    def test_calculate_max_loss(self):
        """Test maximum loss calculation."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        # Mock contract
        contract = Mock()
        contract.Strike = 150.0
        
        underlying_price = 160.0
        
        max_loss = manager.calculate_max_loss(contract, underlying_price)
        
        # Worst case price = 160 * 0.5 = 80
        # Intrinsic value = max(0, 150 - 80) = 70
        # Loss per contract = 70 * 100 = 7000
        expected_loss = max(0, contract.Strike - underlying_price * 0.5) * 100
        assert max_loss == expected_loss
    
    def test_calculate_max_loss_zero_strike(self):
        """Test maximum loss calculation with zero strike."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        # Mock contract with zero strike
        contract = Mock()
        contract.Strike = 0
        
        underlying_price = 160.0
        
        max_loss = manager.calculate_max_loss(contract, underlying_price)
        
        # Should handle zero strike gracefully
        assert max_loss == 0
    
    def test_calculate_margin_based_size(self):
        """Test margin-based position sizing."""
        algorithm = Mock()
        algorithm.Portfolio.MarginRemaining = 50000.0
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        # Mock contract
        contract = Mock()
        contract.Strike = 150.0
        
        size = manager.calculate_margin_based_size(contract)
        
        # Margin requirement = 150 * 100 * 0.2 = 3000
        # Number of contracts = 50000 / 3000 = 16.67, should round to 16
        expected_size = int(50000 / (contract.Strike * 100 * 0.2))
        assert size == expected_size
    
    def test_calculate_margin_based_size_low_margin(self):
        """Test margin-based sizing with low margin."""
        algorithm = Mock()
        algorithm.Portfolio.MarginRemaining = 1000.0  # Low margin
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        # Mock contract
        contract = Mock()
        contract.Strike = 150.0
        
        size = manager.calculate_margin_based_size(contract)
        
        # Should return 0 or 1 for very low margin
        assert size <= 1
    
    def test_calculate_conservative_position_size(self):
        """Test conservative position sizing."""
        algorithm = Mock()
        algorithm.Portfolio.TotalPortfolioValue = 100000.0
        algorithm.max_position_size = 0.20
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        # Mock contract
        contract = Mock()
        contract.Strike = 150.0
        
        size = manager.calculate_conservative_position_size(contract)
        
        # Max position value = 100000 * 0.20 = 20000
        # Margin requirement = 150 * 100 * 0.2 = 3000
        # Number of contracts = 20000 / 3000 = 6.67, should round to 6
        expected_size = max(1, int(100000 * 0.20 / (contract.Strike * 100 * 0.2)))
        assert size == expected_size
    
    def test_get_volatility_adjustment_insufficient_data(self):
        """Test volatility adjustment with insufficient data."""
        algorithm = Mock()
        algorithm.daily_pnl = [1000, 500]  # Only 2 data points
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        adjustment = manager.get_volatility_adjustment()
        
        # Should return default factor
        assert adjustment == 1.0
    
    def test_get_volatility_adjustment_low_volatility(self):
        """Test volatility adjustment for low volatility."""
        algorithm = Mock()
        algorithm.daily_pnl = [1000, 1100, 1050, 1150, 1080] * 4  # Low volatility data
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        adjustment = manager.get_volatility_adjustment()
        
        # Should increase position size for low volatility
        assert adjustment > 1.0
        assert adjustment <= 1.2
    
    def test_get_volatility_adjustment_high_volatility(self):
        """Test volatility adjustment for high volatility."""
        algorithm = Mock()
        algorithm.daily_pnl = [1000, 500, 1500, 200, 1800] * 4  # High volatility data
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        adjustment = manager.get_volatility_adjustment()
        
        # Should decrease position size for high volatility
        assert adjustment < 1.0
        assert adjustment >= 0.7
    
    def test_get_historical_win_rate(self):
        """Test historical win rate calculation."""
        algorithm = Mock()
        algorithm.trades = [
            {'pnl': 1000}, {'pnl': -500}, {'pnl': 800}, {'pnl': -300}, {'pnl': 1200}
        ]
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        win_rate = manager.get_historical_win_rate()
        
        # 3 wins out of 5 trades = 60%
        assert win_rate == 0.6
    
    def test_get_historical_win_rate_no_trades(self):
        """Test historical win rate with no trades."""
        algorithm = Mock()
        algorithm.trades = []
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        win_rate = manager.get_historical_win_rate()
        
        # Should return default win rate
        assert win_rate == 0.5
    
    def test_get_average_win(self):
        """Test average win calculation."""
        algorithm = Mock()
        algorithm.trades = [
            {'pnl': 1000}, {'pnl': -500}, {'pnl': 800}, {'pnl': -300}, {'pnl': 1200}
        ]
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        avg_win = manager.get_average_win()
        
        # Average of 1000, 800, 1200 = 1000
        assert avg_win == 1000.0
    
    def test_get_average_win_no_wins(self):
        """Test average win with no winning trades."""
        algorithm = Mock()
        algorithm.trades = [
            {'pnl': -500}, {'pnl': -300}, {'pnl': -200}
        ]
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        avg_win = manager.get_average_win()
        
        # Should return 0 if no wins
        assert avg_win == 0.0
    
    def test_get_average_loss(self):
        """Test average loss calculation."""
        algorithm = Mock()
        algorithm.trades = [
            {'pnl': 1000}, {'pnl': -500}, {'pnl': 800}, {'pnl': -300}, {'pnl': 1200}
        ]
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        avg_loss = manager.get_average_loss()
        
        # Average of -500, -300 = -400 (absolute value)
        assert avg_loss == 400.0
    
    def test_get_average_loss_no_losses(self):
        """Test average loss with no losing trades."""
        algorithm = Mock()
        algorithm.trades = [
            {'pnl': 1000}, {'pnl': 800}, {'pnl': 1200}
        ]
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        avg_loss = manager.get_average_loss()
        
        # Should return 0 if no losses
        assert avg_loss == 0.0
    
    def test_should_stop_trading_drawdown_exceeded(self):
        """Test trading stop when drawdown exceeded."""
        algorithm = Mock()
        algorithm.Portfolio.TotalPortfolioValue = 85000.0
        algorithm.peak_portfolio_value = 100000.0
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        should_stop = manager.should_stop_trading()
        
        # Drawdown = (100000 - 85000) / 100000 = 15%
        # Should stop when drawdown >= max_drawdown (15%)
        assert should_stop is True
    
    def test_should_stop_trading_drawdown_not_exceeded(self):
        """Test trading continue when drawdown not exceeded."""
        algorithm = Mock()
        algorithm.Portfolio.TotalPortfolioValue = 90000.0
        algorithm.peak_portfolio_value = 100000.0
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        should_stop = manager.should_stop_trading()
        
        # Drawdown = (100000 - 90000) / 100000 = 10%
        # Should continue when drawdown < max_drawdown (15%)
        assert should_stop is False
    
    def test_should_stop_trading_consecutive_losses(self):
        """Test trading stop when consecutive losses exceeded."""
        algorithm = Mock()
        algorithm.Portfolio.TotalPortfolioValue = 95000.0
        algorithm.peak_portfolio_value = 100000.0
        
        # Mock recent losing trades
        algorithm.trades = [
            {'pnl': -1000}, {'pnl': -800}, {'pnl': -1200}, {'pnl': -600}
        ]
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        should_stop = manager.should_stop_trading()
        
        # Should stop after 4 consecutive losses
        assert should_stop is True
    
    def test_should_stop_trading_volatility_exceeded(self):
        """Test trading stop when volatility exceeded."""
        algorithm = Mock()
        algorithm.Portfolio.TotalPortfolioValue = 95000.0
        algorithm.peak_portfolio_value = 100000.0
        algorithm.daily_pnl = [1000, -2000, 1500, -3000, 800] * 4  # High volatility
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        should_stop = manager.should_stop_trading()
        
        # Should stop when volatility is too high
        assert should_stop is True
    
    def test_get_risk_metrics(self):
        """Test risk metrics calculation."""
        algorithm = Mock()
        algorithm.trades = [
            {'pnl': 1000}, {'pnl': -500}, {'pnl': 800}, {'pnl': -300}, {'pnl': 1200}
        ]
        algorithm.daily_pnl = [1000, 1100, 1050, 1150, 1080] * 4
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        metrics = manager.get_risk_metrics()
        
        assert 'win_rate' in metrics
        assert 'volatility' in metrics
        assert metrics['win_rate'] == 0.6  # 3 wins out of 5
        assert isinstance(metrics['volatility'], float)
    
    def test_get_risk_metrics_no_data(self):
        """Test risk metrics with no data."""
        algorithm = Mock()
        algorithm.trades = []
        algorithm.daily_pnl = []
        
        ticker = "AAPL"
        manager = RiskManager(algorithm, ticker)
        
        metrics = manager.get_risk_metrics()
        
        assert 'win_rate' in metrics
        assert 'volatility' in metrics
        assert metrics['win_rate'] == 0.5  # Default win rate
        assert metrics['volatility'] == 0.0  # Default volatility 