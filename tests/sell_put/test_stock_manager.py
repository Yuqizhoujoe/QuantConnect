"""
Tests for the StockManager class.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date
from strategies.sell_put.stock_manager import StockManager


class TestStockManager:
    """Test cases for StockManager."""
    
    def test_initialization(self):
        """Test StockManager initialization."""
        algorithm = Mock()
        ticker = "AAPL"
        stock_config = {
            'target_delta_min': 0.25,
            'target_delta_max': 0.75,
            'max_position_size': 0.20,
            'option_frequency': 'monthly',
            'weight': 0.25,
            'enabled': True
        }
        
        manager = StockManager(algorithm, ticker, stock_config)
        
        assert manager.algorithm == algorithm
        assert manager.ticker == ticker
        assert manager.config == stock_config
        assert manager.target_delta_min == 0.25
        assert manager.target_delta_max == 0.75
        assert manager.max_position_size == 0.20
        assert manager.option_frequency == 'monthly'
        assert manager.weight == 0.25
        assert manager.enabled is True
        assert manager.current_contract is None
        assert manager.trade_count == 0
        assert manager.profit_loss == 0.0
        assert manager.trades == []
        assert manager.daily_pnl == []
        assert manager.price_history == []
        assert manager.volatility_history == []
        assert manager.returns_history == []
    
    def test_setup_stock_parameters_defaults(self):
        """Test stock parameter setup with default values."""
        algorithm = Mock()
        ticker = "AAPL"
        stock_config = {}  # Empty config to test defaults
        
        manager = StockManager(algorithm, ticker, stock_config)
        
        assert manager.target_delta_min == 0.25  # Default value
        assert manager.target_delta_max == 0.75  # Default value
        assert manager.max_position_size == 0.20  # Default value
        assert manager.option_frequency == 'monthly'  # Default value
        assert manager.weight == 0.25  # Default value
        assert manager.enabled is True  # Default value
    
    def test_update_data_enabled(self):
        """Test data update when stock is enabled."""
        algorithm = Mock()
        ticker = "AAPL"
        stock_config = {'enabled': True}
        manager = StockManager(algorithm, ticker, stock_config)
        
        slice_data = Mock()
        slice_data.Equity = {ticker: Mock(Price=150.0)}
        
        manager.update_data(slice_data)
        
        # Verify data handler was updated
        manager.data_handler.update_data.assert_called_once_with(slice_data)
        # Verify price history was updated
        assert manager.price_history == [150.0]
    
    def test_update_data_disabled(self):
        """Test data update when stock is disabled."""
        algorithm = Mock()
        ticker = "AAPL"
        stock_config = {'enabled': False}
        manager = StockManager(algorithm, ticker, stock_config)
        
        slice_data = Mock()
        slice_data.Equity = {ticker: Mock(Price=150.0)}
        
        manager.update_data(slice_data)
        
        # Verify data handler was NOT updated
        manager.data_handler.update_data.assert_not_called()
        # Verify price history was NOT updated
        assert manager.price_history == []
    
    def test_update_price_history(self):
        """Test price history update with memory management."""
        algorithm = Mock()
        ticker = "AAPL"
        stock_config = {}
        manager = StockManager(algorithm, ticker, stock_config)
        
        # Add prices to exceed max history
        for i in range(110):
            manager._update_price_history(float(i))
        
        # Should keep only the last 100 prices
        assert len(manager.price_history) == 100
        assert manager.price_history[0] == 10.0  # First price after trimming
        assert manager.price_history[-1] == 109.0  # Last price
    
    def test_should_trade_basic_conditions(self):
        """Test basic trading conditions."""
        algorithm = Mock()
        algorithm.Time.date.return_value = date(2023, 1, 1)
        algorithm.Portfolio = Mock()
        algorithm.Portfolio.__getitem__ = Mock(return_value=Mock(Quantity=0))
        
        ticker = "AAPL"
        stock_config = {'enabled': True}
        manager = StockManager(algorithm, ticker, stock_config)
        
        # Test with no open position and no underlying ownership
        assert manager.should_trade() is True
    
    def test_should_trade_disabled(self):
        """Test trading when stock is disabled."""
        algorithm = Mock()
        ticker = "AAPL"
        stock_config = {'enabled': False}
        manager = StockManager(algorithm, ticker, stock_config)
        
        assert manager.should_trade() is False
    
    def test_should_trade_with_open_position(self):
        """Test trading when there's an open position."""
        algorithm = Mock()
        algorithm.Time.date.return_value = date(2023, 1, 1)
        algorithm.Portfolio = Mock()
        algorithm.Portfolio.__getitem__ = Mock(return_value=Mock(Quantity=0))
        
        ticker = "AAPL"
        stock_config = {'enabled': True}
        manager = StockManager(algorithm, ticker, stock_config)
        
        # Mock open position
        manager.current_contract = Mock()
        manager.current_contract.Symbol = Mock()
        algorithm.Portfolio.__getitem__.return_value = Mock(Invested=True)
        
        assert manager.should_trade() is False
    
    def test_should_trade_already_traded_today(self):
        """Test trading when already traded today."""
        algorithm = Mock()
        algorithm.Time.date.return_value = date(2023, 1, 1)
        algorithm.Portfolio = Mock()
        algorithm.Portfolio.__getitem__ = Mock(return_value=Mock(Quantity=0))
        
        ticker = "AAPL"
        stock_config = {'enabled': True}
        manager = StockManager(algorithm, ticker, stock_config)
        
        # Mock that we already traded today
        manager.last_trade_date = date(2023, 1, 1)
        
        assert manager.should_trade() is False
    
    def test_should_trade_owns_underlying(self):
        """Test trading when owning the underlying."""
        algorithm = Mock()
        algorithm.Time.date.return_value = date(2023, 1, 1)
        algorithm.Portfolio = Mock()
        algorithm.Portfolio.__getitem__ = Mock(return_value=Mock(Quantity=100))  # Owns underlying
        
        ticker = "AAPL"
        stock_config = {'enabled': True}
        manager = StockManager(algorithm, ticker, stock_config)
        
        assert manager.should_trade() is False
    
    def test_should_trade_risk_manager_stop(self):
        """Test trading when risk manager stops trading."""
        algorithm = Mock()
        algorithm.Time.date.return_value = date(2023, 1, 1)
        algorithm.Portfolio = Mock()
        algorithm.Portfolio.__getitem__ = Mock(return_value=Mock(Quantity=0))
        
        ticker = "AAPL"
        stock_config = {'enabled': True}
        manager = StockManager(algorithm, ticker, stock_config)
        
        # Mock risk manager stopping trading
        manager.risk_manager.should_stop_trading.return_value = True
        
        assert manager.should_trade() is False
    
    def test_should_close_position(self):
        """Test position closing decision."""
        algorithm = Mock()
        ticker = "AAPL"
        stock_config = {}
        manager = StockManager(algorithm, ticker, stock_config)
        
        # Mock position manager
        manager.position_manager.should_close_position.return_value = True
        
        assert manager.should_close_position() is True
        manager.position_manager.should_close_position.assert_called_once()
    
    def test_find_and_enter_position_no_trade(self):
        """Test position entry when should not trade."""
        algorithm = Mock()
        ticker = "AAPL"
        stock_config = {'enabled': True}
        manager = StockManager(algorithm, ticker, stock_config)
        
        # Mock that we should not trade
        manager.should_trade = Mock(return_value=False)
        
        manager.find_and_enter_position()
        
        # Should not call position manager
        manager.position_manager.find_and_enter_position.assert_not_called()
    
    def test_find_and_enter_position_no_option_symbol(self):
        """Test position entry when no option symbol available."""
        algorithm = Mock()
        algorithm.option_symbols = {}  # No option symbol for this ticker
        
        ticker = "AAPL"
        stock_config = {'enabled': True}
        manager = StockManager(algorithm, ticker, stock_config)
        
        # Mock that we should trade
        manager.should_trade = Mock(return_value=True)
        
        manager.find_and_enter_position()
        
        # Should not call position manager
        manager.position_manager.find_and_enter_position.assert_not_called()
    
    def test_find_and_enter_position_no_slice_data(self):
        """Test position entry when no slice data available."""
        algorithm = Mock()
        algorithm.option_symbols = {'AAPL': 'AAPL'}
        
        ticker = "AAPL"
        stock_config = {'enabled': True}
        manager = StockManager(algorithm, ticker, stock_config)
        
        # Mock that we should trade
        manager.should_trade = Mock(return_value=True)
        # Mock no slice data
        manager.data_handler.latest_slice = None
        
        manager.find_and_enter_position()
        
        # Should not call position manager
        manager.position_manager.find_and_enter_position.assert_not_called()
    
    def test_find_and_enter_position_success(self):
        """Test successful position entry."""
        algorithm = Mock()
        algorithm.option_symbols = {'AAPL': 'AAPL'}
        
        ticker = "AAPL"
        stock_config = {'enabled': True}
        manager = StockManager(algorithm, ticker, stock_config)
        
        # Mock that we should trade
        manager.should_trade = Mock(return_value=True)
        
        # Mock slice data and option chain
        slice_data = Mock()
        chain = Mock()
        slice_data.OptionChains = {'AAPL': chain}
        manager.data_handler.latest_slice = slice_data
        
        manager.find_and_enter_position()
        
        # Should call position manager
        manager.position_manager.find_and_enter_position.assert_called_once()
    
    def test_close_position_no_contract(self):
        """Test position closing when no contract exists."""
        algorithm = Mock()
        ticker = "AAPL"
        stock_config = {}
        manager = StockManager(algorithm, ticker, stock_config)
        
        manager.current_contract = None
        
        manager.close_position()
        
        # Should not attempt to close
        algorithm.Buy.assert_not_called()
    
    def test_close_position_not_invested(self):
        """Test position closing when not invested."""
        algorithm = Mock()
        ticker = "AAPL"
        stock_config = {}
        manager = StockManager(algorithm, ticker, stock_config)
        
        manager.current_contract = Mock()
        manager.current_contract.Symbol = Mock()
        
        # Mock not invested
        algorithm.Portfolio.__getitem__.return_value = Mock(Invested=False)
        
        manager.close_position()
        
        # Should not attempt to close
        algorithm.Buy.assert_not_called()
    
    def test_close_position_success(self):
        """Test successful position closing."""
        algorithm = Mock()
        ticker = "AAPL"
        stock_config = {}
        manager = StockManager(algorithm, ticker, stock_config)
        
        # Mock contract and position
        contract = Mock()
        contract.Symbol = Mock()
        manager.current_contract = contract
        
        position = Mock()
        position.Invested = True
        position.Quantity = 1
        algorithm.Portfolio.__getitem__.return_value = position
        
        # Mock order
        order = Mock()
        order.AverageFillPrice = 2.0
        algorithm.Buy.return_value = order
        
        # Mock previous trade
        manager.trades = [{'price': 3.0}]  # Entry price
        
        manager.close_position()
        
        # Should attempt to close
        algorithm.Buy.assert_called_once_with(contract.Symbol, 1)
        # Should calculate PnL
        expected_pnl = (3.0 - 2.0) * 1 * 100  # (entry - exit) * quantity * 100
        assert manager.profit_loss == expected_pnl
        # Should reset contract
        assert manager.current_contract is None
    
    def test_get_performance_metrics(self):
        """Test performance metrics retrieval."""
        algorithm = Mock()
        ticker = "AAPL"
        stock_config = {'enabled': True}
        manager = StockManager(algorithm, ticker, stock_config)
        
        # Set some test data
        manager.trade_count = 5
        manager.profit_loss = 1000.0
        manager.current_contract = Mock()
        manager.current_contract.Symbol = "AAPL230616P00150000"
        manager.enabled = True
        
        metrics = manager.get_performance_metrics()
        
        assert metrics['ticker'] == ticker
        assert metrics['trade_count'] == 5
        assert metrics['profit_loss'] == 1000.0
        assert metrics['current_position'] == "AAPL230616P00150000"
        assert metrics['enabled'] is True
    
    def test_get_performance_metrics_no_contract(self):
        """Test performance metrics when no current contract."""
        algorithm = Mock()
        ticker = "AAPL"
        stock_config = {'enabled': True}
        manager = StockManager(algorithm, ticker, stock_config)
        
        manager.current_contract = None
        
        metrics = manager.get_performance_metrics()
        
        assert metrics['current_position'] is None
    
    def test_update_performance(self):
        """Test performance update."""
        algorithm = Mock()
        ticker = "AAPL"
        stock_config = {}
        manager = StockManager(algorithm, ticker, stock_config)
        
        initial_pnl = manager.profit_loss
        pnl_change = 500.0
        
        manager.update_performance(pnl_change)
        
        assert manager.profit_loss == initial_pnl + pnl_change 