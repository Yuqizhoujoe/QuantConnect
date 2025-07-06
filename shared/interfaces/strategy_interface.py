"""
Strategy interface for all trading strategies.
"""

from abc import ABC, abstractmethod
from typing import Any


class StrategyInterface(ABC):
    """
    Interface that all trading strategies must implement.
    """

    @abstractmethod
    def Initialize(self) -> None:
        """
        Initialize the strategy with configuration and setup components.
        """
        pass

    @abstractmethod
    def OnData(self, slice: Any) -> None:
        """
        Handle incoming market data.

        Args:
            slice: Market data slice from QuantConnect
        """
        pass

    @abstractmethod
    def OnEndOfAlgorithm(self) -> None:
        """
        Handle end of algorithm processing and finalize results.
        """
        pass
