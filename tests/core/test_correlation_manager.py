"""
Tests for the CorrelationManager class.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import numpy as np
from core.correlation_manager import CorrelationManager


class TestCorrelationManager:
    """Test cases for CorrelationManager."""
    
    def test_initialization(self):
        """Test CorrelationManager initialization."""
        algorithm = Mock()
        ticker = "AAPL"
        
        manager = CorrelationManager(algorithm, ticker)
        
        assert manager.algorithm == algorithm
        assert manager.ticker == ticker
        assert manager.correlation_threshold == 0.7
        assert manager.lookback_period == 30
        assert manager.correlation_data == {}
        assert manager.correlation_matrix == {}
    
    def test_update_correlation_data_single_stock(self):
        """Test correlation data update with single stock."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = CorrelationManager(algorithm, ticker)
        
        # Mock stock managers
        stock_managers = {
            'AAPL': Mock()
        }
        stock_managers['AAPL'].get_correlation_data.return_value = [100, 101, 102, 103, 104]
        
        manager.update_correlation_data(stock_managers)
        
        # Should store correlation data
        assert 'AAPL' in manager.correlation_data
        assert len(manager.correlation_data['AAPL']) == 5
    
    def test_update_correlation_data_multiple_stocks(self):
        """Test correlation data update with multiple stocks."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = CorrelationManager(algorithm, ticker)
        
        # Mock stock managers
        stock_managers = {
            'AAPL': Mock(),
            'MSFT': Mock(),
            'GOOGL': Mock()
        }
        stock_managers['AAPL'].get_correlation_data.return_value = [100, 101, 102, 103, 104]
        stock_managers['MSFT'].get_correlation_data.return_value = [200, 201, 202, 203, 204]
        stock_managers['GOOGL'].get_correlation_data.return_value = [300, 301, 302, 303, 304]
        
        manager.update_correlation_data(stock_managers)
        
        # Should store correlation data for all stocks
        assert 'AAPL' in manager.correlation_data
        assert 'MSFT' in manager.correlation_data
        assert 'GOOGL' in manager.correlation_data
        assert len(manager.correlation_data['AAPL']) == 5
        assert len(manager.correlation_data['MSFT']) == 5
        assert len(manager.correlation_data['GOOGL']) == 5
    
    def test_update_correlation_data_insufficient_data(self):
        """Test correlation data update with insufficient data."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = CorrelationManager(algorithm, ticker)
        
        # Mock stock managers with insufficient data
        stock_managers = {
            'AAPL': Mock()
        }
        stock_managers['AAPL'].get_correlation_data.return_value = [100, 101]  # Only 2 data points
        
        manager.update_correlation_data(stock_managers)
        
        # Should not store insufficient data
        assert 'AAPL' not in manager.correlation_data
    
    def test_calculate_correlation_matrix_single_stock(self):
        """Test correlation matrix calculation with single stock."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = CorrelationManager(algorithm, ticker)
        
        # Set up correlation data
        manager.correlation_data = {
            'AAPL': [100, 101, 102, 103, 104]
        }
        
        matrix = manager.calculate_correlation_matrix()
        
        # Should return matrix with single stock
        assert 'AAPL' in matrix
        assert matrix['AAPL']['AAPL'] == 1.0  # Self-correlation should be 1.0
    
    def test_calculate_correlation_matrix_multiple_stocks(self):
        """Test correlation matrix calculation with multiple stocks."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = CorrelationManager(algorithm, ticker)
        
        # Set up correlation data with different trends
        manager.correlation_data = {
            'AAPL': [100, 101, 102, 103, 104],  # Upward trend
            'MSFT': [200, 201, 202, 203, 204],  # Upward trend (high correlation)
            'GOOGL': [300, 299, 298, 297, 296]  # Downward trend (negative correlation)
        }
        
        matrix = manager.calculate_correlation_matrix()
        
        # Should return matrix with all stocks
        assert 'AAPL' in matrix
        assert 'MSFT' in matrix
        assert 'GOOGL' in matrix
        
        # Self-correlations should be 1.0
        assert matrix['AAPL']['AAPL'] == 1.0
        assert matrix['MSFT']['MSFT'] == 1.0
        assert matrix['GOOGL']['GOOGL'] == 1.0
        
        # AAPL and MSFT should have high positive correlation
        assert matrix['AAPL']['MSFT'] > 0.9
        assert matrix['MSFT']['AAPL'] > 0.9
        
        # AAPL and GOOGL should have negative correlation
        assert matrix['AAPL']['GOOGL'] < 0
        assert matrix['GOOGL']['AAPL'] < 0
    
    def test_calculate_correlation_matrix_insufficient_data(self):
        """Test correlation matrix calculation with insufficient data."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = CorrelationManager(algorithm, ticker)
        
        # Set up insufficient correlation data
        manager.correlation_data = {
            'AAPL': [100, 101]  # Only 2 data points
        }
        
        matrix = manager.calculate_correlation_matrix()
        
        # Should return empty matrix
        assert matrix == {}
    
    def test_get_stock_correlation_existing(self):
        """Test getting stock correlation when it exists."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = CorrelationManager(algorithm, ticker)
        
        # Set up correlation matrix
        manager.correlation_matrix = {
            'AAPL': {'MSFT': 0.8, 'GOOGL': 0.3},
            'MSFT': {'AAPL': 0.8, 'GOOGL': 0.4},
            'GOOGL': {'AAPL': 0.3, 'MSFT': 0.4}
        }
        
        correlation = manager.get_stock_correlation('MSFT')
        
        # Should return correlation with AAPL
        assert correlation == 0.8
    
    def test_get_stock_correlation_not_found(self):
        """Test getting stock correlation when not found."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = CorrelationManager(algorithm, ticker)
        
        # Set up correlation matrix
        manager.correlation_matrix = {
            'AAPL': {'MSFT': 0.8}
        }
        
        correlation = manager.get_stock_correlation('GOOGL')
        
        # Should return 0 for unknown stock
        assert correlation == 0.0
    
    def test_get_stock_correlation_empty_matrix(self):
        """Test getting stock correlation with empty matrix."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = CorrelationManager(algorithm, ticker)
        
        # Empty correlation matrix
        manager.correlation_matrix = {}
        
        correlation = manager.get_stock_correlation('MSFT')
        
        # Should return 0 for empty matrix
        assert correlation == 0.0
    
    def test_get_high_correlation_stocks(self):
        """Test getting high correlation stocks."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = CorrelationManager(algorithm, ticker)
        
        # Set up correlation matrix
        manager.correlation_matrix = {
            'AAPL': {'MSFT': 0.8, 'GOOGL': 0.3, 'TSLA': 0.9},
            'MSFT': {'AAPL': 0.8, 'GOOGL': 0.4, 'TSLA': 0.7},
            'GOOGL': {'AAPL': 0.3, 'MSFT': 0.4, 'TSLA': 0.2},
            'TSLA': {'AAPL': 0.9, 'MSFT': 0.7, 'GOOGL': 0.2}
        }
        
        high_corr_stocks = manager.get_high_correlation_stocks()
        
        # Should return stocks with correlation >= 0.7
        assert 'MSFT' in high_corr_stocks
        assert 'TSLA' in high_corr_stocks
        assert 'GOOGL' not in high_corr_stocks  # Correlation 0.3 < 0.7
    
    def test_get_high_correlation_stocks_empty_matrix(self):
        """Test getting high correlation stocks with empty matrix."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = CorrelationManager(algorithm, ticker)
        
        # Empty correlation matrix
        manager.correlation_matrix = {}
        
        high_corr_stocks = manager.get_high_correlation_stocks()
        
        # Should return empty list
        assert high_corr_stocks == []
    
    def test_should_reduce_trading_high_correlation(self):
        """Test trading reduction decision with high correlation."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = CorrelationManager(algorithm, ticker)
        
        # Set up correlation matrix with high correlation
        manager.correlation_matrix = {
            'AAPL': {'MSFT': 0.8, 'GOOGL': 0.9},
            'MSFT': {'AAPL': 0.8, 'GOOGL': 0.7},
            'GOOGL': {'AAPL': 0.9, 'MSFT': 0.7}
        }
        
        should_reduce = manager.should_reduce_trading()
        
        # Should reduce trading due to high correlations
        assert should_reduce is True
    
    def test_should_reduce_trading_low_correlation(self):
        """Test trading reduction decision with low correlation."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = CorrelationManager(algorithm, ticker)
        
        # Set up correlation matrix with low correlation
        manager.correlation_matrix = {
            'AAPL': {'MSFT': 0.3, 'GOOGL': 0.2},
            'MSFT': {'AAPL': 0.3, 'GOOGL': 0.4},
            'GOOGL': {'AAPL': 0.2, 'MSFT': 0.4}
        }
        
        should_reduce = manager.should_reduce_trading()
        
        # Should not reduce trading due to low correlations
        assert should_reduce is False
    
    def test_should_reduce_trading_empty_matrix(self):
        """Test trading reduction decision with empty matrix."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = CorrelationManager(algorithm, ticker)
        
        # Empty correlation matrix
        manager.correlation_matrix = {}
        
        should_reduce = manager.should_reduce_trading()
        
        # Should not reduce trading with no correlation data
        assert should_reduce is False
    
    def test_get_correlation_summary(self):
        """Test correlation summary generation."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = CorrelationManager(algorithm, ticker)
        
        # Set up correlation matrix
        manager.correlation_matrix = {
            'AAPL': {'MSFT': 0.8, 'GOOGL': 0.3, 'TSLA': 0.9},
            'MSFT': {'AAPL': 0.8, 'GOOGL': 0.4, 'TSLA': 0.7},
            'GOOGL': {'AAPL': 0.3, 'MSFT': 0.4, 'TSLA': 0.2},
            'TSLA': {'AAPL': 0.9, 'MSFT': 0.7, 'GOOGL': 0.2}
        }
        
        summary = manager.get_correlation_summary()
        
        # Should return summary with key metrics
        assert 'average_correlation' in summary
        assert 'high_correlation_pairs' in summary
        assert 'low_correlation_pairs' in summary
        assert 'recommendation' in summary
        
        # Check that high correlation pairs are identified
        high_corr_pairs = summary['high_correlation_pairs']
        assert any('AAPL' in pair and 'TSLA' in pair for pair in high_corr_pairs)
        assert any('AAPL' in pair and 'MSFT' in pair for pair in high_corr_pairs)
    
    def test_get_correlation_summary_empty_matrix(self):
        """Test correlation summary with empty matrix."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = CorrelationManager(algorithm, ticker)
        
        # Empty correlation matrix
        manager.correlation_matrix = {}
        
        summary = manager.get_correlation_summary()
        
        # Should return default summary
        assert 'average_correlation' in summary
        assert 'high_correlation_pairs' in summary
        assert 'low_correlation_pairs' in summary
        assert 'recommendation' in summary
        assert summary['average_correlation'] == 0.0
        assert summary['high_correlation_pairs'] == []
        assert summary['low_correlation_pairs'] == []
    
    def test_update_correlation_matrix(self):
        """Test correlation matrix update."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = CorrelationManager(algorithm, ticker)
        
        # Mock stock managers
        stock_managers = {
            'AAPL': Mock(),
            'MSFT': Mock()
        }
        stock_managers['AAPL'].get_correlation_data.return_value = [100, 101, 102, 103, 104]
        stock_managers['MSFT'].get_correlation_data.return_value = [200, 201, 202, 203, 204]
        
        # Update correlation data and matrix
        manager.update_correlation_data(stock_managers)
        manager.update_correlation_matrix()
        
        # Should have correlation matrix
        assert manager.correlation_matrix != {}
        assert 'AAPL' in manager.correlation_matrix
        assert 'MSFT' in manager.correlation_matrix
    
    def test_correlation_data_memory_management(self):
        """Test correlation data memory management."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = CorrelationManager(algorithm, ticker)
        
        # Add more data than lookback period
        long_data = list(range(50))  # 50 data points
        manager.correlation_data['AAPL'] = long_data
        
        # Should trim to lookback period
        manager._trim_correlation_data()
        
        # Should keep only the last 30 data points
        assert len(manager.correlation_data['AAPL']) == 30
        assert manager.correlation_data['AAPL'][0] == 20  # First after trimming
        assert manager.correlation_data['AAPL'][-1] == 49  # Last
    
    def test_correlation_data_no_trimming_needed(self):
        """Test correlation data when no trimming is needed."""
        algorithm = Mock()
        ticker = "AAPL"
        manager = CorrelationManager(algorithm, ticker)
        
        # Add data within lookback period
        short_data = list(range(20))  # 20 data points
        manager.correlation_data['AAPL'] = short_data
        
        # Should not trim
        manager._trim_correlation_data()
        
        # Should keep all data
        assert len(manager.correlation_data['AAPL']) == 20
        assert manager.correlation_data['AAPL'] == short_data 