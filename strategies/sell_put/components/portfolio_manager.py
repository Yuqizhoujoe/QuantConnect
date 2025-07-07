# type: ignore
from AlgorithmImports import *
import numpy as np
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass, field
from .stock_manager import StockManager
from shared.utils.position_utils import RiskLimits
from shared.utils.trading_criteria import (
    CriteriaManager,
    CriteriaPresets,
    DeltaCriterion,
    MarketRegimeCriterion,
    VolatilityCriterion,
    DTECriterion,
    RSICriterion,
    TrendCriterion,
)
from shared.utils.constants import (
    MAX_PNL_HISTORY_LENGTH,
)

if TYPE_CHECKING:
    from ..sell_put_strategy import SellPutOptionStrategy


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
        Initialize StockManager instances for each configured stock and set up criteria managers.

        Args:
            stocks_config: List of stock configuration dictionaries
        """
        for stock_config in stocks_config:
            ticker = stock_config["ticker"]
            if stock_config.get("enabled", True):
                # Create stock manager
                stock_manager = StockManager(
                    strategy=self.strategy, ticker=ticker, config=stock_config
                )
                self.stock_managers[ticker] = stock_manager
                
                # Set up criteria manager for this stock
                self._setup_criteria_manager(stock_manager, stock_config)
                
                self.strategy.Log(f"Initialized StockManager for {ticker}")

    def _setup_criteria_manager(self, stock_manager: StockManager, stock_config: dict) -> None:
        """
        Set up criteria manager for a stock based on its configuration.
        
        Args:
            stock_manager: StockManager instance
            stock_config: Stock-specific configuration dictionary
        """
        ticker = stock_manager.ticker
        
        # Get criteria configuration from stock config
        criteria_config = stock_config.get("criteria", {})
        criteria_type = criteria_config.get("type", "delta_only")
        
        self.strategy.Log(f"{ticker}: Setting up criteria manager of type: {criteria_type}")
        
        # Create criteria manager based on configuration
        criteria_manager = self._create_criteria_manager(criteria_config)
        
        # Set the criteria manager for this stock's position manager's market analyzer
        if stock_manager.position_manager and stock_manager.position_manager.market_analyzer:
            stock_manager.position_manager.market_analyzer.set_criteria(criteria_manager)
            self.strategy.Log(f"{ticker}: Criteria manager configured")
        else:
            self.strategy.Log(f"{ticker}: Warning - No market analyzer available")

    def _create_criteria_manager(self, criteria_config: dict) -> CriteriaManager:
        """
        Create a criteria manager based on criteria configuration.
        
        Args:
            criteria_config: Criteria configuration dictionary
            
        Returns:
            Configured CriteriaManager instance
        """
        criteria_type = criteria_config.get("type", "delta_only")
        
        if criteria_type == "delta_only":
            # Use delta-only preset
            manager = CriteriaPresets.delta_only()
            
        elif criteria_type == "custom":
            # Create custom criteria manager
            manager = CriteriaManager()
            
            # Add delta criterion
            delta_config = criteria_config.get("delta", {})
            delta_range = delta_config.get("range", (0.25, 0.75))
            delta_weight = delta_config.get("weight", 1.0)
            manager.add_criterion(DeltaCriterion(target_range=delta_range, weight=delta_weight))
            
            # Add volatility criterion if specified
            vol_config = criteria_config.get("volatility", {})
            if vol_config.get("enabled", False):
                max_vol = vol_config.get("max_volatility", 0.5)
                vol_weight = vol_config.get("weight", 0.7)
                manager.add_criterion(VolatilityCriterion(max_volatility=max_vol, weight=vol_weight))
            
            # Add market regime criterion if specified
            regime_config = criteria_config.get("market_regime", {})
            if regime_config.get("enabled", False):
                allowed_regimes = regime_config.get("allowed_regimes", ["bullish_low_vol", "neutral_normal_vol"])
                regime_weight = regime_config.get("weight", 0.8)
                manager.add_criterion(MarketRegimeCriterion(allowed_regimes=allowed_regimes, weight=regime_weight))
            
            # Add DTE criterion if specified
            dte_config = criteria_config.get("dte", {})
            if dte_config.get("enabled", False):
                dte_range = dte_config.get("range", (14, 45))
                dte_weight = dte_config.get("weight", 0.6)
                manager.add_criterion(DTECriterion(min_dte=dte_range[0], max_dte=dte_range[1], weight=dte_weight))
            
            # Add RSI criterion if specified
            rsi_config = criteria_config.get("rsi", {})
            if rsi_config.get("enabled", False):
                oversold = rsi_config.get("oversold", 30)
                overbought = rsi_config.get("overbought", 70)
                rsi_weight = rsi_config.get("weight", 0.8)
                manager.add_criterion(RSICriterion(oversold=oversold, overbought=overbought, weight=rsi_weight))
            
            # Add trend criterion if specified
            trend_config = criteria_config.get("trend", {})
            if trend_config.get("enabled", False):
                allowed_directions = trend_config.get("allowed_directions", ["bullish", "neutral"])
                trend_weight = trend_config.get("weight", 0.7)
                manager.add_criterion(TrendCriterion(allowed_directions=allowed_directions, weight=trend_weight))
        
        else:
            # Default to delta-only if unknown type
            self.strategy.Log(f"Unknown criteria type '{criteria_type}', using delta_only")
            manager = CriteriaPresets.delta_only()
        
        # Log the criteria configuration
        self.strategy.Log(f"Criteria manager created: {manager.get_criteria_summary()}")
        
        return manager

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
        Simplified opportunity scoring focused on delta availability.

        Args:
            stock_manager: StockManager instance to evaluate

        Returns:
            Score (higher is better)
        """
        score = 0.0

        # Base score from weight
        score += stock_manager.weight * 10

        # Check if we have price data (indicates delta availability)
        if stock_manager.price_history:
            score += 5.0  # Bonus for having price data

        # Check if we have recent data (within last few days)
        if len(stock_manager.price_history) >= 5:
            score += 3.0  # Bonus for sufficient data history

        # Simple check for data quality
        if stock_manager.data_handler and stock_manager.data_handler.latest_slice:
            score += 2.0  # Bonus for having current market data

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
