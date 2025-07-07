from AlgorithmImports import *   # type: ignore
from typing import Any, Optional, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from ..sell_put_strategy import SellPutOptionStrategy


@dataclass
class DataHandler:
    """
    Enhanced data handler with efficient plotting and risk monitoring.
    This includes handling incoming data slices and providing data-related utilities
    while respecting QuantConnect's charting limits.
    """

    strategy: "SellPutOptionStrategy"
    ticker: str
    latest_slice: Optional[Any] = None  # Stores the most recent data slice

    def update_data(self, slice_data: Any) -> None:
        """
        Update data from the latest slice.

        Args:
            slice_data: Latest data slice from the algorithm
        """
        if slice_data is not None:
            self.latest_slice = slice_data
            # Log data availability for debugging
            if hasattr(slice_data, "OptionChains") and slice_data.OptionChains:
                option_symbol = self.strategy.option_symbols.get(self.ticker)
                if option_symbol and option_symbol in slice_data.OptionChains:
                    chain = slice_data.OptionChains.get(option_symbol)
                    if (
                        chain
                        and hasattr(chain, "Underlying")
                        and hasattr(chain.Underlying, "Price")
                    ):
                        self.strategy.Log(
                            f"{self.ticker} data updated - underlying price: ${chain.Underlying.Price:.2f}"
                        )
                    else:
                        self.strategy.Log(
                            f"{self.ticker} data updated - no underlying price available"
                        )
                else:
                    self.strategy.Log(
                        f"{self.ticker} data updated - no option chain available"
                    )
            else:
                self.strategy.Log(
                    f"{self.ticker} data updated - no option chains in slice"
                )

    def on_data(self, slice: Slice) -> None:  # type: ignore
        """
        Simplified data handling for cloud backtesting.

        This method focuses on data storage and analysis without excessive plotting
        to optimize performance for QuantConnect cloud backtesting.

        Args:
            slice: The new data slice from the engine.
        """
        self.latest_slice = slice

        # Update peak portfolio value for drawdown calculation
        current_value: float = self.strategy.Portfolio.TotalPortfolioValue
        if current_value > self.strategy.peak_portfolio_value:
            self.strategy.peak_portfolio_value = current_value

        # Calculate and store daily PnL (for analysis, not plotting)
        if self.strategy.current_contract:
            position: Any = self.strategy.Portfolio[
                self.strategy.current_contract.Symbol
            ]
            if position.Invested:
                daily_pnl: float = position.UnrealizedProfit
                self.strategy.daily_pnl.append(daily_pnl)

                # Keep only recent PnL data for analysis (limit to 100 points)
                if len(self.strategy.daily_pnl) > 100:
                    self.strategy.daily_pnl.pop(0)

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
            return (
                contract.Greeks.Delta
                if contract.Greeks and contract.Greeks.Delta is not None
                else 0
            )
        except:
            # Return 0 in case of any error (e.g., Greeks not calculated yet)
            return 0

