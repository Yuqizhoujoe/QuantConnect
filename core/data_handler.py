
from AlgorithmImports import *
from typing import Any, Optional, Dict

class DataHandler:
    """
    Enhanced data handler with efficient plotting and risk monitoring.
    This includes handling incoming data slices and providing data-related utilities
    while respecting QuantConnect's charting limits.
    """
    def __init__(self, algorithm: Any, ticker: str) -> None:
        """
        Initializes the DataHandler with plotting controls.
        
        Args:
            algorithm: A reference to the main algorithm instance.
            ticker: Stock ticker symbol for this data handler.
        """
        self.algorithm: Any = algorithm
        self.ticker: str = ticker
        self.latest_slice: Optional[Any] = None  # Stores the most recent data slice

    def update_data(self, slice_data: Any) -> None:
        """
        Update data from the latest slice.
        
        Args:
            slice_data: Latest data slice from the algorithm
        """
        self.latest_slice = slice_data

    def on_data(self, slice: Slice) -> None:
        """
        Simplified data handling for cloud backtesting.
        
        This method focuses on data storage and analysis without excessive plotting
        to optimize performance for QuantConnect cloud backtesting.
        
        Args:
            slice: The new data slice from the engine.
        """
        self.latest_slice = slice
        
        # Update peak portfolio value for drawdown calculation
        current_value: float = self.algorithm.Portfolio.TotalPortfolioValue
        if current_value > self.algorithm.peak_portfolio_value:
            self.algorithm.peak_portfolio_value = current_value
        
        # Calculate and store daily PnL (for analysis, not plotting)
        if self.algorithm.current_contract:
            position: Any = self.algorithm.Portfolio[self.algorithm.current_contract.Symbol]
            if position.Invested:
                daily_pnl: float = position.UnrealizedProfit
                self.algorithm.daily_pnl.append(daily_pnl)
                
                # Keep only recent PnL data for analysis (limit to 100 points)
                if len(self.algorithm.daily_pnl) > 100:
                    self.algorithm.daily_pnl.pop(0)

    def get_option_delta(self, contract: Any) -> float:
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
    

