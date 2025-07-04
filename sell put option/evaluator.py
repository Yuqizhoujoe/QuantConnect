
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
        Enhanced end-of-algorithm evaluation with comprehensive performance metrics.
        """
        self.algorithm.Log("=== ENHANCED STRATEGY COMPLETE ===")
        self.algorithm.Log(f"Ticker: {self.algorithm.ticker}")
        self.algorithm.Log(f"Total Trades: {self.algorithm.trade_count}")
        self.algorithm.Log(f"Final Portfolio Value: ${self.algorithm.Portfolio.TotalPortfolioValue:.2f}")
        self.algorithm.Log(f"Total P&L: ${self.algorithm.profit_loss:.2f}")
        
        # Calculate drawdown
        max_drawdown = (self.algorithm.peak_portfolio_value - self.algorithm.Portfolio.TotalPortfolioValue) / self.algorithm.peak_portfolio_value
        self.algorithm.Log(f"Maximum Drawdown: {max_drawdown:.2%}")

        if self.algorithm.trades:
            # Enhanced trade analysis
            completed_trades = [t for t in self.algorithm.trades if 'pnl' in t]
            if completed_trades:
                # Initialize variables to avoid scope issues
                avg_win = None
                avg_loss = None
                max_win = None
                max_loss = None
                
                # Win rate analysis
                winning_trades = [t for t in completed_trades if t['pnl'] > 0]
                win_rate = len(winning_trades) / len(completed_trades) * 100
                self.algorithm.Log(f"Win Rate: {win_rate:.1f}%")

                # Profit analysis
                if winning_trades:
                    avg_win = np.mean([t['pnl'] for t in winning_trades])
                    max_win = max([t['pnl'] for t in winning_trades])
                    self.algorithm.Log(f"Average Win: ${avg_win:.2f}")
                    self.algorithm.Log(f"Maximum Win: ${max_win:.2f}")

                # Loss analysis
                losing_trades = [t for t in completed_trades if t['pnl'] < 0]
                if losing_trades:
                    avg_loss = np.mean([t['pnl'] for t in losing_trades])
                    max_loss = min([t['pnl'] for t in losing_trades])
                    self.algorithm.Log(f"Average Loss: ${avg_loss:.2f}")
                    self.algorithm.Log(f"Maximum Loss: ${max_loss:.2f}")

                # Risk metrics - only calculate if both values are available
                if avg_win is not None and avg_loss is not None:
                    profit_factor = abs(avg_win / avg_loss)
                    self.algorithm.Log(f"Profit Factor: {profit_factor:.2f}")
                
                # Trade duration analysis
                durations = []
                for trade in completed_trades:
                    if 'entry_date' in trade and 'exit_date' in trade:
                        duration = (trade['exit_date'] - trade['entry_date']).days
                        durations.append(duration)
                
                if durations:
                    avg_duration = np.mean(durations)
                    self.algorithm.Log(f"Average Trade Duration: {avg_duration:.1f} days")
                
                # Risk-adjusted returns
                try:
                    if self.algorithm.daily_pnl and len(self.algorithm.daily_pnl) > 1:
                        returns = np.diff(self.algorithm.daily_pnl)
                        if len(returns) > 0:
                            sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
                            self.algorithm.Log(f"Sharpe Ratio: {sharpe_ratio:.2f}")
                except Exception as e:
                    self.algorithm.Log(f"Could not calculate Sharpe ratio: {str(e)}")
        
        # Risk management summary
        try:
            risk_metrics = self.algorithm.risk_manager.get_risk_metrics()
            self.algorithm.Log(f"Final Win Rate: {risk_metrics['win_rate']:.1%}")
            self.algorithm.Log(f"Final Volatility Factor: {risk_metrics['volatility']:.2f}")
        except Exception as e:
            self.algorithm.Log(f"Could not calculate final risk metrics: {str(e)}")
