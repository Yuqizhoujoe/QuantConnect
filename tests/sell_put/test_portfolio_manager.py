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
    
    def test_update_portfolio_data(self):
        """Test portfolio data update."""
        algorithm = Mock()
        portfolio_config = {'max_stocks': 5}
        manager = PortfolioManager(algorithm, portfolio_config)
        
        # Create mock stock managers
        stock1 = Mock()
        stock2 = Mock()
        manager.stock_managers = {
            'AAPL': stock1,
            'MSFT': stock2
        }
        
        slice_data = Mock()
        
        manager.update_portfolio_data(slice_data)
        
        # Should update each stock manager
        stock1.update_data.assert_called_once_with(slice_data)
        stock2.update_data.assert_called_once_with(slice_data)
    
    def test_update_portfolio_performance(self):
        """Test portfolio performance update."""
        algorithm = Mock()
        algorithm.Portfolio.TotalPortfolioValue = 105000.0
        portfolio_config = {'max_stocks': 5}
        manager = PortfolioManager(algorithm, portfolio_config)
        
        # Set initial values
        manager.peak_portfolio_value = 100000.0
        manager._last_portfolio_value = 100000.0
        
        manager._update_portfolio_performance()
        
        # Should update peak value
        assert manager.peak_portfolio_value == 105000.0
        
        # Should add daily PnL
        assert len(manager.daily_portfolio_pnl) == 1
        assert manager.daily_portfolio_pnl[0] == 5000.0
    
    def test_check_portfolio_risk_limits_drawdown_exceeded(self):
        """Test portfolio risk limits when drawdown exceeded."""
        algorithm = Mock()
        algorithm.Portfolio.TotalPortfolioValue = 80000.0
        portfolio_config = {
            'max_stocks': 5,
            'max_drawdown': 0.15
        }
        manager = PortfolioManager(algorithm, portfolio_config)
        
        # Set peak value
        manager.peak_portfolio_value = 100000.0
        
        # Add some daily PnL data
        manager.daily_portfolio_pnl = [1000, -500, 800, -300] * 5  # 20 data points
        
        risk_exceeded = manager._check_portfolio_risk_limits()
        
        # Should return True (risk limits exceeded)
        assert risk_exceeded is True
    
    def test_check_portfolio_risk_limits_volatility_exceeded(self):
        """Test portfolio risk limits when volatility exceeded."""
        algorithm = Mock()
        algorithm.Portfolio.TotalPortfolioValue = 95000.0
        portfolio_config = {
            'max_stocks': 5,
            'max_portfolio_risk': 0.02
        }
        manager = PortfolioManager(algorithm, portfolio_config)
        
        # Set peak value
        manager.peak_portfolio_value = 100000.0
        
        # Add high volatility daily PnL data
        manager.daily_portfolio_pnl = [10000, -8000, 12000, -9000] * 5  # High volatility
        
        risk_exceeded = manager._check_portfolio_risk_limits()
        
        # Should return True (volatility exceeded)
        assert risk_exceeded is True
    
    def test_check_portfolio_risk_limits_normal(self):
        """Test portfolio risk limits under normal conditions."""
        algorithm = Mock()
        algorithm.Portfolio.TotalPortfolioValue = 95000.0
        portfolio_config = {
            'max_stocks': 5,
            'max_drawdown': 0.15,
            'max_portfolio_risk': 0.02
        }
        manager = PortfolioManager(algorithm, portfolio_config)
        
        # Set peak value
        manager.peak_portfolio_value = 100000.0
        
        # Add normal daily PnL data
        manager.daily_portfolio_pnl = [1000, -500, 800, -300] * 5  # Normal volatility
        
        risk_exceeded = manager._check_portfolio_risk_limits()
        
        # Should return False (risk limits not exceeded)
        assert risk_exceeded is False
    
    def test_manage_positions_close_positions(self):
        """Test position management with positions to close."""
        algorithm = Mock()
        portfolio_config = {'max_stocks': 5}
        manager = PortfolioManager(algorithm, portfolio_config)
        
        # Create mock stock managers
        stock1 = Mock()
        stock1.should_close_position.return_value = True
        
        stock2 = Mock()
        stock2.should_close_position.return_value = False
        
        manager.stock_managers = {
            'AAPL': stock1,
            'MSFT': stock2
        }
        
        manager.manage_positions()
        
        # Should close position for stock1
        stock1.close_position.assert_called_once()
        
        # Should not close position for stock2
        stock2.close_position.assert_not_called()
    
    def test_manage_positions_find_new_opportunities(self):
        """Test position management finding new opportunities."""
        algorithm = Mock()
        algorithm.Portfolio.TotalPortfolioValue = 100000.0
        portfolio_config = {'max_stocks': 5}
        manager = PortfolioManager(algorithm, portfolio_config)
        
        # Mock should_trade_portfolio to return True
        manager.should_trade_portfolio = Mock(return_value=True)
        
        # Create mock stock managers
        stock1 = Mock()
        stock1.should_close_position.return_value = False
        stock1.should_trade.return_value = True
        
        stock2 = Mock()
        stock2.should_close_position.return_value = False
        stock2.should_trade.return_value = False
        
        manager.stock_managers = {
            'AAPL': stock1,
            'MSFT': stock2
        }
        
        # Mock _find_best_trading_opportunity
        manager._find_best_trading_opportunity = Mock(return_value=stock1)
        
        manager.manage_positions()
        
        # Should find and enter position for stock1
        stock1.find_and_enter_position.assert_called_once()
    
    def test_find_best_trading_opportunity(self):
        """Test finding the best trading opportunity."""
        algorithm = Mock()
        portfolio_config = {'max_stocks': 5}
        manager = PortfolioManager(algorithm, portfolio_config)
        
        # Create mock stock managers
        stock1 = Mock()
        stock1.should_trade.return_value = True
        stock1.weight = 0.3
        
        stock2 = Mock()
        stock2.should_trade.return_value = True
        stock2.weight = 0.5
        
        stock3 = Mock()
        stock3.should_trade.return_value = False
        
        manager.stock_managers = {
            'AAPL': stock1,
            'MSFT': stock2,
            'GOOGL': stock3
        }
        
        # Mock market analyzer
        stock1.market_analyzer = Mock()
        stock1.market_analyzer.analyze_market_conditions.return_value = {
            'market_regime': 'bullish_low_vol'
        }
        
        stock2.market_analyzer = Mock()
        stock2.market_analyzer.analyze_market_conditions.return_value = {
            'market_regime': 'bullish_normal_vol'
        }
        
        best_stock = manager._find_best_trading_opportunity()
        
        # Should return stock2 (higher weight and better market conditions)
        assert best_stock == stock2
    
    def test_calculate_opportunity_score(self):
        """Test opportunity score calculation."""
        algorithm = Mock()
        portfolio_config = {'max_stocks': 5}
        manager = PortfolioManager(algorithm, portfolio_config)
        
        # Create mock stock manager
        stock_manager = Mock()
        stock_manager.weight = 0.4
        stock_manager.price_history = [100, 101, 102, 103, 104]
        
        # Mock market analyzer
        stock_manager.market_analyzer = Mock()
        stock_manager.market_analyzer.analyze_market_conditions.return_value = {
            'market_regime': 'bullish_low_vol',
            'volatility': {'current': 0.15}
        }
        
        score = manager._calculate_opportunity_score(stock_manager)
        
        # Should calculate a positive score
        assert score > 0
        assert isinstance(score, float)
    
    def test_get_portfolio_metrics(self):
        """Test portfolio metrics retrieval."""
        algorithm = Mock()
        algorithm.Portfolio.TotalPortfolioValue = 105000.0
        portfolio_config = {'max_stocks': 5}
        manager = PortfolioManager(algorithm, portfolio_config)
        
        # Set some test data
        manager.total_trades = 10
        manager.portfolio_pnl = 5000.0
        manager.peak_portfolio_value = 100000.0
        
        # Create mock stock managers
        stock1 = Mock()
        stock1.get_performance_metrics.return_value = {
            'ticker': 'AAPL',
            'trade_count': 5,
            'profit_loss': 2000.0
        }
        
        manager.stock_managers = {
            'AAPL': stock1
        }
        
        metrics = manager.get_portfolio_metrics()
        
        # Should return comprehensive metrics
        assert metrics['total_trades'] == 10
        assert metrics['portfolio_pnl'] == 5000.0
        assert metrics['current_value'] == 105000.0
        assert metrics['peak_value'] == 100000.0
        assert metrics['drawdown'] == -0.05  # (100000 - 105000) / 100000
        assert 'stock_metrics' in metrics
        assert 'AAPL' in metrics['stock_metrics']
    
    def test_get_correlation_matrix(self):
        """Test correlation matrix retrieval."""
        algorithm = Mock()
        portfolio_config = {'max_stocks': 5}
        manager = PortfolioManager(algorithm, portfolio_config)
        
        matrix = manager.get_correlation_matrix()
        
        # Should return empty dict (simplified implementation)
        assert matrix == {}
    
    def test_adjust_allocations(self):
        """Test allocation adjustments."""
        algorithm = Mock()
        portfolio_config = {'max_stocks': 5}
        manager = PortfolioManager(algorithm, portfolio_config)
        
        # Should not raise an exception
        manager.adjust_allocations() 