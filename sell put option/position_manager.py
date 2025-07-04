
from AlgorithmImports import *
from datetime import timedelta

class PositionManager:
    """
    Handles the logic for entering, exiting, and managing positions.
    This class determines when to open a new position and when to close an existing one.
    """
    def __init__(self, algorithm, data_handler):
        """
        Initializes the PositionManager.
        
        Args:
            algorithm: A reference to the main algorithm instance.
            data_handler: A reference to the data handler instance.
        """
        self.algorithm = algorithm
        self.data_handler = data_handler

    def should_close_position(self):
        """
        Determines if the currently held position should be closed.
        A position is closed if it is near expiry.
        
        Returns:
            True if the position should be closed, False otherwise.
        """
        if not self.algorithm.current_contract:
            return False

        position = self.algorithm.Portfolio[self.algorithm.current_contract.Symbol]
        if not position.Invested:
            return False

        # Check the number of days until the option expires.
        days_to_expiry = (self.algorithm.current_contract.Expiry.date() - self.algorithm.Time.date()).days
        delta = abs(self.data_handler.get_option_delta(self.algorithm.current_contract))

        # Close the position if it's within 14 days of expiry to avoid assignment risk.
        if days_to_expiry <= 14:
            self.algorithm.Log(f"Rolling before expiry (DTE={days_to_expiry}, delta={delta:.2f})")
            return True

        return False

    def should_enter_position(self):
        """
        Determines if a new position should be opened.
        A new position is opened if there is no current position, no recent trades,
        and sufficient margin.
        
        Returns:
            True if a new position should be opened, False otherwise.
        """
        # Avoid opening a new position if we already hold the underlying stock.
        if self.algorithm.Portfolio[self.algorithm.ticker].Quantity != 0:
            return False
        # Avoid opening a new position if we already have an open option contract.
        if self.algorithm.current_contract and self.algorithm.Portfolio[self.algorithm.current_contract.Symbol].Invested:
            return False
        # Avoid trading more than once on the same day.
        if self.algorithm.last_trade_date == self.algorithm.Time.date():
            return False
        # Ensure there is enough margin to open a new position.
        if self.algorithm.Portfolio.MarginRemaining < 10000:
            return False
        return True

    def find_and_enter_position(self):
        """
        Finds a suitable option contract and enters a short put position.
        This method filters the option chain based on the configured parameters
        (delta, expiry) and selects the best contract to sell.
        """
        slice_data = self.data_handler.latest_slice
        if not slice_data:
            self.algorithm.Debug("No data available for evaluation")
            return

        chain = slice_data.OptionChains.get(self.algorithm.option.Symbol)
        if not chain:
            self.algorithm.Debug("No option chain available")
            return

        underlying_price = chain.Underlying.Price
        
        # Filter for put options that match the configured frequency (monthly, weekly, etc.)
        puts = [x for x in chain
                if x.Right == OptionRight.Put and self.is_valid_option(x.Expiry)]

        if not puts:
            self.algorithm.Debug("No put options available for the selected frequency")
            return

        # Find a new contract with a more flexible expiry window (30-60 days).
        expiry_window = (self.algorithm.Time + timedelta(days=30), self.algorithm.Time + timedelta(days=60))
        
        # Filter the puts based on the target delta range and expiry window.
        valid_puts = [p for p in puts
                      if expiry_window[0].date() <= p.Expiry.date() <= expiry_window[1].date()
                      and self.algorithm.target_delta_min <= abs(self.data_handler.get_option_delta(p)) <= self.algorithm.target_delta_max]

        if not valid_puts:
            # Log more detailed information about available options
            available_deltas = [abs(self.data_handler.get_option_delta(p)) for p in puts if expiry_window[0].date() <= p.Expiry.date() <= expiry_window[1].date()]
            if available_deltas:
                min_delta = min(available_deltas)
                max_delta = max(available_deltas)
                self.algorithm.Debug(f"No valid puts found. Available puts: {len(puts)}, expiry window puts: {len([p for p in puts if expiry_window[0].date() <= p.Expiry.date() <= expiry_window[1].date()])}, delta range available: {min_delta:.2f}-{max_delta:.2f}, target delta: {self.algorithm.target_delta_min}-{self.algorithm.target_delta_max}")
            else:
                self.algorithm.Debug(f"No valid puts found. Available puts: {len(puts)}, target delta: {self.algorithm.target_delta_min}-{self.algorithm.target_delta_max}")
            return

        # Select the contract with the strike price closest to the underlying price.
        selected_contract = sorted(valid_puts, key=lambda x: abs(x.Strike - underlying_price))[0]
        
        # Calculate the position size and enter the trade.
        quantity = self.calculate_position_size(selected_contract)
        if quantity > 0:
            self.algorithm.trade_executor.enter_position(selected_contract, quantity)

    def is_valid_option(self, expiry):
        """
        Checks if an option's expiry matches the configured frequency.
        
        Args:
            expiry: The expiry date of the option contract.
            
        Returns:
            True if the option matches the frequency, False otherwise.
        """
        if self.algorithm.option_frequency == "monthly":
            # Monthly options typically expire on the 3rd Friday of the month.
            return expiry.weekday() == 4 and 15 <= expiry.day <= 21
        elif self.algorithm.option_frequency == "weekly":
            # Weekly options typically expire on Fridays.
            return expiry.weekday() == 4
        elif self.algorithm.option_frequency == "any":
            # No filter for 'any' frequency.
            return True
        return False

    def calculate_position_size(self, contract):
        """
        Calculates the number of contracts to sell based on the configured
        maximum position size and available margin.
        
        Args:
            contract: The option contract to be traded.
            
        Returns:
            The number of contracts to sell (quantity).
        """
        portfolio_value = self.algorithm.Portfolio.TotalPortfolioValue
        max_position_value = portfolio_value * self.algorithm.max_position_size
        
        # Calculate the margin requirement for a single contract.
        margin_requirement = contract.Strike * 100 * 0.2
        quantity = int(max_position_value / margin_requirement)
        
        # Ensure the position size does not exceed the available margin.
        available_margin = self.algorithm.Portfolio.MarginRemaining
        max_quantity_by_margin = int(available_margin / margin_requirement)
        
        quantity = min(quantity, max_quantity_by_margin)
        return quantity if quantity >= 1 else 0
