
from AlgorithmImports import *
import numpy as np

class Evaluator:
    """
    Handles the performance evaluation and logging for the algorithm.
    This class calculates and displays key performance metrics at the end of the backtest.
    """
    def __init__(self, algorithm):
        """
        Initializes the Evaluator.
        
        Args:
            algorithm: A reference to the main algorithm instance.
        """
        self.algorithm = algorithm

    def on_end_of_algorithm(self):
        """
        The primary method that is called at the end of the algorithm's execution.
        It logs a summary of the strategy's performance.
        """
        self.algorithm.Log("=== STRATEGY COMPLETE ===")
        self.algorithm.Log(f"Ticker: {self.algorithm.ticker}")
        self.algorithm.Log(f"Total Trades: {self.algorithm.trade_count}")
        self.algorithm.Log(f"Final Portfolio Value: ${self.algorithm.Portfolio.TotalPortfolioValue:.2f}")
        self.algorithm.Log(f"Total P&L: ${self.algorithm.profit_loss:.2f}")

        if self.algorithm.trades:
            # Calculate and log the win rate.
            winning_trades = [t for t in self.algorithm.trades if 'pnl' in t and t['pnl'] > 0]
            win_rate = len(winning_trades) / len([t for t in self.algorithm.trades if 'pnl' in t]) * 100
            self.algorithm.Log(f"Win Rate: {win_rate:.1f}%")

            # Calculate and log the average win amount.
            if winning_trades:
                avg_win = np.mean([t['pnl'] for t in winning_trades])
                self.algorithm.Log(f"Average Win: ${avg_win:.2f}")

            # Calculate and log the average loss amount.
            losing_trades = [t for t in self.algorithm.trades if 'pnl' in t and t['pnl'] < 0]
            if losing_trades:
                avg_loss = np.mean([t['pnl'] for t in losing_trades])
                self.algorithm.Log(f"Average Loss: ${avg_loss:.2f}")
