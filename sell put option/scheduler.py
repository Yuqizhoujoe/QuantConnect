
from AlgorithmImports import *

class Scheduler:
    """
    Manages the scheduling of periodic events for the algorithm.
    This class centralizes the logic for when the strategy should be evaluated.
    """
    def __init__(self, algorithm, position_manager):
        """
        Initializes the Scheduler.
        
        Args:
            algorithm: A reference to the main algorithm instance.
            position_manager: A reference to the position manager instance.
        """
        self.algorithm = algorithm
        self.position_manager = position_manager

    def setup_events(self):
        """
        Sets up the scheduled events for the algorithm.
        This method schedules the `evaluate_option_strategy` to run daily.
        """
        self.algorithm.Schedule.On(self.algorithm.DateRules.EveryDay(self.algorithm.ticker),
                                  self.algorithm.TimeRules.At(11, 0),
                                  self.evaluate_option_strategy)

    def evaluate_option_strategy(self):
        """
        The core logic function that is called on a schedule.
        It checks if a position should be closed or if a new one should be entered.
        """
        try:
            # First, check if we need to close the current position.
            if self.position_manager.should_close_position():
                self.algorithm.trade_executor.close_all_positions()
                return

            # If not closing, check if we should enter a new position.
            if self.position_manager.should_enter_position():
                self.position_manager.find_and_enter_position()
        except Exception as e:
            self.algorithm.Log(f"Error in EvaluateOptionStrategy: {str(e)}")
