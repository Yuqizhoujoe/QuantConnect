# type: ignore
from AlgorithmImports import *
import numpy as np
from typing import Dict, List, Any, Optional, TYPE_CHECKING
from shared.utils.position_utils import PositionUtil, RiskLimits
from shared.utils.constants import (
    DEFAULT_VOLATILITY_LOOKBACK,
    DEFAULT_VOLATILITY_THRESHOLD,
    DEFAULT_MAX_PORTFOLIO_RISK,
    DEFAULT_MAX_DRAWDOWN,
)
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from ..sell_put_strategysell_put_strategy import SellPutOptionStrategy


@dataclass
class RiskManager:
    """
    Enhanced risk management for option trading.

    This module provides comprehensive risk management including:
    - Position sizing based on portfolio value and volatility
    - Portfolio-level risk limits
    - Drawdown protection
    - Volatility-based position adjustments
    - Correlation-based risk reduction

    The goal is to maintain consistent risk exposure while maximizing returns.
    """

    strategy: "SellPutOptionStrategy"
    ticker: str
    max_portfolio_risk: float = DEFAULT_MAX_PORTFOLIO_RISK
    max_drawdown: float = DEFAULT_MAX_DRAWDOWN
    volatility_lookback: int = DEFAULT_VOLATILITY_LOOKBACK
    volatility_threshold: float = DEFAULT_VOLATILITY_THRESHOLD

    def calculate_position_size(self, contract: Any, underlying_price: float) -> int:
        """
        Calculate optimal position size using position sizing utilities.

        This method uses the PositionUtil utilities to calculate optimal
        position size based on multiple risk factors.

        Args:
            contract: Option contract to trade
            underlying_price: Current underlying price

        Returns:
            Optimal number of contracts to trade (minimum 1)
        """
        # Get trade history and daily PnL for position sizing calculations
        trades = self.get_trade_history()
        daily_pnl = self.get_daily_pnl()

        # Use position sizing utilities for optimal calculation
        portfolio_value = self.strategy.Portfolio.TotalPortfolioValue
        available_margin = self.strategy.Portfolio.MarginRemaining

        self.strategy.Log(
            f"{self.ticker} position sizing: portfolio=${portfolio_value:.2f}, margin=${available_margin:.2f}, trades={len(trades)}"
        )

        position_size = PositionUtil.calculate_optimal_position_size(
            contract,
            underlying_price,
            portfolio_value,
            available_margin,
            trades,
            daily_pnl,
            self.max_portfolio_risk,
            0.20,  # max_position_pct = 20%
        )

        self.strategy.Log(
            f"{self.ticker} calculated position size: {position_size} contracts"
        )
        return position_size

    def calculate_portfolio_risk_size(
        self, contract: Any, underlying_price: float
    ) -> int:
        """
        Calculate position size based on maximum portfolio risk per trade.

        This method ensures that no single trade can lose more than a specified
        percentage of the total portfolio value.

        Args:
            contract: Option contract to trade
            underlying_price: Current underlying price

        Returns:
            Maximum number of contracts based on portfolio risk limits
        """
        portfolio_value: float = self.strategy.Portfolio.TotalPortfolioValue
        max_risk_amount: float = portfolio_value * self.max_portfolio_risk

        # Calculate potential loss at different underlying price levels
        potential_loss: float = self.calculate_max_loss(contract, underlying_price)

        if potential_loss <= 0:
            return 1  # Minimum position size

        # Number of contracts = max risk amount / potential loss per contract
        return int(max_risk_amount / potential_loss)

    def calculate_max_loss(self, contract: Any, underlying_price: float) -> float:
        """
        Calculate maximum potential loss for a short put position.

        For short puts, the maximum loss occurs if the underlying goes to zero.
        However, we use a more realistic scenario (50% drop) for risk calculation.

        Args:
            contract: Option contract
            underlying_price: Current underlying price

        Returns:
            Maximum potential loss per contract
        """
        # Use a realistic worst-case scenario: 50% drop in underlying price
        # This is more conservative than assuming the stock goes to zero
        worst_case_price: float = underlying_price * 0.5

        # Calculate intrinsic value at worst-case price
        intrinsic_value: float = max(0, contract.Strike - worst_case_price)

        # Loss per contract = intrinsic value * 100 (contract multiplier)
        return intrinsic_value * 100

    def get_trade_history(self) -> List[Dict[str, Any]]:
        """
        Get trade history for position sizing calculations.

        Returns:
            List of trade dictionaries
        """
        trades = []
        if (
            hasattr(self.strategy, "portfolio_manager")
            and self.strategy.portfolio_manager
        ):
            for (
                stock_manager
            ) in self.strategy.portfolio_manager.stock_managers.values():
                if hasattr(stock_manager, "trades"):
                    trades.extend(stock_manager.trades)
        return trades

    def get_daily_pnl(self) -> List[float]:
        """
        Get daily PnL for volatility calculations.

        Returns:
            List of daily PnL values
        """
        daily_pnl = []
        if (
            hasattr(self.strategy, "portfolio_manager")
            and self.strategy.portfolio_manager
        ):
            for (
                stock_manager
            ) in self.strategy.portfolio_manager.stock_managers.values():
                if hasattr(stock_manager, "daily_pnl"):
                    daily_pnl.extend(stock_manager.daily_pnl)
        return daily_pnl

    def should_stop_trading(self):
        """
        Check if we should stop trading due to risk limits using position sizing utilities.

        This implements circuit breakers to protect the portfolio using the RiskLimits utilities.

        Returns:
            True if trading should be stopped, False otherwise
        """
        current_value = self.strategy.Portfolio.TotalPortfolioValue
        peak_value = self.strategy.peak_portfolio_value

        trades = self.get_trade_history()
        daily_pnl = self.get_daily_pnl()

        return RiskLimits.should_stop_trading(
            current_value,
            peak_value,
            self.max_drawdown,
            trades,
            daily_pnl,
            current_value,
            self.max_portfolio_risk,
        )
