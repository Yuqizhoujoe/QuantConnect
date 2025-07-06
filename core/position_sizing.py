"""
Position Sizing Utilities

This module provides reusable position sizing calculations that can be used
across different strategies and risk management components.
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from .technical_indicators import PerformanceMetrics

class PositionSizing:
    """Position sizing calculation utilities."""
    
    @staticmethod
    def calculate_kelly_criterion(win_rate: float, avg_win: float, avg_loss: float) -> float:
        """Calculate Kelly Criterion fraction for position sizing."""
        if avg_loss == 0:
            return 0.1  # Conservative default
        
        # Kelly formula: f = (bp - q) / b
        # where b = odds received, p = probability of win, q = probability of loss
        kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        
        # Cap Kelly fraction between 10-50% to avoid over-leveraging
        return max(0.1, min(0.5, kelly_fraction))
    
    @staticmethod
    def calculate_portfolio_risk_size(contract: Any, underlying_price: float, 
                                    portfolio_value: float, max_risk_pct: float) -> int:
        """Calculate position size based on portfolio risk limits."""
        max_risk_amount = portfolio_value * max_risk_pct
        potential_loss = PositionSizing.calculate_max_loss(contract, underlying_price)
        
        if potential_loss <= 0:
            return 1  # Minimum position size
        
        return int(max_risk_amount / potential_loss)
    
    @staticmethod
    def calculate_max_loss(contract: Any, underlying_price: float) -> float:
        """Calculate maximum potential loss for a short put position."""
        # Use a realistic worst-case scenario: 50% drop in underlying price
        worst_case_price = underlying_price * 0.5
        
        # Calculate intrinsic value at worst-case price
        intrinsic_value = max(0, contract.Strike - worst_case_price)
        
        # Loss per contract = intrinsic value * 100 (contract multiplier)
        return intrinsic_value * 100
    
    @staticmethod
    def calculate_margin_based_size(contract: Any, available_margin: float) -> int:
        """Calculate position size based on available margin."""
        # Margin requirement for short puts is typically 20% of strike price
        margin_requirement = contract.Strike * 100 * 0.2
        return int(available_margin / margin_requirement)
    
    @staticmethod
    def calculate_conservative_size(contract: Any, portfolio_value: float, 
                                  max_position_pct: float) -> int:
        """Calculate conservative position size."""
        max_position_value = portfolio_value * max_position_pct
        margin_requirement = contract.Strike * 100 * 0.2
        return max(1, int(max_position_value / margin_requirement))
    
    @staticmethod
    def get_volatility_adjustment(daily_pnl: List[float], lookback: int = 20, 
                                threshold: float = 0.4) -> float:
        """Get volatility adjustment factor for position sizing."""
        if len(daily_pnl) < lookback:
            return 1.0  # Default factor when insufficient data
        
        recent_pnl = daily_pnl[-lookback:]
        volatility = float(np.std(recent_pnl))
        
        # Adjust position size based on volatility regime
        if volatility > threshold:
            return 0.7  # Reduce position size in high volatility
        elif volatility < 0.1:
            return 1.2  # Increase position size in low volatility
        else:
            return 1.0  # Normal position size in moderate volatility
    
    @staticmethod
    def calculate_optimal_position_size(contract: Any, underlying_price: float,
                                      portfolio_value: float, available_margin: float,
                                      trades: List[Dict[str, Any]], daily_pnl: List[float],
                                      max_risk_pct: float = 0.02, max_position_pct: float = 0.20) -> int:
        """Calculate optimal position size using multiple methods."""
        # Step 1: Calculate Kelly Criterion
        win_rate = PerformanceMetrics.calculate_win_rate(trades)
        avg_win = PerformanceMetrics.calculate_average_win(trades)
        avg_loss = PerformanceMetrics.calculate_average_loss(trades)
        
        kelly_fraction = PositionSizing.calculate_kelly_criterion(win_rate, avg_win, avg_loss)
        
        # Step 2: Get volatility adjustment
        volatility_factor = PositionSizing.get_volatility_adjustment(daily_pnl)
        
        # Step 3: Calculate different sizing methods
        portfolio_risk_size = PositionSizing.calculate_portfolio_risk_size(
            contract, underlying_price, portfolio_value, max_risk_pct)
        margin_size = PositionSizing.calculate_margin_based_size(contract, available_margin)
        conservative_size = PositionSizing.calculate_conservative_size(
            contract, portfolio_value, max_position_pct)
        
        # Step 4: Combine all sizing methods - take the most conservative approach
        optimal_size = min(portfolio_risk_size, margin_size, conservative_size,
                          int(portfolio_risk_size * kelly_fraction * volatility_factor))
        
        # Ensure minimum position size of 1 contract
        return max(1, optimal_size)

class RiskLimits:
    """Risk limit checking utilities."""
    
    @staticmethod
    def check_drawdown_limit(current_value: float, peak_value: float, 
                           max_drawdown: float) -> bool:
        """Check if drawdown limit is exceeded."""
        if peak_value <= 0:
            return False
        
        drawdown = (peak_value - current_value) / peak_value
        return drawdown > max_drawdown
    
    @staticmethod
    def check_consecutive_losses(trades: List[Dict[str, Any]], 
                               max_consecutive: int = 3, lookback: int = 5) -> bool:
        """Check if consecutive loss limit is exceeded."""
        if not trades:
            return False
        
        recent_trades = [t for t in trades[-lookback:] if 'pnl' in t]
        if len(recent_trades) < 3:
            return False
        
        consecutive_losses = sum(1 for t in recent_trades if t['pnl'] < 0)
        return consecutive_losses >= max_consecutive
    
    @staticmethod
    def check_portfolio_volatility(daily_pnl: List[float], portfolio_value: float,
                                 max_volatility_pct: float, min_data_points: int = 20) -> bool:
        """Check if portfolio volatility limit is exceeded."""
        if len(daily_pnl) < min_data_points:
            return False
        
        volatility = float(np.std(daily_pnl))
        max_volatility = portfolio_value * max_volatility_pct
        return volatility > max_volatility
    
    @staticmethod
    def should_stop_trading(current_value: float, peak_value: float, max_drawdown: float,
                          trades: List[Dict[str, Any]], daily_pnl: List[float],
                          portfolio_value: float, max_volatility_pct: float) -> bool:
        """Check if trading should be stopped due to risk limits."""
        # Check drawdown limit
        if RiskLimits.check_drawdown_limit(current_value, peak_value, max_drawdown):
            return True
        
        # Check consecutive losses
        if RiskLimits.check_consecutive_losses(trades):
            return True
        
        # Check portfolio volatility
        if RiskLimits.check_portfolio_volatility(daily_pnl, portfolio_value, max_volatility_pct):
            return True
        
        return False 