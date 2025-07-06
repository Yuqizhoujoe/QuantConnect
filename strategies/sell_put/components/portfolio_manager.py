# type: ignore
from AlgorithmImports import *
import numpy as np
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass, field
from .stock_manager import StockManager
from shared.utils.position_utils import RiskLimits
from shared.utils.constants import (
    MAX_PNL_HISTORY_LENGTH,
    VOLATILITY_LOW_THRESHOLD,
    VOLATILITY_HIGH_THRESHOLD,
    MARKET_SCORE_BULLISH_LOW_VOL,
    MARKET_SCORE_BULLISH_NORMAL_VOL,
    MARKET_SCORE_BEARISH_HIGH_VOL,
    VOLATILITY_SCORE_LOW,
    VOLATILITY_SCORE_HIGH,
)

if TYPE_CHECKING:
    from .sell_put_strategy import SellPutOptionStrategy


@dataclass
class PortfolioManager:
    strategy: "SellPutOptionStrategy"
    total_trades: int
    portfolio_pnl: float
    peak_portfolio_value: float
    daily_portfolio_pnl: List[float]
    max_stocks: int
    max_portfolio_risk: float
    max_drawdown: float
    portfolio_returns: List[float]
    portfolio_volatility: List[float]
    stock_managers: Dict[str, StockManager] = field(default_factory=dict)

    def initialize_stocks(self, stocks_config: List[dict]) -> None:
        """
        Initialize StockManager instances for each configured stock.

        Args:
            stocks_config: List of stock configuration dictionaries
        """
        for stock_config in stocks_config:
            ticker = stock_config["ticker"]
            if stock_config.get("enabled", True):
                self.stock_managers[ticker] = StockManager(
                    strategy=self.strategy, ticker=ticker, config=stock_config
                )
                self.strategy.Log(f"Initialized StockManager for {ticker}")

    def update_portfolio_data(self, slice_data) -> None:
        """
        Update data for all stocks in the portfolio.

        Args:
            slice_data: Latest data slice from the algorithm
        """
        # Update each stock manager
        for stock_manager in self.stock_managers.values():
            stock_manager.update_data(slice_data)

        # Update portfolio performance
        self._update_portfolio_performance()

    def _update_portfolio_performance(self) -> None:
        """Update portfolio-level performance metrics."""
        current_value = self.strategy.Portfolio.TotalPortfolioValue

        # Update peak value
        if current_value > self.peak_portfolio_value:
            self.peak_portfolio_value = current_value
            self.strategy.peak_portfolio_value = current_value

        # Calculate daily PnL
        if hasattr(self, "_last_portfolio_value"):
            daily_pnl = current_value - self._last_portfolio_value
            self.daily_portfolio_pnl.append(daily_pnl)

            # Keep only recent data
            if len(self.daily_portfolio_pnl) > MAX_PNL_HISTORY_LENGTH:
                self.daily_portfolio_pnl.pop(0)

        self._last_portfolio_value = current_value

    def should_trade_portfolio(self) -> bool:
        """
        Determine if the portfolio should trade based on overall conditions.

        Returns:
            True if portfolio should trade, False otherwise
        """
        self.strategy.Log(
            f"should_trade_portfolio called - max_stocks: {self.max_stocks}"
        )

        # Check portfolio-level risk limits
        if self._check_portfolio_risk_limits():
            self.strategy.Log("Portfolio risk limits exceeded")
            return False

        # Check correlation limits (simplified - correlation not critical)
        # if self.correlation_manager.should_reduce_trading():  # Disabled
        #     return False

        # Check if we have too many open positions
        open_positions = self._count_open_positions()
        self.strategy.Log(f"Open positions: {open_positions}/{self.max_stocks}")
        if open_positions >= self.max_stocks:
            self.strategy.Log("Maximum number of open positions reached")
            return False

        self.strategy.Log("Portfolio should trade")
        return True

    def _check_portfolio_risk_limits(self) -> bool:
        """
        Check if portfolio risk limits are exceeded using position sizing utilities.

        Returns:
            True if risk limits exceeded, False otherwise
        """
        current_value = self.strategy.Portfolio.TotalPortfolioValue

        # Check drawdown using position sizing utilities
        if RiskLimits.check_drawdown_limit(
            current_value, self.peak_portfolio_value, self.max_drawdown
        ):
            self.strategy.Log(f"Portfolio drawdown limit exceeded")
            return True

        # Check portfolio volatility using position sizing utilities
        if RiskLimits.check_portfolio_volatility(
            self.daily_portfolio_pnl, current_value, self.max_portfolio_risk
        ):
            self.strategy.Log(f"Portfolio volatility limit exceeded")
            return True

        return False

    def _count_open_positions(self) -> int:
        """Count the number of stocks with open positions."""
        count = 0
        for stock_manager in self.stock_managers.values():
            if (
                stock_manager.current_contract
                and self.strategy.Portfolio[
                    stock_manager.current_contract.Symbol
                ].Invested
            ):
                count += 1
        return count

    def manage_positions(self) -> None:
        """
        Manage all positions in the portfolio.
        """
        try:
            self.strategy.Log(
                f"manage_positions called - {len(self.stock_managers)} stock managers"
            )

            # First, check for positions that should be closed
            for stock_manager in self.stock_managers.values():
                if stock_manager.should_close_position():
                    self.strategy.Log(f"Closing position for {stock_manager.ticker}")
                    stock_manager.close_position()

            # Then, look for new trading opportunities
            if not self.should_trade_portfolio():
                self.strategy.Log("Portfolio should not trade - skipping new positions")
                return

            # Find the best trading opportunity
            best_stock = self._find_best_trading_opportunity()
            if best_stock:
                self.strategy.Log(
                    f"Found best trading opportunity: {best_stock.ticker}"
                )
                best_stock.find_and_enter_position()
            else:
                self.strategy.Log("No suitable trading opportunities found")
        except Exception as e:
            self.strategy.Log(f"Error in manage_positions: {str(e)}")

    def _find_best_trading_opportunity(self) -> Optional[StockManager]:
        """
        Find the best stock to trade based on multiple criteria.

        Returns:
            StockManager instance for the best opportunity, or None
        """
        self.strategy.Log("_find_best_trading_opportunity called")
        opportunities: List[Tuple[StockManager, float]] = []

        for stock_manager in self.stock_managers.values():
            self.strategy.Log(
                f"Checking {stock_manager.ticker} for trading opportunity"
            )
            if not stock_manager.should_trade():
                self.strategy.Log(f"{stock_manager.ticker} should not trade")
                continue

            # Calculate opportunity score
            score = self._calculate_opportunity_score(stock_manager)
            self.strategy.Log(f"{stock_manager.ticker} opportunity score: {score:.2f}")
            if score > 0:
                opportunities.append((stock_manager, score))

        # Sort by score and return the best
        if opportunities:
            opportunities.sort(key=lambda x: x[1], reverse=True)
            best_stock = opportunities[0][0]
            self.strategy.Log(
                f"Best opportunity: {best_stock.ticker} with score {opportunities[0][1]:.2f}"
            )
            return best_stock

        self.strategy.Log("No opportunities found")
        return None

    def _calculate_opportunity_score(self, stock_manager: StockManager) -> float:
        """
        Calculate a score for trading opportunity quality.

        Args:
            stock_manager: StockManager instance to evaluate

        Returns:
            Score (higher is better)
        """
        score = 0.0

        # Base score from weight
        score += stock_manager.weight * 10

        # Market condition bonus
        market_analysis = stock_manager.market_analyzer.analyze_market_conditions(
            stock_manager.price_history[-1] if stock_manager.price_history else 0
        )

        if market_analysis.market_regime.value == "bullish_low_vol":
            score += MARKET_SCORE_BULLISH_LOW_VOL
        elif market_analysis.market_regime.value == "bullish_normal_vol":
            score += MARKET_SCORE_BULLISH_NORMAL_VOL
        elif market_analysis.market_regime.value == "bearish_high_vol":
            score += MARKET_SCORE_BEARISH_HIGH_VOL

        # Volatility bonus (prefer lower volatility)
        volatility = market_analysis.volatility.current
        if volatility < VOLATILITY_LOW_THRESHOLD:
            score += VOLATILITY_SCORE_LOW
        elif volatility > VOLATILITY_HIGH_THRESHOLD:
            score += VOLATILITY_SCORE_HIGH

        # Correlation penalty (simplified - correlation not critical)
        # correlation = self.correlation_manager.get_stock_correlation(stock_manager.ticker)  # Disabled
        # if correlation > 0.8:
        #     score -= 5
        # elif correlation < 0.3:
        #     score += 3

        return score

    def get_portfolio_metrics(self) -> dict:
        """
        Get comprehensive portfolio performance metrics.

        Returns:
            Dictionary with portfolio metrics
        """
        # Calculate total trades from all stock managers
        total_trades = sum(
            stock_manager.trade_count for stock_manager in self.stock_managers.values()
        )

        # Calculate total portfolio PnL from all stock managers
        total_portfolio_pnl = sum(
            stock_manager.profit_loss for stock_manager in self.stock_managers.values()
        )

        metrics = {
            "total_trades": total_trades,
            "portfolio_pnl": total_portfolio_pnl,
            "current_value": self.strategy.Portfolio.TotalPortfolioValue,
            "peak_value": self.peak_portfolio_value,
            "drawdown": (
                self.peak_portfolio_value - self.strategy.Portfolio.TotalPortfolioValue
            )
            / self.peak_portfolio_value,
            "open_positions": self._count_open_positions(),
            "stock_metrics": {},
        }

        # Add individual stock metrics
        for ticker, stock_manager in self.stock_managers.items():
            metrics["stock_metrics"][ticker] = stock_manager.get_performance_metrics()

        return metrics

    def get_correlation_matrix(self) -> dict:
        """
        Get the correlation matrix for all stocks.

        Returns:
            Correlation matrix as a dictionary (simplified - returns empty dict)
        """
        return {}  # Simplified - correlation not critical

    def adjust_allocations(self) -> None:
        """
        Dynamically adjust stock allocations based on performance and correlation.
        """
        # This could implement dynamic allocation adjustments
        # based on performance, correlation, and market conditions
        pass
