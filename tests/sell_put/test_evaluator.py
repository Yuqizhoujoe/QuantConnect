"""
Tests for the Evaluator class.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import numpy as np
from datetime import date
from strategies.sell_put.evaluator import Evaluator


class TestEvaluator:
    """Test cases for Evaluator."""
    
    def test_initialization(self):
        """Test Evaluator initialization."""
        algorithm = Mock()
        
        evaluator = Evaluator(algorithm)
        
        assert evaluator.algorithm == algorithm
    
    def test_on_end_of_algorithm_basic_metrics(self):
        """Test basic end-of-algorithm metrics."""
        algorithm = Mock()
        algorithm.ticker = "AAPL"
        algorithm.trade_count = 10
        algorithm.Portfolio.TotalPortfolioValue = 105000.0
        algorithm.profit_loss = 5000.0
        algorithm.peak_portfolio_value = 100000.0
        
        evaluator = Evaluator(algorithm)
        
        # Mock Log method
        algorithm.Log = Mock()
        
        evaluator.on_end_of_algorithm()
        
        # Verify basic metrics were logged
        algorithm.Log.assert_any_call("=== ENHANCED STRATEGY COMPLETE ===")
        algorithm.Log.assert_any_call("Ticker: AAPL")
        algorithm.Log.assert_any_call("Total Trades: 10")
        algorithm.Log.assert_any_call("Final Portfolio Value: $105000.00")
        algorithm.Log.assert_any_call("Total P&L: $5000.00")
        algorithm.Log.assert_any_call("Maximum Drawdown: 5.00%")
    
    def test_on_end_of_algorithm_no_trades(self):
        """Test end-of-algorithm with no trades."""
        algorithm = Mock()
        algorithm.ticker = "AAPL"
        algorithm.trade_count = 0
        algorithm.Portfolio.TotalPortfolioValue = 100000.0
        algorithm.profit_loss = 0.0
        algorithm.peak_portfolio_value = 100000.0
        algorithm.trades = []
        
        evaluator = Evaluator(algorithm)
        algorithm.Log = Mock()
        
        evaluator.on_end_of_algorithm()
        
        # Should not try to calculate trade statistics
        algorithm.Log.assert_any_call("=== ENHANCED STRATEGY COMPLETE ===")
        algorithm.Log.assert_any_call("Total Trades: 0")
    
    def test_on_end_of_algorithm_with_completed_trades(self):
        """Test end-of-algorithm with completed trades."""
        algorithm = Mock()
        algorithm.ticker = "AAPL"
        algorithm.trade_count = 5
        algorithm.Portfolio.TotalPortfolioValue = 105000.0
        algorithm.profit_loss = 5000.0
        algorithm.peak_portfolio_value = 100000.0
        
        # Mock completed trades
        algorithm.trades = [
            {'entry_date': date(2023, 1, 1), 'exit_date': date(2023, 1, 15), 'pnl': 1000.0},
            {'entry_date': date(2023, 1, 16), 'exit_date': date(2023, 1, 30), 'pnl': -500.0},
            {'entry_date': date(2023, 2, 1), 'exit_date': date(2023, 2, 15), 'pnl': 800.0},
            {'entry_date': date(2023, 2, 16), 'exit_date': date(2023, 2, 28), 'pnl': 1200.0},
            {'entry_date': date(2023, 3, 1), 'exit_date': date(2023, 3, 15), 'pnl': -200.0}
        ]
        
        evaluator = Evaluator(algorithm)
        algorithm.Log = Mock()
        
        evaluator.on_end_of_algorithm()
        
        # Verify trade statistics were calculated and logged
        algorithm.Log.assert_any_call("Win Rate: 60.0%")  # 3 wins out of 5
        algorithm.Log.assert_any_call("Average Win: $1000.00")  # (1000 + 800 + 1200) / 3
        algorithm.Log.assert_any_call("Maximum Win: $1200.00")
        algorithm.Log.assert_any_call("Average Loss: $350.00")  # (-500 + -200) / 2
        algorithm.Log.assert_any_call("Maximum Loss: $500.00")
        algorithm.Log.assert_any_call("Profit Factor: 2.86")  # 1000 / 350
        algorithm.Log.assert_any_call("Average Trade Duration: 14.0 days")
    
    def test_on_end_of_algorithm_all_winning_trades(self):
        """Test end-of-algorithm with all winning trades."""
        algorithm = Mock()
        algorithm.ticker = "AAPL"
        algorithm.trade_count = 3
        algorithm.Portfolio.TotalPortfolioValue = 103000.0
        algorithm.profit_loss = 3000.0
        algorithm.peak_portfolio_value = 100000.0
        
        # Mock all winning trades
        algorithm.trades = [
            {'entry_date': date(2023, 1, 1), 'exit_date': date(2023, 1, 15), 'pnl': 1000.0},
            {'entry_date': date(2023, 1, 16), 'exit_date': date(2023, 1, 30), 'pnl': 800.0},
            {'entry_date': date(2023, 2, 1), 'exit_date': date(2023, 2, 15), 'pnl': 1200.0}
        ]
        
        evaluator = Evaluator(algorithm)
        algorithm.Log = Mock()
        
        evaluator.on_end_of_algorithm()
        
        # Verify trade statistics for all winning trades
        algorithm.Log.assert_any_call("Win Rate: 100.0%")
        algorithm.Log.assert_any_call("Average Win: $1000.00")
        algorithm.Log.assert_any_call("Maximum Win: $1200.00")
        # Should not log loss statistics
        assert not any("Average Loss" in str(call) for call in algorithm.Log.call_args_list)
        assert not any("Maximum Loss" in str(call) for call in algorithm.Log.call_args_list)
        assert not any("Profit Factor" in str(call) for call in algorithm.Log.call_args_list)
    
    def test_on_end_of_algorithm_all_losing_trades(self):
        """Test end-of-algorithm with all losing trades."""
        algorithm = Mock()
        algorithm.ticker = "AAPL"
        algorithm.trade_count = 3
        algorithm.Portfolio.TotalPortfolioValue = 97000.0
        algorithm.profit_loss = -3000.0
        algorithm.peak_portfolio_value = 100000.0
        
        # Mock all losing trades
        algorithm.trades = [
            {'entry_date': date(2023, 1, 1), 'exit_date': date(2023, 1, 15), 'pnl': -1000.0},
            {'entry_date': date(2023, 1, 16), 'exit_date': date(2023, 1, 30), 'pnl': -800.0},
            {'entry_date': date(2023, 2, 1), 'exit_date': date(2023, 2, 15), 'pnl': -1200.0}
        ]
        
        evaluator = Evaluator(algorithm)
        algorithm.Log = Mock()
        
        evaluator.on_end_of_algorithm()
        
        # Verify trade statistics for all losing trades
        algorithm.Log.assert_any_call("Win Rate: 0.0%")
        algorithm.Log.assert_any_call("Average Loss: $1000.00")
        algorithm.Log.assert_any_call("Maximum Loss: $1200.00")
        # Should not log win statistics
        assert not any("Average Win" in str(call) for call in algorithm.Log.call_args_list)
        assert not any("Maximum Win" in str(call) for call in algorithm.Log.call_args_list)
        assert not any("Profit Factor" in str(call) for call in algorithm.Log.call_args_list)
    
    def test_on_end_of_algorithm_incomplete_trades(self):
        """Test end-of-algorithm with incomplete trades."""
        algorithm = Mock()
        algorithm.ticker = "AAPL"
        algorithm.trade_count = 3
        algorithm.Portfolio.TotalPortfolioValue = 102000.0
        algorithm.profit_loss = 2000.0
        algorithm.peak_portfolio_value = 100000.0
        
        # Mock trades with some incomplete (no pnl)
        algorithm.trades = [
            {'entry_date': date(2023, 1, 1), 'exit_date': date(2023, 1, 15), 'pnl': 1000.0},
            {'entry_date': date(2023, 1, 16)},  # Incomplete trade
            {'entry_date': date(2023, 2, 1), 'exit_date': date(2023, 2, 15), 'pnl': 1000.0}
        ]
        
        evaluator = Evaluator(algorithm)
        algorithm.Log = Mock()
        
        evaluator.on_end_of_algorithm()
        
        # Should only analyze completed trades
        algorithm.Log.assert_any_call("Win Rate: 100.0%")  # 2 wins out of 2 completed
        algorithm.Log.assert_any_call("Average Win: $1000.00")
    
    def test_on_end_of_algorithm_trade_duration_calculation(self):
        """Test trade duration calculation."""
        algorithm = Mock()
        algorithm.ticker = "AAPL"
        algorithm.trade_count = 2
        algorithm.Portfolio.TotalPortfolioValue = 101000.0
        algorithm.profit_loss = 1000.0
        algorithm.peak_portfolio_value = 100000.0
        
        # Mock trades with different durations
        algorithm.trades = [
            {'entry_date': date(2023, 1, 1), 'exit_date': date(2023, 1, 10), 'pnl': 500.0},  # 9 days
            {'entry_date': date(2023, 1, 15), 'exit_date': date(2023, 1, 30), 'pnl': 500.0}  # 15 days
        ]
        
        evaluator = Evaluator(algorithm)
        algorithm.Log = Mock()
        
        evaluator.on_end_of_algorithm()
        
        # Average duration should be 12 days
        algorithm.Log.assert_any_call("Average Trade Duration: 12.0 days")
    
    def test_on_end_of_algorithm_sharpe_ratio_calculation(self):
        """Test Sharpe ratio calculation."""
        algorithm = Mock()
        algorithm.ticker = "AAPL"
        algorithm.trade_count = 2
        algorithm.Portfolio.TotalPortfolioValue = 101000.0
        algorithm.profit_loss = 1000.0
        algorithm.peak_portfolio_value = 100000.0
        algorithm.trades = []
        
        # Mock daily PnL data for Sharpe calculation
        algorithm.daily_pnl = [100000, 100500, 101000]  # Daily portfolio values
        
        evaluator = Evaluator(algorithm)
        algorithm.Log = Mock()
        
        evaluator.on_end_of_algorithm()
        
        # Should calculate and log Sharpe ratio
        # Returns would be [500, 500], mean=500, std=0, Sharpe=inf (handled by code)
        assert any("Sharpe Ratio" in str(call) for call in algorithm.Log.call_args_list)
    
    def test_on_end_of_algorithm_sharpe_ratio_insufficient_data(self):
        """Test Sharpe ratio calculation with insufficient data."""
        algorithm = Mock()
        algorithm.ticker = "AAPL"
        algorithm.trade_count = 2
        algorithm.Portfolio.TotalPortfolioValue = 101000.0
        algorithm.profit_loss = 1000.0
        algorithm.peak_portfolio_value = 100000.0
        algorithm.trades = []
        
        # Mock insufficient daily PnL data
        algorithm.daily_pnl = [100000]  # Only one data point
        
        evaluator = Evaluator(algorithm)
        algorithm.Log = Mock()
        
        evaluator.on_end_of_algorithm()
        
        # Should not calculate Sharpe ratio with insufficient data
        assert not any("Sharpe Ratio" in str(call) for call in algorithm.Log.call_args_list)
    
    def test_on_end_of_algorithm_sharpe_ratio_exception(self):
        """Test Sharpe ratio calculation with exception handling."""
        algorithm = Mock()
        algorithm.ticker = "AAPL"
        algorithm.trade_count = 2
        algorithm.Portfolio.TotalPortfolioValue = 101000.0
        algorithm.profit_loss = 1000.0
        algorithm.peak_portfolio_value = 100000.0
        algorithm.trades = []
        
        # Mock daily PnL that will cause an exception
        algorithm.daily_pnl = [100000, 100500, 101000]
        
        evaluator = Evaluator(algorithm)
        algorithm.Log = Mock()
        
        # Mock numpy to raise an exception
        with patch('numpy.diff', side_effect=Exception("Test exception")):
            evaluator.on_end_of_algorithm()
        
        # Should handle exception gracefully
        algorithm.Log.assert_any_call("Could not calculate Sharpe ratio: Test exception")
    
    def test_on_end_of_algorithm_risk_metrics_success(self):
        """Test risk metrics calculation success."""
        algorithm = Mock()
        algorithm.ticker = "AAPL"
        algorithm.trade_count = 2
        algorithm.Portfolio.TotalPortfolioValue = 101000.0
        algorithm.profit_loss = 1000.0
        algorithm.peak_portfolio_value = 100000.0
        algorithm.trades = []
        
        # Mock risk manager
        algorithm.risk_manager = Mock()
        algorithm.risk_manager.get_risk_metrics.return_value = {
            'win_rate': 0.75,
            'volatility': 0.15
        }
        
        evaluator = Evaluator(algorithm)
        algorithm.Log = Mock()
        
        evaluator.on_end_of_algorithm()
        
        # Should log risk metrics
        algorithm.Log.assert_any_call("Final Win Rate: 75.0%")
        algorithm.Log.assert_any_call("Final Volatility Factor: 0.15")
    
    def test_on_end_of_algorithm_risk_metrics_exception(self):
        """Test risk metrics calculation with exception handling."""
        algorithm = Mock()
        algorithm.ticker = "AAPL"
        algorithm.trade_count = 2
        algorithm.Portfolio.TotalPortfolioValue = 101000.0
        algorithm.profit_loss = 1000.0
        algorithm.peak_portfolio_value = 100000.0
        algorithm.trades = []
        
        # Mock risk manager that raises exception
        algorithm.risk_manager = Mock()
        algorithm.risk_manager.get_risk_metrics.side_effect = Exception("Risk metrics error")
        
        evaluator = Evaluator(algorithm)
        algorithm.Log = Mock()
        
        evaluator.on_end_of_algorithm()
        
        # Should handle exception gracefully
        algorithm.Log.assert_any_call("Could not calculate final risk metrics: Risk metrics error")
    
    def test_on_end_of_algorithm_no_risk_manager(self):
        """Test end-of-algorithm when no risk manager exists."""
        algorithm = Mock()
        algorithm.ticker = "AAPL"
        algorithm.trade_count = 2
        algorithm.Portfolio.TotalPortfolioValue = 101000.0
        algorithm.profit_loss = 1000.0
        algorithm.peak_portfolio_value = 100000.0
        algorithm.trades = []
        
        # No risk_manager attribute
        if hasattr(algorithm, 'risk_manager'):
            delattr(algorithm, 'risk_manager')
        
        evaluator = Evaluator(algorithm)
        algorithm.Log = Mock()
        
        evaluator.on_end_of_algorithm()
        
        # Should handle missing risk manager gracefully
        algorithm.Log.assert_any_call("Could not calculate final risk metrics: 'Mock' object has no attribute 'risk_manager'")
    
    def test_on_end_of_algorithm_zero_peak_value(self):
        """Test end-of-algorithm with zero peak value to avoid division by zero."""
        algorithm = Mock()
        algorithm.ticker = "AAPL"
        algorithm.trade_count = 0
        algorithm.Portfolio.TotalPortfolioValue = 0.0
        algorithm.profit_loss = 0.0
        algorithm.peak_portfolio_value = 0.0
        algorithm.trades = []
        
        evaluator = Evaluator(algorithm)
        algorithm.Log = Mock()
        
        evaluator.on_end_of_algorithm()
        
        # Should handle zero peak value gracefully
        algorithm.Log.assert_any_call("Maximum Drawdown: 0.00%")
    
    def test_on_end_of_algorithm_negative_drawdown(self):
        """Test end-of-algorithm with negative drawdown (current value > peak)."""
        algorithm = Mock()
        algorithm.ticker = "AAPL"
        algorithm.trade_count = 0
        algorithm.Portfolio.TotalPortfolioValue = 110000.0
        algorithm.profit_loss = 10000.0
        algorithm.peak_portfolio_value = 100000.0
        algorithm.trades = []
        
        evaluator = Evaluator(algorithm)
        algorithm.Log = Mock()
        
        evaluator.on_end_of_algorithm()
        
        # Should handle negative drawdown gracefully
        algorithm.Log.assert_any_call("Maximum Drawdown: -10.00%") 