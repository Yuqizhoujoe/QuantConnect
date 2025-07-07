# type: ignore
"""
Simple Sell Put Strategy

A straightforward delta-based options strategy that:
- Sells puts when delta is between 0.4-0.5
- Rolls up when delta drops below 0.25
- Rolls down when delta rises above 0.75
- Maintains delta in the 0.4-0.5 range

This is a simplified version for testing and learning purposes.
"""

from AlgorithmImports import *  # type: ignore
from datetime import timedelta
import logging


class SimpleSellPutStrategy(QCAlgorithm):  # type: ignore
    """
    Simple delta-based sell put strategy.
    
    Trade Logic:
    - Target delta range: 0.4 - 0.5
    - Roll up when delta < 0.25
    - Roll down when delta > 0.75
    - Close position when delta < 0.1 or > 0.9
    """
    
    def Initialize(self):
        """Initialize the strategy."""
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2024, 12, 31)
        self.SetCash(100000)
        
        # Add symbols
        self.symbol = self.AddEquity("AAPL", Resolution.Daily).Symbol
        self.option = self.AddOption("AAPL", Resolution.Daily)
        
        # Set option filter
        self.option.SetFilter(-2, 2, timedelta(days=30), timedelta(days=60))
        
        # Strategy parameters
        self.target_delta_min = 0.4
        self.target_delta_max = 0.5
        self.roll_up_threshold = 0.25
        self.roll_down_threshold = 0.75
        self.close_threshold_low = 0.1
        self.close_threshold_high = 0.9
        
        # Position tracking
        self.current_position = None
        self.last_trade_time = None
        self.min_days_between_trades = 5
        
        # Logging
        self.Log("Simple Sell Put Strategy initialized")
        self.Log(f"Target delta range: {self.target_delta_min} - {self.target_delta_max}")
        self.Log(f"Roll up threshold: {self.roll_up_threshold}")
        self.Log(f"Roll down threshold: {self.roll_down_threshold}")
    
    def OnData(self, slice):
        """Main data processing method."""
        if not slice.OptionChains or self.option.Symbol not in slice.OptionChains:
            return
        
        # Check if enough time has passed since last trade
        if self.last_trade_time and (self.Time - self.last_trade_time).days < self.min_days_between_trades:
            return
        
        option_chain = slice.OptionChains[self.option.Symbol]
        if not option_chain:
            return
        
        # Get current position delta
        current_delta = self.get_current_position_delta()
        
        # Log current state
        if current_delta is not None:
            self.Log(f"Current delta: {current_delta:.3f}")
        else:
            self.Log("Current delta: None")
        
        # Decision logic
        if current_delta is None:
            # No position - look for entry opportunity
            self.try_entry(option_chain)
        else:
            # Have position - check for roll or close
            self.manage_position(option_chain, current_delta)
    
    def get_current_position_delta(self):
        """Get delta of current position."""
        if not self.Portfolio[self.symbol].Invested:
            return None
        
        # For simplicity, assume we have a put position
        # In real implementation, you'd calculate actual delta
        position = self.Portfolio[self.symbol]
        if position.Quantity < 0:  # Short position
            # Estimate delta based on position size and time
            # This is simplified - in reality you'd get from option chain
            return 0.45  # Placeholder
        return None
    
    def try_entry(self, option_chain):
        """Try to enter a new position."""
        # Find puts with delta in target range
        target_puts = []
        contract_count = 0
        for contract in option_chain:
            if contract.Right == OptionRight.Put:
                contract_count += 1
                delta = self.estimate_delta(contract)
                self.Log(f"Contract: {contract.Symbol}, Strike: {contract.Strike}, Expiry: {contract.Expiry}, Est. Delta: {delta:.3f}")
                if self.target_delta_min <= delta <= self.target_delta_max:
                    self.Log(f"  -> In target delta range: {self.target_delta_min}-{self.target_delta_max}")
                    target_puts.append((contract, delta))
        self.Log(f"Total put contracts checked: {contract_count}, In target range: {len(target_puts)}")
        
        if target_puts:
            # Sort by delta proximity to target
            target_puts.sort(key=lambda x: abs(x[1] - 0.45))
            best_contract, delta = target_puts[0]
            
            # Sell the put
            quantity = -1  # Sell 1 contract
            self.MarketOrder(best_contract.Symbol, quantity)
            self.current_position = best_contract
            self.last_trade_time = self.Time
            
            self.Log(f"ENTRY: Sold put {best_contract.Symbol} with delta {delta:.3f}")
        else:
            self.Log("No suitable put contracts found for entry.")
    
    def manage_position(self, option_chain, current_delta):
        """Manage existing position."""
        if current_delta < self.close_threshold_low:
            # Close position - delta too low
            self.close_position("Delta too low")
        elif current_delta > self.close_threshold_high:
            # Close position - delta too high
            self.close_position("Delta too high")
        elif current_delta < self.roll_up_threshold:
            # Roll up - sell higher strike put
            self.roll_position(option_chain, "up")
        elif current_delta > self.roll_down_threshold:
            # Roll down - sell lower strike put
            self.roll_position(option_chain, "down")
    
    def roll_position(self, option_chain, direction):
        """Roll position up or down."""
        if not self.current_position:
            return
        
        current_strike = self.current_position.Strike
        target_puts = []
        
        for contract in option_chain:
            if contract.Right == OptionRight.Put:
                if direction == "up" and contract.Strike > current_strike:
                    delta = self.estimate_delta(contract)
                    if self.target_delta_min <= delta <= self.target_delta_max:
                        target_puts.append((contract, delta))
                elif direction == "down" and contract.Strike < current_strike:
                    delta = self.estimate_delta(contract)
                    if self.target_delta_min <= delta <= self.target_delta_max:
                        target_puts.append((contract, delta))
        
        if target_puts:
            # Sort by delta proximity to target
            target_puts.sort(key=lambda x: abs(x[1] - 0.45))
            new_contract, delta = target_puts[0]
            
            # Close old position and open new one
            self.MarketOrder(self.current_position.Symbol, 1)  # Buy back old put
            self.MarketOrder(new_contract.Symbol, -1)  # Sell new put
            
            self.current_position = new_contract
            self.last_trade_time = self.Time
            
            self.Log(f"ROLL {direction.upper()}: {self.current_position.Symbol} -> {new_contract.Symbol} (delta: {delta:.3f})")
    
    def close_position(self, reason):
        """Close current position."""
        if self.current_position:
            self.MarketOrder(self.current_position.Symbol, 1)  # Buy back put
            self.Log(f"CLOSE: {reason} - Closed position {self.current_position.Symbol}")
            self.current_position = None
            self.last_trade_time = self.Time
    
    def estimate_delta(self, contract):
        """Estimate delta for a put contract (simplified)."""
        # This is a simplified delta estimation
        # In reality, you'd get this from the option chain data
        
        # Basic delta estimation for puts
        # Delta is negative for puts, typically between -1 and 0
        # We'll use absolute value for our logic
        
        # Estimate based on moneyness and time to expiration
        underlying_price = self.Securities[self.symbol].Price
        strike = contract.Strike
        days_to_expiry = (contract.Expiry - self.Time).days
        
        # Moneyness
        moneyness = underlying_price / strike
        
        # Simplified delta estimation
        if moneyness > 1.1:  # Deep ITM
            delta = 0.9
        elif moneyness > 1.05:  # ITM
            delta = 0.7
        elif moneyness > 0.95:  # ATM
            delta = 0.5
        elif moneyness > 0.9:  # OTM
            delta = 0.3
        else:  # Deep OTM
            delta = 0.1
        
        # Adjust for time decay
        if days_to_expiry < 10:
            delta *= 0.8  # Less delta for near expiry
        
        return delta
    
    def OnOrderEvent(self, orderEvent):
        """Handle order events."""
        if orderEvent.Status == OrderStatus.Filled:
            self.Log(f"Order filled: {orderEvent.Symbol} {orderEvent.FillQuantity} @ {orderEvent.FillPrice}")
    
    def OnEndOfAlgorithm(self):
        """Called at the end of the algorithm."""
        self.Log("=== SIMPLE SELL PUT STRATEGY COMPLETE ===")
        self.Log(f"Final Portfolio Value: ${self.Portfolio.TotalPortfolioValue:,.2f}")
        self.Log(f"Total Trades: {len(list(self.Transactions.GetOrders()))}")
        
        if self.current_position:
            self.Log(f"Open Position: {self.current_position.Symbol}")
        else:
            self.Log("No open positions") 
