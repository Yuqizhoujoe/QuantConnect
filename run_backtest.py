# type: ignore
"""
QuantConnect Algorithm Entry Point

This file is for Lean/QuantConnect backtesting only.
To switch strategies, change the parent class of OptionStrategy below:
    - SellPutOptionStrategy (default)
    - CoveredCallStrategy

For CLI/local testing, use run_cli.py instead.
"""
from AlgorithmImports import *  # type: ignore
from strategies.sell_put.sell_put_strategy import SellPutOptionStrategy

# from strategies.covered_call.covered_call_strategy import CoveredCallStrategy


class OptionStrategy(SellPutOptionStrategy):  # Change to CoveredCallStrategy to switch
    """
    Main algorithm class for QuantConnect/Lean.
    Inherit from the desired strategy class above.
    """

    def Initialize(self) -> None:
        from datetime import datetime

        start_date = datetime(
            2022, 1, 1
        )  # Updated to 2022 for better option data availability
        end_date = datetime(2023, 12, 31)  # Updated to 2023 for comprehensive testing
        config_path = "sell_put_stock.json"  # Config file copied to root directory
        super().Initialize(start_date, end_date, config_path)
        self.Log(f"Initialized strategy: {self.__class__.__bases__[0].__name__}")
        self.Log(f"Testing period: {start_date.date()} to {end_date.date()}")
        self.Log(f"Using configuration: {config_path}")

    def OnData(self, slice: Slice) -> None:
        self.Log(
            f"OnData called at {self.Time} - Portfolio Value: ${self.Portfolio.TotalPortfolioValue:.2f}"
        )
        self.Log(
            f"Slice contains {len(slice.OptionChains) if slice.OptionChains else 0} option chains"
        )
        super().OnData(slice)

    def OnEndOfAlgorithm(self) -> None:
        super().OnEndOfAlgorithm()
