"""
Modular Trading Criteria System

This module provides a flexible framework for implementing trading criteria
that can be easily added, removed, or scaled across different strategies.

Each criterion is implemented as a separate class that can be combined
with other criteria to create complex decision trees.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from datetime import date


class CriteriaResult(Enum):
    """Result of a trading criteria evaluation."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


@dataclass
class CriteriaEvaluation:
    """Result of evaluating a trading criterion."""
    criterion_name: str
    result: CriteriaResult
    score: float  # 0.0 to 1.0, where 1.0 is best
    message: str
    details: Dict[str, Any]

    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class TradingContext:
    """
    Well-defined context for trading criteria evaluation.
    
    This class ensures that all required data is available and properly typed
    for criteria evaluation. Missing data is handled gracefully with defaults.
    """
    
    # Option-specific data
    delta: float = 0.0
    dte: int = 0
    strike: float = 0.0
    underlying_price: float = 0.0
    
    # Market data
    volatility: float = 0.0
    market_regime: str = "unknown"
    rsi: float = 50.0
    trend_direction: str = "neutral"
    trend_strength: float = 0.5
    
    # Additional context
    contract: Optional[Any] = None
    timestamp: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for backward compatibility."""
        return {
            'delta': self.delta,
            'dte': self.dte,
            'strike': self.strike,
            'underlying_price': self.underlying_price,
            'volatility': self.volatility,
            'market_regime': self.market_regime,
            'rsi': self.rsi,
            'trend_direction': self.trend_direction,
            'trend_strength': self.trend_strength,
            'contract': self.contract,
            'timestamp': self.timestamp,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TradingContext":
        """Create TradingContext from dictionary."""
        return cls(**data)
    
    def validate(self) -> List[str]:
        """
        Validate that required data is available.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check for required numeric data
        if self.delta == 0.0:
            errors.append("Delta is required")
        if self.dte == 0:
            errors.append("DTE is required")
        if self.underlying_price == 0.0:
            errors.append("Underlying price is required")
        if self.strike == 0.0:
            errors.append("Strike price is required")
        
        # Check for valid ranges
        if not (0.0 <= self.delta <= 1.0):
            errors.append("Delta must be between 0.0 and 1.0")
        if self.dte < 0:
            errors.append("DTE must be non-negative")
        if self.underlying_price < 0:
            errors.append("Underlying price must be non-negative")
        if self.strike < 0:
            errors.append("Strike price must be non-negative")
        if not (0.0 <= self.volatility <= 2.0):
            errors.append("Volatility must be between 0.0 and 2.0")
        if not (0.0 <= self.rsi <= 100.0):
            errors.append("RSI must be between 0.0 and 100.0")
        if not (0.0 <= self.trend_strength <= 1.0):
            errors.append("Trend strength must be between 0.0 and 1.0")
        
        return errors


class TradingCriterion(ABC):
    """Base class for all trading criteria."""
    
    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight
    
    @abstractmethod
    def evaluate(self, context: TradingContext) -> CriteriaEvaluation:
        """
        Evaluate this criterion against the given context.
        
        Args:
            context: TradingContext containing all relevant data for evaluation
            
        Returns:
            CriteriaEvaluation with result and details
        """
        pass
    
    def get_required_fields(self) -> List[str]:
        """
        Get list of required fields for this criterion.
        
        Returns:
            List of required field names
        """
        return []


class DeltaCriterion(TradingCriterion):
    """Criterion based on option delta values."""
    
    def __init__(self, target_range: Tuple[float, float], weight: float = 1.0):
        super().__init__("Delta", weight)
        self.target_range = target_range
    
    def get_required_fields(self) -> List[str]:
        return ["delta"]
    
    def evaluate(self, context: TradingContext) -> CriteriaEvaluation:
        """Evaluate if delta is within acceptable range."""
        delta_abs = abs(context.delta)
        min_delta, max_delta = self.target_range
        
        if min_delta <= delta_abs <= max_delta:
            # Calculate score based on proximity to middle of range
            target_mid = (min_delta + max_delta) / 2
            distance = abs(delta_abs - target_mid)
            max_distance = (max_delta - min_delta) / 2
            score = max(0.0, 1.0 - (distance / max_distance))
            
            return CriteriaEvaluation(
                criterion_name=self.name,
                result=CriteriaResult.PASS,
                score=score,
                message=f"Delta {delta_abs:.3f} within range {min_delta:.3f}-{max_delta:.3f}",
                details={"delta": delta_abs, "target_range": self.target_range}
            )
        else:
            return CriteriaEvaluation(
                criterion_name=self.name,
                result=CriteriaResult.FAIL,
                score=0.0,
                message=f"Delta {delta_abs:.3f} outside range {min_delta:.3f}-{max_delta:.3f}",
                details={"delta": delta_abs, "target_range": self.target_range}
            )


class MarketRegimeCriterion(TradingCriterion):
    """Criterion based on market regime analysis."""
    
    def __init__(self, allowed_regimes: List[str], weight: float = 1.0):
        super().__init__("MarketRegime", weight)
        self.allowed_regimes = allowed_regimes
    
    def get_required_fields(self) -> List[str]:
        return ["market_regime"]
    
    def evaluate(self, context: TradingContext) -> CriteriaEvaluation:
        """Evaluate if current market regime is acceptable."""
        current_regime = context.market_regime
        
        if current_regime in self.allowed_regimes:
            return CriteriaEvaluation(
                criterion_name=self.name,
                result=CriteriaResult.PASS,
                score=1.0,
                message=f"Market regime '{current_regime}' is acceptable",
                details={"current_regime": current_regime, "allowed_regimes": self.allowed_regimes}
            )
        else:
            return CriteriaEvaluation(
                criterion_name=self.name,
                result=CriteriaResult.FAIL,
                score=0.0,
                message=f"Market regime '{current_regime}' not in allowed list",
                details={"current_regime": current_regime, "allowed_regimes": self.allowed_regimes}
            )


class VolatilityCriterion(TradingCriterion):
    """Criterion based on market volatility."""
    
    def __init__(self, max_volatility: float = 0.5, weight: float = 1.0):
        super().__init__("Volatility", weight)
        self.max_volatility = max_volatility
    
    def get_required_fields(self) -> List[str]:
        return ["volatility"]
    
    def evaluate(self, context: TradingContext) -> CriteriaEvaluation:
        """Evaluate if volatility is acceptable."""
        current_volatility = context.volatility
        
        if current_volatility <= self.max_volatility:
            # Score based on how low the volatility is (lower is better)
            score = max(0.0, 1.0 - (current_volatility / self.max_volatility))
            
            return CriteriaEvaluation(
                criterion_name=self.name,
                result=CriteriaResult.PASS,
                score=score,
                message=f"Volatility {current_volatility:.3f} below threshold {self.max_volatility:.3f}",
                details={"current_volatility": current_volatility, "max_volatility": self.max_volatility}
            )
        else:
            return CriteriaEvaluation(
                criterion_name=self.name,
                result=CriteriaResult.FAIL,
                score=0.0,
                message=f"Volatility {current_volatility:.3f} above threshold {self.max_volatility:.3f}",
                details={"current_volatility": current_volatility, "max_volatility": self.max_volatility}
            )


class DTECriterion(TradingCriterion):
    """Criterion based on days to expiration."""
    
    def __init__(self, min_dte: int = 14, max_dte: int = 45, weight: float = 1.0):
        super().__init__("DTE", weight)
        self.min_dte = min_dte
        self.max_dte = max_dte
    
    def get_required_fields(self) -> List[str]:
        return ["dte"]
    
    def evaluate(self, context: TradingContext) -> CriteriaEvaluation:
        """Evaluate if DTE is within acceptable range."""
        current_dte = context.dte
        
        if self.min_dte <= current_dte <= self.max_dte:
            # Score based on proximity to middle of range
            target_dte = (self.min_dte + self.max_dte) / 2
            distance = abs(current_dte - target_dte)
            max_distance = (self.max_dte - self.min_dte) / 2
            score = max(0.0, 1.0 - (distance / max_distance))
            
            return CriteriaEvaluation(
                criterion_name=self.name,
                result=CriteriaResult.PASS,
                score=score,
                message=f"DTE {current_dte} within range {self.min_dte}-{self.max_dte}",
                details={"current_dte": current_dte, "target_range": (self.min_dte, self.max_dte)}
            )
        else:
            return CriteriaEvaluation(
                criterion_name=self.name,
                result=CriteriaResult.FAIL,
                score=0.0,
                message=f"DTE {current_dte} outside range {self.min_dte}-{self.max_dte}",
                details={"current_dte": current_dte, "target_range": (self.min_dte, self.max_dte)}
            )


class RSICriterion(TradingCriterion):
    """Criterion based on RSI momentum indicator."""
    
    def __init__(self, oversold: float = 30, overbought: float = 70, weight: float = 1.0):
        super().__init__("RSI", weight)
        self.oversold = oversold
        self.overbought = overbought
    
    def get_required_fields(self) -> List[str]:
        return ["rsi"]
    
    def evaluate(self, context: TradingContext) -> CriteriaEvaluation:
        """Evaluate if RSI is in acceptable range."""
        current_rsi = context.rsi
        
        if self.oversold <= current_rsi <= self.overbought:
            # Score based on distance from extremes
            distance_from_center = abs(current_rsi - 50.0)
            max_distance = 50.0
            score = max(0.0, 1.0 - (distance_from_center / max_distance))
            
            return CriteriaEvaluation(
                criterion_name=self.name,
                result=CriteriaResult.PASS,
                score=score,
                message=f"RSI {current_rsi:.1f} in acceptable range {self.oversold}-{self.overbought}",
                details={"current_rsi": current_rsi, "range": (self.oversold, self.overbought)}
            )
        else:
            return CriteriaEvaluation(
                criterion_name=self.name,
                result=CriteriaResult.FAIL,
                score=0.0,
                message=f"RSI {current_rsi:.1f} outside range {self.oversold}-{self.overbought}",
                details={"current_rsi": current_rsi, "range": (self.oversold, self.overbought)}
            )


class TrendCriterion(TradingCriterion):
    """Criterion based on price trend analysis."""
    
    def __init__(self, allowed_directions: List[str], weight: float = 1.0):
        super().__init__("Trend", weight)
        self.allowed_directions = allowed_directions
    
    def get_required_fields(self) -> List[str]:
        return ["trend_direction", "trend_strength"]
    
    def evaluate(self, context: TradingContext) -> CriteriaEvaluation:
        """Evaluate if trend direction is acceptable."""
        current_trend = context.trend_direction
        trend_strength = context.trend_strength
        
        if current_trend in self.allowed_directions:
            return CriteriaEvaluation(
                criterion_name=self.name,
                result=CriteriaResult.PASS,
                score=trend_strength,  # Use trend strength as score
                message=f"Trend '{current_trend}' is acceptable with strength {trend_strength:.2f}",
                details={"trend_direction": current_trend, "trend_strength": trend_strength}
            )
        else:
            return CriteriaEvaluation(
                criterion_name=self.name,
                result=CriteriaResult.FAIL,
                score=0.0,
                message=f"Trend '{current_trend}' not in allowed directions",
                details={"trend_direction": current_trend, "allowed_directions": self.allowed_directions}
            )


class CriteriaManager:
    """Manages multiple trading criteria and combines their results."""
    
    def __init__(self, criteria: Optional[List[TradingCriterion]] = None):
        self.criteria = criteria if criteria is not None else []
    
    def add_criterion(self, criterion: TradingCriterion) -> None:
        """Add a criterion to the manager."""
        self.criteria.append(criterion)
    
    def remove_criterion(self, criterion_name: str) -> None:
        """Remove a criterion by name."""
        self.criteria = [c for c in self.criteria if c.name != criterion_name]
    
    def get_required_fields(self) -> List[str]:
        """Get all required fields for all criteria."""
        required_fields = set()
        for criterion in self.criteria:
            required_fields.update(criterion.get_required_fields())
        return list(required_fields)
    
    def validate_context(self, context: TradingContext) -> List[str]:
        """
        Validate that context has all required fields.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check context validation
        errors.extend(context.validate())
        
        # Check required fields for criteria
        required_fields = self.get_required_fields()
        for field in required_fields:
            if not hasattr(context, field) or getattr(context, field) is None:
                errors.append(f"Required field '{field}' is missing")
        
        return errors
    
    def evaluate_all(self, context: TradingContext) -> Dict[str, CriteriaEvaluation]:
        """Evaluate all criteria against the given context."""
        results = {}
        
        # Validate context first
        validation_errors = self.validate_context(context)
        if validation_errors:
            # Return failed evaluations for all criteria if context is invalid
            for criterion in self.criteria:
                results[criterion.name] = CriteriaEvaluation(
                    criterion_name=criterion.name,
                    result=CriteriaResult.FAIL,
                    score=0.0,
                    message=f"Context validation failed: {', '.join(validation_errors)}",
                    details={"validation_errors": validation_errors}
                )
            return results
        
        # Evaluate each criterion
        for criterion in self.criteria:
            results[criterion.name] = criterion.evaluate(context)
        
        return results
    
    def should_trade(self, context: TradingContext) -> Tuple[bool, float, str]:
        """
        Determine if trading should proceed based on all criteria.
        
        Returns:
            Tuple of (should_trade, overall_score, summary_message)
        """
        if not self.criteria:
            return True, 1.0, "No criteria defined - allowing trade"
        
        # Validate context
        validation_errors = self.validate_context(context)
        if validation_errors:
            return False, 0.0, f"Context validation failed: {', '.join(validation_errors)}"
        
        evaluations = self.evaluate_all(context)
        
        # Check if any criteria failed
        failed_criteria = [name for name, eval in evaluations.items() 
                          if eval.result == CriteriaResult.FAIL]
        
        if failed_criteria:
            failed_messages = [evaluations[name].message for name in failed_criteria]
            return False, 0.0, f"Trade blocked by: {', '.join(failed_messages)}"
        
        # Calculate weighted score
        total_weight = sum(c.weight for c in self.criteria)
        weighted_score = sum(
            evaluations[c.name].score * c.weight 
            for c in self.criteria
        ) / total_weight if total_weight > 0 else 0.0
        
        # Generate summary
        passed_criteria = [name for name, eval in evaluations.items() 
                          if eval.result == CriteriaResult.PASS]
        summary = f"Trade allowed by {len(passed_criteria)} criteria with score {weighted_score:.3f}"
        
        return True, weighted_score, summary
    
    def get_criteria_summary(self) -> str:
        """Get a summary of all criteria."""
        if not self.criteria:
            return "No criteria defined"
        
        summary = "Trading Criteria:\n"
        for criterion in self.criteria:
            required_fields = ", ".join(criterion.get_required_fields())
            summary += f"  - {criterion.name} (weight: {criterion.weight}, requires: [{required_fields}])\n"
        return summary


# Predefined criteria configurations for common strategies
class CriteriaPresets:
    """Predefined criteria configurations for different strategies."""
    
    @staticmethod
    def delta_only() -> CriteriaManager:
        """Only use delta-based criteria with loose range for easy trading."""
        manager = CriteriaManager()
        manager.add_criterion(DeltaCriterion(target_range=(0.15, 0.85)))
        return manager
    
    @staticmethod
    def conservative() -> CriteriaManager:
        """Conservative criteria with multiple checks."""
        manager = CriteriaManager()
        manager.add_criterion(DeltaCriterion(target_range=(0.2, 0.6), weight=1.0))
        manager.add_criterion(MarketRegimeCriterion(
            allowed_regimes=['bullish_low_vol', 'bullish_normal_vol', 'neutral_normal_vol'], 
            weight=0.8
        ))
        manager.add_criterion(VolatilityCriterion(max_volatility=0.4, weight=0.7))
        manager.add_criterion(DTECriterion(min_dte=21, max_dte=45, weight=0.6))
        return manager
    
    @staticmethod
    def aggressive() -> CriteriaManager:
        """Aggressive criteria with fewer restrictions."""
        manager = CriteriaManager()
        manager.add_criterion(DeltaCriterion(target_range=(0.3, 0.8), weight=1.0))
        manager.add_criterion(VolatilityCriterion(max_volatility=0.6, weight=0.5))
        return manager
    
    @staticmethod
    def momentum_based() -> CriteriaManager:
        """Momentum-based criteria using RSI and trend."""
        manager = CriteriaManager()
        manager.add_criterion(DeltaCriterion(target_range=(0.25, 0.75), weight=1.0))
        manager.add_criterion(RSICriterion(oversold=25, overbought=75, weight=0.8))
        manager.add_criterion(TrendCriterion(
            allowed_directions=['bullish', 'neutral'], 
            weight=0.7
        ))
        return manager 