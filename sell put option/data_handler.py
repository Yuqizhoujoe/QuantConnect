
from AlgorithmImports import *

class DataHandler:
    """
    Manages all data-related operations for the algorithm.
    This includes handling incoming data slices and providing data-related utilities.
    """
    def __init__(self, algorithm):
        """
        Initializes the DataHandler.
        
        Args:
            algorithm: A reference to the main algorithm instance.
        """
        self.algorithm = algorithm
        self.latest_slice = None  # Stores the most recent data slice

    def on_data(self, slice: Slice):
        """
        Primary method to handle new data slices from the QuantConnect engine.
        It stores the latest slice and updates the daily PnL plot.
        
        Args:
            slice: The new data slice from the engine.
        """
        self.latest_slice = slice
        
        # Plot the unrealized profit and loss for the current position.
        if self.algorithm.current_contract:
            position = self.algorithm.Portfolio[self.algorithm.current_contract.Symbol]
            if position.Invested:
                daily_pnl = position.UnrealizedProfit
                self.algorithm.Plot("Daily PnL", "Unrealized PnL", daily_pnl)

    def get_option_delta(self, contract):
        """
        Safely retrieves the delta of a given option contract.
        Delta is a measure of the option's price sensitivity to changes in the
        underlying asset's price.
        
        Args:
            contract: The option contract to get the delta for.
            
        Returns:
            The delta of the contract, or 0 if it's not available.
        """
        try:
            # Check if Greeks and Delta are available and not None
            return contract.Greeks.Delta if contract.Greeks and contract.Greeks.Delta is not None else 0
        except:
            # Return 0 in case of any error (e.g., Greeks not calculated yet)
            return 0
