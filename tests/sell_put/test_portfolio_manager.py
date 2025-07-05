"""
Tests for the PortfolioManager class.
"""

import pytest
from unittest.mock import Mock, MagicMock
from strategies.sell_put.portfolio_manager import PortfolioManager


class TestPortfolioManager:
    """Test cases for PortfolioManager."""
    
    def test_initialization(self):
        """Test PortfolioManager initialization."""
        algorithm = Mock()
        portfolio_config = {
            'max_stocks': 5,
            'max_portfolio_risk': 0.02,
            'max_drawdown': 0.15,
            'correlation_threshold': 0.7
        }
        
        manager = PortfolioManager(algorithm, portfolio_config)
        
        assert manager.algorithm == algorithm
        assert manager.config == portfolio_config
        assert manager.max_stocks == 5
        assert manager.max_portfolio_risk == 0.02
        assert manager.max_drawdown == 0.15
        assert manager.correlation_threshold == 0.7
        assert manager.stock_managers == {}
    
    def test_initialize_stocks(self):
        """Test stock initialization."""
        algorithm = Mock()
        portfolio_config = {'max_stocks': 5}
        manager = PortfolioManager(algorithm, portfolio_config)
        
        stocks_config = [
            {'ticker': 'AAPL', 'enabled': True},
            {'ticker': 'MSFT', 'enabled': False},
            {'ticker': 'GOOGL', 'enabled': True}
        ]
        
        manager.initialize_stocks(stocks_config)
        
        # Should only initialize enabled stocks
        assert len(manager.stock_managers) == 2
        assert 'AAPL' in manager.stock_managers
        assert 'GOOGL' in manager.stock_managers
        assert 'MSFT' not in manager.stock_managers
    
    def test_should_trade_portfolio(self):
        """Test portfolio trading decision logic."""
        algorithm = Mock()
        algorithm.Portfolio.TotalPortfolioValue = 100000
        portfolio_config = {
            'max_stocks': 2,
            'max_portfolio_risk': 0.02,
            'max_drawdown': 0.15
        }
        manager = PortfolioManager(algorithm, portfolio_config)
        
        # Test with no open positions
        assert manager.should_trade_portfolio() is True
        
        # Test with too many open positions
        manager.stock_managers = {
            'AAPL': Mock(),
            'MSFT': Mock(),
            'GOOGL': Mock()
        }
        # Mock that all have open positions
        for stock_manager in manager.stock_managers.values():
            stock_manager.current_contract = Mock()
            stock_manager.current_contract.Symbol = Mock()
        
        algorithm.Portfolio = Mock()
        algorithm.Portfolio.__getitem__ = Mock(return_value=Mock(Invested=True))
        
        assert manager.should_trade_portfolio() is False
    
    def test_count_open_positions(self):
        """Test counting open positions."""
        algorithm = Mock()
        portfolio_config = {'max_stocks': 5}
        manager = PortfolioManager(algorithm, portfolio_config)
        
        # Create mock stock managers
        stock1 = Mock()
        stock1.current_contract = Mock()
        stock1.current_contract.Symbol = Mock()
        
        stock2 = Mock()
        stock2.current_contract = None
        
        stock3 = Mock()
        stock3.current_contract = Mock()
        stock3.current_contract.Symbol = Mock()
        
        manager.stock_managers = {
            'AAPL': stock1,
            'MSFT': stock2,
            'GOOGL': stock3
        }
        
        # Mock portfolio positions
        algorithm.Portfolio = Mock()
        algorithm.Portfolio.__getitem__ = Mock(side_effect=lambda x: Mock(Invested=True))
        
        count = manager._count_open_positions()
        assert count == 2  # Only stock1 and stock3 have contracts 