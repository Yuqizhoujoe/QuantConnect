"""
Tests for the DataHandler class.
"""

import pytest
from unittest.mock import Mock, MagicMock
from core.data_handler import DataHandler


class TestDataHandler:
    """Test cases for DataHandler."""
    
    def test_initialization(self):
        """Test DataHandler initialization."""
        algorithm = Mock()
        ticker = "AAPL"
        
        handler = DataHandler(algorithm, ticker)
        
        assert handler.algorithm == algorithm
        assert handler.ticker == ticker
        assert handler.latest_slice is None
        assert handler.plot_counter == 0
        assert handler.plotting_enabled is True
    
    def test_update_data(self):
        """Test data update functionality."""
        algorithm = Mock()
        ticker = "AAPL"
        handler = DataHandler(algorithm, ticker)
        
        slice_data = Mock()
        handler.update_data(slice_data)
        
        assert handler.latest_slice == slice_data
    
    def test_get_option_delta(self):
        """Test option delta retrieval."""
        algorithm = Mock()
        ticker = "AAPL"
        handler = DataHandler(algorithm, ticker)
        
        # Test with valid Greeks
        contract = Mock()
        contract.Greeks = Mock()
        contract.Greeks.Delta = 0.5
        
        delta = handler.get_option_delta(contract)
        assert delta == 0.5
        
        # Test with None Greeks
        contract.Greeks = None
        delta = handler.get_option_delta(contract)
        assert delta == 0
        
        # Test with None Delta
        contract.Greeks = Mock()
        contract.Greeks.Delta = None
        delta = handler.get_option_delta(contract)
        assert delta == 0
    
    def test_should_plot(self):
        """Test plotting decision logic."""
        algorithm = Mock()
        ticker = "AAPL"
        handler = DataHandler(algorithm, ticker)
        
        # Test with plotting disabled
        handler.plotting_enabled = False
        assert handler.should_plot() is False
        
        # Test with plotting enabled
        handler.plotting_enabled = True
        handler.plot_counter = 50  # Should plot every 50 points
        assert handler.should_plot() is True
        
        # Test risk plotting (less frequent)
        handler.plot_counter = 150  # Should plot risk every 150 points
        assert handler.should_plot("risk") is True
        
        # Test PnL plotting
        handler.plot_pnl = False
        assert handler.should_plot("pnl") is False 