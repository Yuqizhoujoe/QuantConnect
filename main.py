# region imports
from AlgorithmImports import *
from strategies import SellPutOption
# endregion

class Main(SellPutOption):
    """
    Main algorithm class that runs the sell put strategy.
    This is the entry point for QuantConnect.
    """
    
    def Initialize(self) -> None:
        """
        Initialize the algorithm with sell put strategy configuration.
        """
        # Call the parent class Initialize method to set up the strategy
        super().Initialize()
        
        # Add any additional initialization specific to this main class
        self.Log("Main algorithm initialized - Sell Put Strategy is running")
        
        # Set up basic plotting for portfolio tracking
        self.Plot("Strategy Performance", "Portfolio Value", self.Portfolio.TotalPortfolioValue)
        
    def OnData(self, slice: Slice) -> None:
        """
        Handle incoming data and delegate to the sell put strategy.
        """
        # Call the parent class OnData method to run the strategy logic
        super().OnData(slice)
        
        # Add any additional data handling specific to this main class
        # (Currently just using the parent implementation)
        
    def OnEndOfAlgorithm(self) -> None:
        """
        Handle end of algorithm and delegate to the sell put strategy.
        """
        # Call the parent class OnEndOfAlgorithm method
        super().OnEndOfAlgorithm()
        
        # Add any additional end-of-algorithm handling
        self.Log("Main algorithm completed - Sell Put Strategy finished") 