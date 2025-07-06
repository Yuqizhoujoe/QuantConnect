"""
StrategyContext for dependency injection in sell put strategy.
"""

from dataclasses import dataclass
from typing import Callable, Any, Dict


@dataclass
class StrategyContext:
    """
    Dependency container for strategy components.

    Contains all shared dependencies that components need:
    - Configuration
    - Logging function
    - Trading methods (buy, sell)
    - Portfolio data
    - Symbol mappings
    - Time and scheduling
    """

    config: Any
    log: Callable[[str], None]
    buy: Callable
    sell: Callable
    portfolio: Any
    option_symbols: Dict[str, Any]
    stock_symbols: Dict[str, Any]
    time: Any
    schedule: Any
