"""
Common type definitions for trading strategies.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class TradeLog:
    """Log entry for a trade."""

    timestamp: datetime
    ticker: str
    action: str  # 'buy', 'sell', 'close'
    quantity: int
    price: float
    pnl: float
    contract_symbol: Optional[str] = None


@dataclass
class PositionData:
    """Data about a current position."""

    ticker: str
    quantity: int
    entry_price: float
    current_price: float
    pnl: float
    contract_symbol: Optional[str] = None


@dataclass
class MarketData:
    """Market data for analysis."""

    ticker: str
    price: float
    volume: int
    timestamp: datetime
    option_chains: Optional[Dict[str, Any]] = None


@dataclass
class StrategyMetrics:
    """Performance metrics for a strategy."""

    total_trades: int
    winning_trades: int
    losing_trades: int
    total_pnl: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
