from AlgorithmImports import *  # type: ignore
from shared.utils.constants import (
    DEFAULT_SCHEDULE_TIME_HOUR,
    DEFAULT_SCHEDULE_TIME_MINUTE,
    DEFAULT_SCHEDULE_REFERENCE,
    ERROR_NO_STOCKS_AVAILABLE,
)
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .sell_put_strategy import SellPutOptionStrategy


@dataclass
class Scheduler:
    """
    Manages the scheduling of periodic events for the algorithm.
    This class centralizes the logic for when the strategy should be evaluated.
    """

    strategy: "SellPutOptionStrategy"

    def setup_events(self) -> None:
        """
        Sets up the scheduled events for the algorithm.
        This method schedules the `evaluate_option_strategy` to run daily.
        """

        if self.strategy.portfolio_manager.stock_managers:
            reference_symbol = list(
                self.strategy.portfolio_manager.stock_managers.keys()
            )[0]
            self.strategy.Log(f"Using {reference_symbol} for scheduling")
        else:
            reference_symbol = DEFAULT_SCHEDULE_REFERENCE
            self.strategy.Log(ERROR_NO_STOCKS_AVAILABLE)

        self.strategy.Schedule.On(
            self.strategy.DateRules.EveryDay(reference_symbol),
            self.strategy.TimeRules.At(
                DEFAULT_SCHEDULE_TIME_HOUR, DEFAULT_SCHEDULE_TIME_MINUTE
            ),
            self.evaluate_option_strategy,
        )

    def evaluate_option_strategy(self) -> None:
        """
        The core logic function that is called on a schedule.
        It delegates position management to the PortfolioManager.
        """
        try:
            self.strategy.portfolio_manager.manage_positions()
        except Exception as e:
            self.strategy.Log(f"Error in EvaluateOptionStrategy: {str(e)}")
