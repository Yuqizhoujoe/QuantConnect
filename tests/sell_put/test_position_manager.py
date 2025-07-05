"""
Tests for the PositionManager class.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date, timedelta
from strategies.sell_put.position_manager import PositionManager


class TestPositionManager:
    """Test cases for PositionManager."""
    
    def test_initialization(self):
        """Test PositionManager initialization."""
        algorithm = Mock()
        data_handler = Mock()
        ticker = "AAPL"
        stock_manager = Mock()
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        assert manager.algorithm == algorithm
        assert manager.data_handler == data_handler
        assert manager.ticker == ticker
        assert manager.stock_manager == stock_manager
        assert manager.risk_manager is not None
        assert manager.market_analyzer is not None
    
    def test_should_close_position_no_contract(self):
        """Test position closing when no contract exists."""
        algorithm = Mock()
        data_handler = Mock()
        ticker = "AAPL"
        stock_manager = Mock()
        stock_manager.current_contract = None
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        assert manager.should_close_position() is False
    
    def test_should_close_position_not_invested(self):
        """Test position closing when not invested."""
        algorithm = Mock()
        data_handler = Mock()
        ticker = "AAPL"
        stock_manager = Mock()
        stock_manager.current_contract = Mock()
        
        # Mock not invested
        algorithm.Portfolio.__getitem__.return_value = Mock(Invested=False)
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        assert manager.should_close_position() is False
    
    def test_should_close_position_early_expiry_delta_in_range(self):
        """Test position closing with early expiry but delta in range."""
        algorithm = Mock()
        algorithm.Time.date.return_value = date(2023, 1, 1)
        
        data_handler = Mock()
        data_handler.get_option_delta.return_value = 0.5
        
        ticker = "AAPL"
        stock_manager = Mock()
        stock_manager.current_contract = Mock()
        stock_manager.current_contract.Expiry.date.return_value = date(2023, 1, 10)  # 9 days to expiry
        stock_manager.target_delta_min = 0.25
        stock_manager.target_delta_max = 0.75
        
        # Mock invested
        algorithm.Portfolio.__getitem__.return_value = Mock(Invested=True)
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        # Should not close - delta is in range
        assert manager.should_close_position() is False
    
    def test_should_close_position_early_expiry_delta_out_of_range(self):
        """Test position closing with early expiry and delta out of range."""
        algorithm = Mock()
        algorithm.Time.date.return_value = date(2023, 1, 1)
        
        data_handler = Mock()
        data_handler.get_option_delta.return_value = 0.1  # Below min delta
        
        ticker = "AAPL"
        stock_manager = Mock()
        stock_manager.current_contract = Mock()
        stock_manager.current_contract.Expiry.date.return_value = date(2023, 1, 10)  # 9 days to expiry
        stock_manager.target_delta_min = 0.25
        stock_manager.target_delta_max = 0.75
        
        # Mock invested
        algorithm.Portfolio.__getitem__.return_value = Mock(Invested=True)
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        # Should close - both conditions met
        assert manager.should_close_position() is True
    
    def test_should_close_position_late_expiry_delta_out_of_range(self):
        """Test position closing with late expiry but delta out of range."""
        algorithm = Mock()
        algorithm.Time.date.return_value = date(2023, 1, 1)
        
        data_handler = Mock()
        data_handler.get_option_delta.return_value = 0.1  # Below min delta
        
        ticker = "AAPL"
        stock_manager = Mock()
        stock_manager.current_contract = Mock()
        stock_manager.current_contract.Expiry.date.return_value = date(2023, 1, 20)  # 19 days to expiry
        stock_manager.target_delta_min = 0.25
        stock_manager.target_delta_max = 0.75
        
        # Mock invested
        algorithm.Portfolio.__getitem__.return_value = Mock(Invested=True)
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        # Should not close - expiry not early enough
        assert manager.should_close_position() is False
    
    def test_should_enter_position_owns_underlying(self):
        """Test position entry when owning underlying."""
        algorithm = Mock()
        algorithm.Portfolio.__getitem__ = Mock(return_value=Mock(Quantity=100))  # Owns underlying
        algorithm.Portfolio.MarginRemaining = 50000
        
        data_handler = Mock()
        ticker = "AAPL"
        stock_manager = Mock()
        stock_manager.current_contract = None
        stock_manager.last_trade_date = date(2022, 12, 31)
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        assert manager.should_enter_position() is False
    
    def test_should_enter_position_has_open_position(self):
        """Test position entry when has open position."""
        algorithm = Mock()
        algorithm.Portfolio.__getitem__ = Mock(return_value=Mock(Quantity=0))
        algorithm.Portfolio.MarginRemaining = 50000
        
        data_handler = Mock()
        ticker = "AAPL"
        stock_manager = Mock()
        stock_manager.current_contract = Mock()
        stock_manager.last_trade_date = date(2022, 12, 31)
        
        # Mock invested position
        algorithm.Portfolio.__getitem__.return_value = Mock(Invested=True)
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        assert manager.should_enter_position() is False
    
    def test_should_enter_position_traded_today(self):
        """Test position entry when already traded today."""
        algorithm = Mock()
        algorithm.Time.date.return_value = date(2023, 1, 1)
        algorithm.Portfolio.__getitem__ = Mock(return_value=Mock(Quantity=0))
        algorithm.Portfolio.MarginRemaining = 50000
        
        data_handler = Mock()
        ticker = "AAPL"
        stock_manager = Mock()
        stock_manager.current_contract = None
        stock_manager.last_trade_date = date(2023, 1, 1)  # Traded today
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        assert manager.should_enter_position() is False
    
    def test_should_enter_position_insufficient_margin(self):
        """Test position entry with insufficient margin."""
        algorithm = Mock()
        algorithm.Portfolio.__getitem__ = Mock(return_value=Mock(Quantity=0))
        algorithm.Portfolio.MarginRemaining = 5000  # Low margin
        
        data_handler = Mock()
        ticker = "AAPL"
        stock_manager = Mock()
        stock_manager.current_contract = None
        stock_manager.last_trade_date = date(2022, 12, 31)
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        assert manager.should_enter_position() is False
    
    def test_should_enter_position_risk_manager_stop(self):
        """Test position entry when risk manager stops trading."""
        algorithm = Mock()
        algorithm.Portfolio.__getitem__ = Mock(return_value=Mock(Quantity=0))
        algorithm.Portfolio.MarginRemaining = 50000
        
        data_handler = Mock()
        ticker = "AAPL"
        stock_manager = Mock()
        stock_manager.current_contract = None
        stock_manager.last_trade_date = date(2022, 12, 31)
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        # Mock risk manager stopping trading
        manager.risk_manager.should_stop_trading.return_value = True
        
        assert manager.should_enter_position() is False
    
    def test_should_enter_position_no_slice_data(self):
        """Test position entry when no slice data available."""
        algorithm = Mock()
        algorithm.Portfolio.__getitem__ = Mock(return_value=Mock(Quantity=0))
        algorithm.Portfolio.MarginRemaining = 50000
        
        data_handler = Mock()
        data_handler.latest_slice = None  # No slice data
        
        ticker = "AAPL"
        stock_manager = Mock()
        stock_manager.current_contract = None
        stock_manager.last_trade_date = date(2022, 12, 31)
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        assert manager.should_enter_position() is False
    
    def test_should_enter_position_no_option_chain(self):
        """Test position entry when no option chain available."""
        algorithm = Mock()
        algorithm.Portfolio.__getitem__ = Mock(return_value=Mock(Quantity=0))
        algorithm.Portfolio.MarginRemaining = 50000
        algorithm.option_symbols = {'AAPL': 'AAPL'}
        
        data_handler = Mock()
        slice_data = Mock()
        slice_data.OptionChains = {}  # No option chain
        data_handler.latest_slice = slice_data
        
        ticker = "AAPL"
        stock_manager = Mock()
        stock_manager.current_contract = None
        stock_manager.last_trade_date = date(2022, 12, 31)
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        assert manager.should_enter_position() is False
    
    def test_should_enter_position_market_conditions_avoid(self):
        """Test position entry when market conditions suggest avoiding trade."""
        algorithm = Mock()
        algorithm.Portfolio.__getitem__ = Mock(return_value=Mock(Quantity=0))
        algorithm.Portfolio.MarginRemaining = 50000
        algorithm.option_symbols = {'AAPL': 'AAPL'}
        
        data_handler = Mock()
        slice_data = Mock()
        chain = Mock()
        chain.Underlying.Price = 150.0
        slice_data.OptionChains = {'AAPL': chain}
        data_handler.latest_slice = slice_data
        
        ticker = "AAPL"
        stock_manager = Mock()
        stock_manager.current_contract = None
        stock_manager.last_trade_date = date(2022, 12, 31)
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        # Mock market analyzer to avoid trading
        manager.market_analyzer.should_avoid_trading.return_value = True
        
        assert manager.should_enter_position() is False
    
    def test_should_enter_position_success(self):
        """Test successful position entry conditions."""
        algorithm = Mock()
        algorithm.Portfolio.__getitem__ = Mock(return_value=Mock(Quantity=0))
        algorithm.Portfolio.MarginRemaining = 50000
        algorithm.option_symbols = {'AAPL': 'AAPL'}
        
        data_handler = Mock()
        slice_data = Mock()
        chain = Mock()
        chain.Underlying.Price = 150.0
        slice_data.OptionChains = {'AAPL': chain}
        data_handler.latest_slice = slice_data
        
        ticker = "AAPL"
        stock_manager = Mock()
        stock_manager.current_contract = None
        stock_manager.last_trade_date = date(2022, 12, 31)
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        # Mock market analyzer to allow trading
        manager.market_analyzer.should_avoid_trading.return_value = False
        
        assert manager.should_enter_position() is True
    
    def test_find_and_enter_position_no_slice_data(self):
        """Test position finding when no slice data available."""
        algorithm = Mock()
        algorithm.option_symbols = {'AAPL': 'AAPL'}
        
        data_handler = Mock()
        data_handler.latest_slice = None
        
        ticker = "AAPL"
        stock_manager = Mock()
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        manager.find_and_enter_position()
        
        # Should not proceed with position entry
        manager.market_analyzer.analyze_market_conditions.assert_not_called()
    
    def test_find_and_enter_position_no_option_chain(self):
        """Test position finding when no option chain available."""
        algorithm = Mock()
        algorithm.option_symbols = {'AAPL': 'AAPL'}
        
        data_handler = Mock()
        slice_data = Mock()
        slice_data.OptionChains = {}  # No option chain
        data_handler.latest_slice = slice_data
        
        ticker = "AAPL"
        stock_manager = Mock()
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        manager.find_and_enter_position()
        
        # Should not proceed with position entry
        manager.market_analyzer.analyze_market_conditions.assert_not_called()
    
    def test_find_and_enter_position_no_put_options(self):
        """Test position finding when no put options available."""
        algorithm = Mock()
        algorithm.option_symbols = {'AAPL': 'AAPL'}
        algorithm.Time = Mock()
        
        data_handler = Mock()
        slice_data = Mock()
        chain = Mock()
        chain.Underlying.Price = 150.0
        # No put options in chain
        chain.__iter__ = Mock(return_value=iter([]))
        slice_data.OptionChains = {'AAPL': chain}
        data_handler.latest_slice = slice_data
        
        ticker = "AAPL"
        stock_manager = Mock()
        stock_manager.option_frequency = "any"
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        manager.find_and_enter_position()
        
        # Should not proceed with position entry
        manager.market_analyzer.analyze_market_conditions.assert_not_called()
    
    def test_is_valid_option_monthly(self):
        """Test option validation for monthly frequency."""
        algorithm = Mock()
        data_handler = Mock()
        ticker = "AAPL"
        stock_manager = Mock()
        stock_manager.option_frequency = "monthly"
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        # Test monthly expiry (third Friday)
        monthly_expiry = date(2023, 1, 20)  # Third Friday of January
        assert manager.is_valid_option(monthly_expiry) is True
        
        # Test non-monthly expiry
        weekly_expiry = date(2023, 1, 13)  # Second Friday
        assert manager.is_valid_option(weekly_expiry) is False
    
    def test_is_valid_option_weekly(self):
        """Test option validation for weekly frequency."""
        algorithm = Mock()
        data_handler = Mock()
        ticker = "AAPL"
        stock_manager = Mock()
        stock_manager.option_frequency = "weekly"
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        # Test weekly expiry (any Friday)
        weekly_expiry = date(2023, 1, 13)  # Friday
        assert manager.is_valid_option(weekly_expiry) is True
        
        # Test non-weekly expiry
        non_friday_expiry = date(2023, 1, 15)  # Sunday
        assert manager.is_valid_option(non_friday_expiry) is False
    
    def test_is_valid_option_any(self):
        """Test option validation for any frequency."""
        algorithm = Mock()
        data_handler = Mock()
        ticker = "AAPL"
        stock_manager = Mock()
        stock_manager.option_frequency = "any"
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        # Any expiry should be valid
        any_expiry = date(2023, 1, 15)
        assert manager.is_valid_option(any_expiry) is True
    
    @patch('strategies.sell_put.position_manager.OptionRight')
    def test_select_best_contract(self, mock_option_right):
        """Test contract selection logic."""
        algorithm = Mock()
        data_handler = Mock()
        ticker = "AAPL"
        stock_manager = Mock()
        
        manager = PositionManager(algorithm, data_handler, ticker, stock_manager)
        
        # Mock option contracts
        contract1 = Mock()
        contract1.Strike = 140.0
        contract1.Expiry = date(2023, 1, 20)
        contract1.Bid = 2.0
        contract1.Ask = 2.1
        
        contract2 = Mock()
        contract2.Strike = 145.0
        contract2.Expiry = date(2023, 1, 20)
        contract2.Bid = 3.0
        contract2.Ask = 3.1
        
        valid_puts = [contract1, contract2]
        underlying_price = 150.0
        market_analysis = {'market_regime': 'bullish_low_vol'}
        
        # Mock delta values
        data_handler.get_option_delta.side_effect = [0.3, 0.4]
        
        selected = manager.select_best_contract(valid_puts, underlying_price, market_analysis)
        
        # Should return one of the contracts
        assert selected in valid_puts 