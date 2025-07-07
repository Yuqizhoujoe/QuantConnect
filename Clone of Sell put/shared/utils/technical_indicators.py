# region imports
from AlgorithmImports import *
# endregion
"""
Technical Analysis Utilities

This module provides reusable technical analysis functions that can be used
across different strategies and components.
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Union
from datetime import date


class TechnicalIndicators:
    """Collection of reusable technical analysis functions."""

    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> float:
        """Calculate Simple Moving Average."""
        if len(prices) < period:
            return prices[-1] if prices else 0
        return float(np.mean(prices[-period:]))

    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return prices[-1] if prices else 0

        alpha = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = alpha * price + (1 - alpha) * ema
        return ema

    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return 50.0  # Neutral RSI

        # Calculate price changes
        changes = np.diff(prices)
        gains = np.where(changes > 0, changes, 0)
        losses = np.where(changes < 0, -changes, 0)

        # Calculate average gains and losses
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi)

    @staticmethod
    def calculate_volatility(prices: List[float], period: int = 20) -> float:
        """Calculate price volatility (standard deviation of returns)."""
        if len(prices) < period + 1:
            return 0.2  # Default volatility

        # Calculate log returns
        returns = np.diff(np.log(prices))
        recent_returns = returns[-period:]

        # Annualized volatility
        volatility = np.std(recent_returns) * np.sqrt(252)
        return float(volatility)

    @staticmethod
    def find_support_resistance(
        prices: List[float], lookback: int = 20
    ) -> Dict[str, Any]:
        """Find support and resistance levels."""
        if len(prices) < lookback:
            return {"support": 0, "resistance": float("inf")}

        recent_prices = prices[-lookback:]
        recent_high = max(recent_prices)
        recent_low = min(recent_prices)
        current_price = prices[-1]

        distance_to_resistance = (recent_high - current_price) / current_price
        distance_to_support = (current_price - recent_low) / current_price

        return {
            "support": recent_low,
            "resistance": recent_high,
            "distance_to_resistance": distance_to_resistance,
            "distance_to_support": distance_to_support,
        }

    @staticmethod
    def determine_trend(prices: List[float], ma_period: int = 50) -> str:
        """Determine price trend using moving average."""
        if len(prices) < ma_period:
            return "neutral"

        current_price = prices[-1]
        ma = TechnicalIndicators.calculate_sma(prices, ma_period)

        if current_price > ma * 1.02:  # 2% above MA = bullish
            return "bullish"
        elif current_price < ma * 0.98:  # 2% below MA = bearish
            return "neutral"
        else:
            return "neutral"

    @staticmethod
    def classify_volatility_regime(current_vol: float, historical_vol: float) -> str:
        """Classify volatility regime."""
        if current_vol > historical_vol * 1.5:
            return "high"
        elif current_vol < historical_vol * 0.7:
            return "low"
        else:
            return "normal"

    @staticmethod
    def determine_market_regime(trend: str, volatility_regime: str, rsi: float) -> str:
        """Determine overall market regime."""
        if trend == "bullish" and volatility_regime == "low":
            return "bullish_low_vol"
        elif trend == "bullish" and volatility_regime == "high":
            return "bullish_high_vol"
        elif trend == "bearish" and volatility_regime == "low":
            return "bearish_low_vol"
        elif trend == "bearish" and volatility_regime == "high":
            return "bearish_high_vol"
        elif rsi > 70:
            return "overbought"
        elif rsi < 30:
            return "oversold"
        else:
            return "neutral"

    @staticmethod
    def should_avoid_trading(
        market_regime: str, rsi: float, volatility_regime: str
    ) -> bool:
        """Determine if trading should be avoided."""
        if market_regime in ["overbought", "oversold"]:
            return True
        if volatility_regime == "high" and market_regime in ["bearish_high_vol"]:
            return True
        if rsi > 80 or rsi < 20:
            return True
        return False


class OptionAnalysis:
    """Option-specific analysis utilities."""

    @staticmethod
    def get_optimal_delta_range(market_regime: str) -> Tuple[float, float]:
        """Get optimal delta range based on market conditions."""
        if market_regime == "bullish_low_vol":
            return (0.3, 0.8)  # More aggressive
        elif market_regime == "bearish_high_vol":
            return (0.15, 0.4)  # More conservative
        elif market_regime == "overbought":
            return (0.2, 0.5)  # Conservative
        elif market_regime == "oversold":
            return (0.3, 0.7)  # Moderate
        else:
            return (0.25, 0.75)  # Default range

    @staticmethod
    def get_optimal_dte_range(
        market_regime: str, volatility_regime: str
    ) -> Tuple[int, int]:
        """Get optimal days to expiration range."""
        if market_regime == "bearish_high_vol":
            return (45, 90)  # Longer DTE to avoid assignment risk
        elif volatility_regime == "high":
            return (30, 60)  # Medium DTE in high volatility
        elif volatility_regime == "low":
            return (21, 45)  # Shorter DTE to capture time decay
        else:
            return (30, 60)  # Default range

    @staticmethod
    def is_valid_option_expiry(expiry: date, frequency: str) -> bool:
        """Check if option expiry matches frequency."""
        if frequency == "monthly":
            # Monthly options typically expire on the 3rd Friday
            return expiry.weekday() == 4 and 15 <= expiry.day <= 21
        elif frequency == "weekly":
            # Weekly options typically expire on Fridays
            return expiry.weekday() == 4
        elif frequency == "any":
            return True
        return False


class PerformanceMetrics:
    """Performance calculation utilities."""

    @staticmethod
    def calculate_win_rate(trades: List[Dict[str, Any]]) -> float:
        """Calculate win rate from trades."""
        completed_trades = [t for t in trades if "pnl" in t]
        if not completed_trades:
            return 0.6  # Default assumption

        winning_trades = [t for t in completed_trades if t["pnl"] > 0]
        return len(winning_trades) / len(completed_trades)

    @staticmethod
    def calculate_average_win(trades: List[Dict[str, Any]]) -> float:
        """Calculate average winning trade amount."""
        completed_trades = [t for t in trades if "pnl" in t and t["pnl"] > 0]
        if not completed_trades:
            return 100  # Default assumption
        return float(np.mean([t["pnl"] for t in completed_trades]))

    @staticmethod
    def calculate_average_loss(trades: List[Dict[str, Any]]) -> float:
        """Calculate average losing trade amount."""
        completed_trades = [t for t in trades if "pnl" in t and t["pnl"] < 0]
        if not completed_trades:
            return 200  # Default assumption
        return abs(float(np.mean([t["pnl"] for t in completed_trades])))

    @staticmethod
    def calculate_drawdown(peak_value: float, current_value: float) -> float:
        """Calculate drawdown percentage."""
        if peak_value <= 0:
            return 0.0
        return (peak_value - current_value) / peak_value

