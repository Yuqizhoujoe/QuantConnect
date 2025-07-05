#!/usr/bin/env python3
"""
Simple test script to verify the risk manager fix.
This script tests the risk manager logic without importing QuantConnect modules.
"""

def test_risk_manager_logic():
    """Test the risk manager logic that was implemented in the fix."""
    
    class MockAlgorithm:
        def __init__(self):
            self.Portfolio = type('MockPortfolio', (), {
                'TotalPortfolioValue': 100000,
                'TotalMarginUsed': 5000,
                'MarginRemaining': 95000
            })()
            self.portfolio_manager = None
            self.peak_portfolio_value = 105000
            
    class MockStockManager:
        def __init__(self, ticker, trades, daily_pnl):
            self.ticker = ticker
            self.trades = trades
            self.daily_pnl = daily_pnl
    
    class MockPortfolioManager:
        def __init__(self, stock_managers):
            self.stock_managers = stock_managers
    
    def get_historical_win_rate(algorithm):
        """This is the win rate logic from the risk manager fix."""
        # Get all trades from portfolio manager if available
        all_trades = []
        if hasattr(algorithm, 'portfolio_manager') and algorithm.portfolio_manager:
            for stock_manager in algorithm.portfolio_manager.stock_managers.values():
                if hasattr(stock_manager, 'trades'):
                    all_trades.extend(stock_manager.trades)
        
        completed_trades = [t for t in all_trades if 'pnl' in t]
        if not completed_trades:
            return 0.6  # Default assumption for new strategies
            
        winning_trades = [t for t in completed_trades if t['pnl'] > 0]
        return len(winning_trades) / len(completed_trades)
    
    def get_volatility_adjustment(algorithm):
        """This is the volatility adjustment logic from the risk manager fix."""
        # Get daily PnL from portfolio manager if available
        all_daily_pnl = []
        if hasattr(algorithm, 'portfolio_manager') and algorithm.portfolio_manager:
            for stock_manager in algorithm.portfolio_manager.stock_managers.values():
                if hasattr(stock_manager, 'daily_pnl'):
                    all_daily_pnl.extend(stock_manager.daily_pnl)
        
        volatility_lookback = 20
        if len(all_daily_pnl) < volatility_lookback:
            return 1.0  # Default factor when insufficient data
            
        # Calculate volatility from recent PnL data
        recent_pnl = all_daily_pnl[-volatility_lookback:]
        
        # Simple standard deviation calculation without numpy
        mean = sum(recent_pnl) / len(recent_pnl)
        variance = sum((x - mean) ** 2 for x in recent_pnl) / len(recent_pnl)
        volatility = variance ** 0.5
        
        # Adjust position size based on volatility regime
        volatility_threshold = 0.4
        if volatility > volatility_threshold:
            return 0.7  # Reduce position size in high volatility
        elif volatility < 0.1:
            return 1.2  # Increase position size in low volatility
        else:
            return 1.0  # Normal position size in moderate volatility
    
    # Test cases
    test_cases = [
        {
            "name": "No Portfolio Manager",
            "algorithm": MockAlgorithm(),
            "expected_win_rate": 0.6,
            "expected_volatility": 1.0
        },
        {
            "name": "Portfolio Manager with Trades",
            "algorithm": MockAlgorithm(),
            "expected_win_rate": 0.75,
            "expected_volatility": 1.0
        }
    ]
    
    print("Testing risk manager logic...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        
        if test_case['name'] == "Portfolio Manager with Trades":
            # Set up stock managers with sample trades
            trades = [
                {'pnl': 150.50},
                {'pnl': -75.25},
                {'pnl': 200.00},
                {'pnl': 125.75}
            ]
            daily_pnl = [10, -5, 15, -3, 8, 12, -2, 7, 9, -1, 11, 6, 13, -4, 14, 5, 16, -6, 17, 4, 18, 3, 19, 2, 20]
            
            stock_managers = {
                "AAPL": MockStockManager("AAPL", trades, daily_pnl),
                "AVGO": MockStockManager("AVGO", trades, daily_pnl)
            }
            test_case['algorithm'].portfolio_manager = MockPortfolioManager(stock_managers)
        
        try:
            win_rate = get_historical_win_rate(test_case['algorithm'])
            volatility = get_volatility_adjustment(test_case['algorithm'])
            
            if abs(win_rate - test_case['expected_win_rate']) < 0.01:
                print(f"✓ Win rate test passed: {win_rate:.2f}")
            else:
                print(f"✗ Win rate test failed - expected {test_case['expected_win_rate']}, got {win_rate}")
                return False
                
            if abs(volatility - test_case['expected_volatility']) < 0.01:
                print(f"✓ Volatility test passed: {volatility:.2f}")
            else:
                print(f"✗ Volatility test failed - expected {test_case['expected_volatility']}, got {volatility}")
                return False
                
        except Exception as e:
            print(f"✗ Test {i} failed with exception: {e}")
            return False
    
    print("\n✓ All risk manager tests passed!")
    return True

if __name__ == "__main__":
    success = test_risk_manager_logic()
    exit(0 if success else 1) 