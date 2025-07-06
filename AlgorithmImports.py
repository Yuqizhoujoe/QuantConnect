# Mock AlgorithmImports for local development
# This file provides stubs for QuantConnect-specific classes and functions

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Mock QCAlgorithm base class
class QCAlgorithm:
    def __init__(self):
        self.Portfolio = MockPortfolio()
        self.Time = datetime.now()
        self.parameters = {}
    
    def AddEquity(self, symbol: str, resolution: Any) -> Any:
        return MockSymbol(symbol)
    
    def AddOption(self, symbol: str, resolution: Any) -> Any:
        return MockOption(symbol)
    
    def Log(self, message: str) -> None:
        print(f"[LOG] {message}")
    
    def Plot(self, chart_name: str, series_name: str, value: float) -> None:
        pass
    
    def SetBenchmark(self, symbol: str) -> None:
        pass

# Mock classes
class MockPortfolio:
    def __init__(self):
        self.TotalPortfolioValue = 100000.0
        self.TotalMarginUsed = 0.0
        self.MarginRemaining = 100000.0

class MockSymbol:
    def __init__(self, symbol: str):
        self.Symbol = symbol
        self.Price = 100.0

class MockOption:
    def __init__(self, symbol: str):
        self.Symbol = symbol
    
    def SetFilter(self, *args) -> None:
        pass

# Mock Resolution enum
class Resolution:
    Minute = "Minute"
    Hour = "Hour"
    Daily = "Daily"

# Mock OptionRight enum
class OptionRight:
    Put = "Put"
    Call = "Call"

# Mock Slice class
class Slice:
    def __init__(self):
        self.Equity = {}
        self.OptionChains = {}

# Export all the mock classes
__all__ = ['QCAlgorithm', 'Resolution', 'Slice', 'MockPortfolio', 'MockSymbol', 'MockOption'] 