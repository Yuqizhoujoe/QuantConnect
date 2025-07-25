# type: ignore
from AlgorithmImports import *
import numpy as np
from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from ..sell_put_strategy import SellPutOptionStrategy


@dataclass
class Evaluator:
    """
    Handles the performance evaluation and logging for the algorithm.
    This class calculates and displays key performance metrics at the end of the backtest.
    """

    strategy: "SellPutOptionStrategy"

    def on_end_of_algorithm(self) -> None:
        """
        Enhanced end-of-algorithm evaluation with comprehensive performance metrics.
        """
        self.strategy.Log("=== ENHANCED STRATEGY COMPLETE ===")

        # Get portfolio metrics from portfolio manager
        if hasattr(self.strategy, "portfolio_manager"):
            portfolio_metrics = self.strategy.portfolio_manager.get_portfolio_metrics()

            # Log basic portfolio information
            self.strategy.Log(
                f"Final Portfolio Value: ${self.strategy.Portfolio.TotalPortfolioValue:.2f}"
            )
            self.strategy.Log(
                f"Total Trades: {portfolio_metrics.get('total_trades', 0)}"
            )
            self.strategy.Log(
                f"Open Positions: {portfolio_metrics.get('open_positions', 0)}"
            )
            self.strategy.Log(f"Drawdown: {portfolio_metrics.get('drawdown', 0):.2%}")

            # Log individual stock performance
            stock_metrics = portfolio_metrics.get("stock_metrics", {})
            if stock_metrics:
                self.strategy.Log("=== INDIVIDUAL STOCK PERFORMANCE ===")
                for ticker, metrics in stock_metrics.items():
                    self.strategy.Log(
                        f"{ticker}: {metrics.get('trade_count', 0)} trades, "
                        f"P&L: ${metrics.get('profit_loss', 0):.2f}"
                    )

            # Aggregate all trades from all stock managers
            all_trades = []
            total_pnl = 0.0

            for (
                stock_manager
            ) in self.strategy.portfolio_manager.stock_managers.values():
                if hasattr(stock_manager, "trades"):
                    all_trades.extend(stock_manager.trades)
                if hasattr(stock_manager, "profit_loss"):
                    total_pnl += stock_manager.profit_loss

            self.strategy.Log(f"Total P&L: ${total_pnl:.2f}")

            # Enhanced trade analysis if we have trades
            if all_trades:
                completed_trades = [t for t in all_trades if "pnl" in t]
                if completed_trades:
                    # Initialize variables to avoid scope issues
                    avg_win: Optional[float] = None
                    avg_loss: Optional[float] = None
                    max_win: Optional[float] = None
                    max_loss: Optional[float] = None

                    # Win rate analysis
                    winning_trades = [t for t in completed_trades if t["pnl"] > 0]
                    win_rate = len(winning_trades) / len(completed_trades) * 100
                    self.strategy.Log(f"Win Rate: {win_rate:.1f}%")

                    # Profit analysis
                    if winning_trades:
                        avg_win = np.mean([t["pnl"] for t in winning_trades])
                        max_win = max([t["pnl"] for t in winning_trades])
                        self.strategy.Log(f"Average Win: ${avg_win:.2f}")
                        self.strategy.Log(f"Maximum Win: ${max_win:.2f}")

                    # Loss analysis
                    losing_trades = [t for t in completed_trades if t["pnl"] < 0]
                    if losing_trades:
                        avg_loss = np.mean([t["pnl"] for t in losing_trades])
                        max_loss = min([t["pnl"] for t in losing_trades])
                        self.strategy.Log(f"Average Loss: ${avg_loss:.2f}")
                        self.strategy.Log(f"Maximum Loss: ${max_loss:.2f}")

                    # Risk metrics - only calculate if both values are available
                    if avg_win is not None and avg_loss is not None and avg_loss != 0:
                        profit_factor = abs(avg_win / avg_loss)
                        self.strategy.Log(f"Profit Factor: {profit_factor:.2f}")

                    # Trade duration analysis
                    durations = []
                    for trade in completed_trades:
                        if "date" in trade and "exit_date" in trade:
                            duration = (trade["exit_date"] - trade["date"]).days
                            durations.append(duration)

                    if durations:
                        avg_duration = np.mean(durations)
                        self.strategy.Log(
                            f"Average Trade Duration: {avg_duration:.1f} days"
                        )

                    # Risk-adjusted returns
                    try:
                        # Collect daily PnL from all stock managers
                        all_daily_pnl = []
                        for (
                            stock_manager
                        ) in self.strategy.portfolio_manager.stock_managers.values():
                            if hasattr(stock_manager, "daily_pnl"):
                                all_daily_pnl.extend(stock_manager.daily_pnl)

                        if all_daily_pnl and len(all_daily_pnl) > 1:
                            returns = np.diff(all_daily_pnl)
                            if len(returns) > 0 and np.std(returns) > 0:
                                sharpe_ratio = np.mean(returns) / np.std(returns)
                                self.strategy.Log(f"Sharpe Ratio: {sharpe_ratio:.2f}")
                    except Exception as e:
                        self.strategy.Log(f"Could not calculate Sharpe ratio: {str(e)}")

            # Risk management summary
            try:
                if hasattr(self.strategy, "risk_manager"):
                    risk_metrics = self.strategy.risk_manager.get_risk_metrics()
                    self.strategy.Log(
                        f"Final Win Rate: {risk_metrics.get('win_rate', 0):.1%}"
                    )
                    self.strategy.Log(
                        f"Final Volatility Factor: {risk_metrics.get('volatility', 0):.2f}"
                    )
            except Exception as e:
                self.strategy.Log(f"Could not calculate final risk metrics: {str(e)}")
        else:
            self.strategy.Log("Portfolio manager not available for evaluation")
