
from AlgorithmImports import *
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from strategies.sell_put.portfolio_manager import PortfolioManager

class Scheduler:
    """
    Manages the scheduling of periodic events for the algorithm.
    This class centralizes the logic for when the strategy should be evaluated.
    """
    def __init__(self, algorithm: Any, portfolio_manager: 'PortfolioManager') -> None:
        """
        Initializes the Scheduler.
        
        Args:
            algorithm: A reference to the main algorithm instance.
            portfolio_manager: A reference to the portfolio manager instance.
        """
        self.algorithm: Any = algorithm
        self.portfolio_manager: PortfolioManager = portfolio_manager

    def setup_events(self) -> None:
        """
        Sets up the scheduled events for the algorithm.
        This method schedules the `evaluate_option_strategy` to run daily.
        """
        # Use the first stock as the reference for scheduling
        first_stock: str = list(self.portfolio_manager.stock_managers.keys())[0] if self.portfolio_manager.stock_managers else "SPY"
        self.algorithm.Schedule.On(self.algorithm.DateRules.EveryDay(first_stock),
                                  self.algorithm.TimeRules.At(11, 0),
                                  self.evaluate_option_strategy)

    def evaluate_option_strategy(self) -> None:
        """
        The core logic function that is called on a schedule.
        It delegates position management to the PortfolioManager.
        """
        try:
            # Delegate all position management to the portfolio manager
            # This handles both closing existing positions and finding new opportunities
            self.portfolio_manager.manage_positions()
        except Exception as e:
            self.algorithm.Log(f"Error in EvaluateOptionStrategy: {str(e)}")
