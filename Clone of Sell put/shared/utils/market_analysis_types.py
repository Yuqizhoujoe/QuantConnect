# region imports
from AlgorithmImports import *
# endregion
"""
Type definitions for market analysis data structures.
This module provides proper types for market analysis results to improve type safety and code maintainability.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum


class MarketRegime(Enum):
    """Enumeration of possible market regimes."""

    BULLISH_LOW_VOL = "bullish_low_vol"
    BULLISH_NORMAL_VOL = "bullish_normal_vol"
    BULLISH_HIGH_VOL = "bullish_high_vol"
    BEARISH_LOW_VOL = "bearish_low_vol"
    BEARISH_NORMAL_VOL = "bearish_normal_vol"
    BEARISH_HIGH_VOL = "bearish_high_vol"
    NEUTRAL_LOW_VOL = "neutral_low_vol"
    NEUTRAL_NORMAL_VOL = "neutral_normal_vol"
    NEUTRAL_HIGH_VOL = "neutral_high_vol"
    UNKNOWN = "unknown"


@dataclass
class VolatilityData:
    """Data structure for volatility information."""

    current: float
    historical_vol: float
    percentile: float
    regime: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for backward compatibility."""
        return {
            "current": self.current,
            "historical_vol": self.historical_vol,
            "percentile": self.percentile,
            "regime": self.regime,
        }


@dataclass
class TrendData:
    """Data structure for trend information."""

    direction: str  # "up", "down", "sideways"
    strength: float  # 0.0 to 1.0
    duration_days: int
    is_strong: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for backward compatibility."""
        return {
            "direction": self.direction,
            "strength": self.strength,
            "duration_days": self.duration_days,
            "is_strong": self.is_strong,
        }


@dataclass
class SupportResistanceData:
    """Data structure for support and resistance levels."""

    support_level: float
    resistance_level: float
    current_distance_to_support: float
    current_distance_to_resistance: float
    is_near_support: bool
    is_near_resistance: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for backward compatibility."""
        return {
            "support_level": self.support_level,
            "resistance_level": self.resistance_level,
            "current_distance_to_support": self.current_distance_to_support,
            "current_distance_to_resistance": self.current_distance_to_resistance,
            "is_near_support": self.is_near_support,
            "is_near_resistance": self.is_near_resistance,
        }


@dataclass
class MarketAnalysis:
    """
    Comprehensive market analysis data structure.

    This class encapsulates all market analysis results in a type-safe manner,
    replacing dictionary returns with proper structured data.
    """

    # Core market regime
    market_regime: MarketRegime

    # Price and trend information
    underlying_price: float
    trend: TrendData

    # Volatility analysis
    volatility: VolatilityData

    # Support and resistance levels
    support_resistance: SupportResistanceData

    # Technical indicators
    rsi: float  # Relative Strength Index (0-100)

    # Risk metrics
    risk_score: float  # 0.0 to 1.0, higher = more risky
    confidence_score: float  # 0.0 to 1.0, higher = more confident

    # Trading recommendations
    should_trade: bool
    recommended_delta_range: tuple[float, float]
    recommended_dte_range: tuple[int, int]

    # Additional metadata
    analysis_timestamp: Optional[str] = None
    data_quality_score: float = 1.0  # 0.0 to 1.0

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for backward compatibility with existing code.

        Returns:
            Dictionary representation of the market analysis
        """
        return {
            "market_regime": self.market_regime.value,
            "underlying_price": self.underlying_price,
            "trend": self.trend.to_dict(),
            "volatility": self.volatility.to_dict(),
            "support_resistance": self.support_resistance.to_dict(),
            "rsi": self.rsi,
            "risk_score": self.risk_score,
            "confidence_score": self.confidence_score,
            "should_trade": self.should_trade,
            "recommended_delta_range": self.recommended_delta_range,
            "recommended_dte_range": self.recommended_dte_range,
            "analysis_timestamp": self.analysis_timestamp,
            "data_quality_score": self.data_quality_score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MarketAnalysis":
        """
        Create MarketAnalysis instance from dictionary.

        Args:
            data: Dictionary containing market analysis data

        Returns:
            MarketAnalysis instance
        """
        return cls(
            market_regime=MarketRegime(data.get("market_regime", "unknown")),
            underlying_price=data.get("underlying_price", 0.0),
            trend=TrendData(**data.get("trend", {})),
            volatility=VolatilityData(**data.get("volatility", {})),
            support_resistance=SupportResistanceData(
                **data.get("support_resistance", {})
            ),
            rsi=data.get("rsi", 50.0),
            risk_score=data.get("risk_score", 0.5),
            confidence_score=data.get("confidence_score", 0.5),
            should_trade=data.get("should_trade", False),
            recommended_delta_range=data.get("recommended_delta_range", (0.25, 0.75)),
            recommended_dte_range=data.get("recommended_dte_range", (14, 45)),
            analysis_timestamp=data.get("analysis_timestamp"),
            data_quality_score=data.get("data_quality_score", 1.0),
        )


@dataclass
class TradingSignal:
    """Data structure for trading signals."""

    signal_type: str  # "buy", "sell", "hold", "close"
    strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    reasoning: str
    risk_level: str  # "low", "medium", "high"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for backward compatibility."""
        return {
            "signal_type": self.signal_type,
            "strength": self.strength,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "risk_level": self.risk_level,
        }

