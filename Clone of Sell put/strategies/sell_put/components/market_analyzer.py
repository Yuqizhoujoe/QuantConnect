from AlgorithmImports import *  # type: ignore
from typing import Dict, List, Any, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass, field
import numpy as np
from shared.utils.market_analysis_types import (
    MarketAnalysis,
    MarketRegime,
    TrendData,
    VolatilityData,
    SupportResistanceData,
)
from shared.utils.trading_criteria import (
    CriteriaManager,
    CriteriaPresets,
    DeltaCriterion,
    MarketRegimeCriterion,
    VolatilityCriterion,
    DTECriterion,
    RSICriterion,
    TrendCriterion,
    TradingContext,
)

if TYPE_CHECKING:
    from ..sell_put_strategy import SellPutOptionStrategy


@dataclass
class MarketAnalyzer:
    """
    Market analysis for option trading decisions using modular criteria system.

    Provides essential market analysis including:
    - Trend analysis using moving averages
    - Volatility analysis
    - Market regime detection
    - Dynamic parameter adjustment
    - Modular criteria evaluation
    """

    strategy: "SellPutOptionStrategy"
    ticker: str

    # Analysis parameters
    volatility_lookback: int = 20
    rsi_period: int = 14
    moving_average_period: int = 50

    # Data storage
    price_history: List[float] = field(default_factory=list)
    volatility_history: List[float] = field(default_factory=list)

    # Criteria manager
    criteria_manager: Optional[CriteriaManager] = field(default=None, init=False)

    def __post_init__(self):
        """Initialize the criteria manager with default criteria."""
        # Start with delta-only criteria (can be customized later)
        self.criteria_manager = CriteriaPresets.delta_only()

    def set_criteria(self, criteria_manager: CriteriaManager) -> None:
        """Set custom criteria for this analyzer."""
        self.criteria_manager = criteria_manager
        self.strategy.Log(f"{self.ticker}: Updated criteria: {criteria_manager.get_criteria_summary()}")

    def analyze_market_conditions(self, underlying_price: float) -> MarketAnalysis:
        """
        Market analysis using modular criteria system.
        
        Evaluates all criteria and determines if trading should proceed.
        """
        self.update_price_history(underlying_price)

        # Perform market analysis
        trend_data = self._analyze_trend()
        volatility_data = self._analyze_volatility()
        support_resistance_data = self._analyze_support_resistance()
        market_regime = self._determine_market_regime(trend_data, volatility_data)
        rsi = self._calculate_rsi()

        # Create context for criteria evaluation
        context = self._create_evaluation_context(
            underlying_price, trend_data, volatility_data, 
            market_regime, rsi
        )

        # Evaluate criteria
        if self.criteria_manager:
            should_trade, score, message = self.criteria_manager.should_trade(context)
        else:
            should_trade, score, message = True, 1.0, "No criteria manager - allowing trade"
        
        self.strategy.Log(f"{self.ticker}: Criteria evaluation - {message}")

        return MarketAnalysis(
            market_regime=market_regime,
            underlying_price=underlying_price,
            trend=trend_data,
            volatility=volatility_data,
            support_resistance=support_resistance_data,
            rsi=rsi,
            risk_score=1.0 - score,  # Invert score for risk (lower is better)
            confidence_score=score,
            should_trade=should_trade,
            recommended_delta_range=self.get_optimal_delta_range(market_regime, volatility_data),
            recommended_dte_range=self.get_optimal_dte_range(volatility_data),
            analysis_timestamp=str(self.strategy.Time),
            data_quality_score=score,
        )

    def _create_evaluation_context(
        self, 
        underlying_price: float,
        trend_data: TrendData,
        volatility_data: VolatilityData,
        market_regime: MarketRegime,
        rsi: float
    ) -> TradingContext:
        """Create TradingContext for criteria evaluation."""
        return TradingContext(
            underlying_price=underlying_price,
            trend_direction=trend_data.direction,
            trend_strength=trend_data.strength,
            volatility=volatility_data.current,
            market_regime=market_regime.value,
            rsi=rsi,
            dte=30,  # Default DTE - will be updated by position manager
            delta=0.5,  # Default delta - will be updated by position manager
            timestamp=str(self.strategy.Time),
        )

    def get_optimal_delta_range(
        self, market_regime: MarketRegime, volatility_data: VolatilityData
    ) -> Tuple[float, float]:
        """
        Get optimal delta range based on market conditions.
        
        This method can be customized based on the criteria manager.
        """
        # For now, return fixed range - can be made dynamic based on criteria
        return (0.25, 0.75)

    def get_optimal_dte_range(self, volatility_data: VolatilityData) -> Tuple[int, int]:
        """
        Get optimal DTE range based on volatility.
        
        This method can be customized based on the criteria manager.
        """
        # For now, return fixed range - can be made dynamic based on criteria
        return (14, 45)

    def update_price_history(self, price: float) -> None:
        """Update price history for analysis."""
        self.price_history.append(price)
        if len(self.price_history) > self.volatility_lookback:
            self.price_history.pop(0)

    def _analyze_trend(self) -> TrendData:
        """Analyze price trend."""
        if len(self.price_history) < self.moving_average_period:
            return TrendData(
                direction="neutral", strength=0.5, duration_days=0, is_strong=False
            )

        current_price = self.price_history[-1]
        ma = float(np.mean(self.price_history[-self.moving_average_period :]))

        if current_price > ma * 1.02:
            direction = "bullish"
        elif current_price < ma * 0.98:
            direction = "bearish"
        else:
            direction = "neutral"

        strength = min(1.0, abs(current_price - ma) / ma)
        is_strong = strength > 0.05

        return TrendData(
            direction=direction,
            strength=strength,
            duration_days=min(30, len(self.price_history)),
            is_strong=is_strong,
        )

    def _analyze_volatility(self) -> VolatilityData:
        """Analyze price volatility."""
        if len(self.price_history) < 10:
            return VolatilityData(
                current=0.2, historical_vol=0.2, percentile=0.5, regime="normal"
            )

        returns = np.diff(np.log(self.price_history))
        current_vol = np.std(returns[-5:]) * np.sqrt(252)
        historical_vol = np.std(returns) * np.sqrt(252)

        self.volatility_history.append(current_vol)
        if len(self.volatility_history) > 50:
            self.volatility_history.pop(0)

        percentile = (
            sum(1 for v in self.volatility_history if v < current_vol)
            / len(self.volatility_history)
            if len(self.volatility_history) > 1
            else 0.5
        )

        if current_vol > historical_vol * 1.5:
            regime = "high"
        elif current_vol < historical_vol * 0.7:
            regime = "low"
        else:
            regime = "normal"

        return VolatilityData(
            current=current_vol,
            historical_vol=historical_vol,
            percentile=percentile,
            regime=regime,
        )

    def _analyze_support_resistance(self) -> SupportResistanceData:
        """Analyze support and resistance levels."""
        if len(self.price_history) < 20:
            return SupportResistanceData(
                support_level=0,
                resistance_level=float("inf"),
                current_distance_to_support=0,
                current_distance_to_resistance=0,
                is_near_support=False,
                is_near_resistance=False,
            )

        recent_high = max(self.price_history[-20:])
        recent_low = min(self.price_history[-20:])
        current_price = self.price_history[-1]

        distance_to_resistance = (recent_high - current_price) / current_price
        distance_to_support = (current_price - recent_low) / current_price

        return SupportResistanceData(
            support_level=recent_low,
            resistance_level=recent_high,
            current_distance_to_resistance=distance_to_resistance,
            current_distance_to_support=distance_to_support,
            is_near_support=distance_to_support < current_price * 0.05,
            is_near_resistance=distance_to_resistance < current_price * 0.05,
        )

    def _determine_market_regime(
        self, trend_data: TrendData, volatility_data: VolatilityData
    ) -> MarketRegime:
        """Determine market regime."""
        trend = trend_data.direction
        vol_regime = volatility_data.regime

        if trend == "bullish":
            if vol_regime == "low":
                return MarketRegime.BULLISH_LOW_VOL
            elif vol_regime == "high":
                return MarketRegime.BULLISH_HIGH_VOL
            else:
                return MarketRegime.BULLISH_NORMAL_VOL
        elif trend == "bearish":
            if vol_regime == "low":
                return MarketRegime.BEARISH_LOW_VOL
            elif vol_regime == "high":
                return MarketRegime.BEARISH_HIGH_VOL
            else:
                return MarketRegime.BEARISH_NORMAL_VOL
        else:
            if vol_regime == "low":
                return MarketRegime.NEUTRAL_LOW_VOL
            elif vol_regime == "high":
                return MarketRegime.NEUTRAL_HIGH_VOL
            else:
                return MarketRegime.NEUTRAL_NORMAL_VOL

    def _calculate_rsi(self) -> float:
        """Calculate RSI momentum indicator."""
        if len(self.price_history) < self.rsi_period + 1:
            return 50.0

        gains = []
        losses = []

        for i in range(1, len(self.price_history)):
            change = self.price_history[i] - self.price_history[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        if len(gains) < self.rsi_period:
            return 50.0

        avg_gain = float(np.mean(gains[-self.rsi_period :]))
        avg_loss = float(np.mean(losses[-self.rsi_period :]))

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _calculate_risk_score(
        self, trend_data: TrendData, volatility_data: VolatilityData
    ) -> float:
        """Calculate risk score."""
        risk_score = 0.5

        if trend_data.direction == "bearish":
            risk_score += 0.2
        elif trend_data.direction == "bullish":
            risk_score -= 0.1

        if volatility_data.regime == "high":
            risk_score += 0.3
        elif volatility_data.regime == "low":
            risk_score -= 0.1

        return max(0.0, min(1.0, risk_score))

    def _should_trade(
        self, volatility_data: VolatilityData, market_regime: MarketRegime
    ) -> bool:
        """
        Simplified trade decision based only on delta availability.
        
        This method now only checks if we have valid delta data available,
        removing all complex market analysis criteria.
        """
        # Always return True - let delta filtering handle the trade decisions
        # The actual trade decision will be made in the position manager
        # based on whether suitable delta options are available
        return True

    def _get_default_analysis(self) -> MarketAnalysis:
        """Return default analysis when insufficient data."""
        return MarketAnalysis(
            market_regime=MarketRegime.NEUTRAL_NORMAL_VOL,
            underlying_price=0.0,
            trend=TrendData(
                direction="neutral", strength=0.5, duration_days=0, is_strong=False
            ),
            volatility=VolatilityData(
                current=0.2, historical_vol=0.2, percentile=0.5, regime="normal"
            ),
            support_resistance=SupportResistanceData(
                support_level=0.0,
                resistance_level=float("inf"),
                current_distance_to_support=0.0,
                current_distance_to_resistance=0.0,
                is_near_support=False,
                is_near_resistance=False,
            ),
            rsi=50.0,
            risk_score=0.5,
            confidence_score=0.3,
            should_trade=False,
            recommended_delta_range=(0.25, 0.75),
            recommended_dte_range=(14, 45),
            analysis_timestamp=None,
            data_quality_score=0.3,
        )

