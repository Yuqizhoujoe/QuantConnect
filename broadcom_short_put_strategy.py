from AlgorithmImports import *
from datetime import timedelta
import numpy as np

class BroadcomShortPutStrategy(QCAlgorithm):

    def Initialize(self):
        # Strategy Parameters
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2025, 1, 1)
        self.SetCash(100000)
        
        # Asset Configuration
        self.ticker = "AVGO"
        self.AddEquity(self.ticker, Resolution.Minute)
        self.option = self.AddOption(self.ticker, Resolution.Minute)
        
        # Options Filter: ATM options expiring in 20-60 days
        self.option.SetFilter(-2, +1, timedelta(20), timedelta(60))
        
        # Strategy Parameters
        self.target_delta_min = 0.44
        self.target_delta_max = 0.50
        self.max_position_size = 0.05  # 5% of portfolio per trade
        self.max_portfolio_risk = 0.20  # 20% max portfolio risk
        self.days_to_expiry_min = 20
        self.days_to_expiry_max = 60
        
        # Schedule evaluation every day at 10 AM
        self.Schedule.On(self.DateRules.EveryDay(self.ticker), 
                         self.TimeRules.At(10, 0), 
                         self.EvaluateOptionStrategy)
        
        # State variables
        self.current_contract = None
        self.last_trade_date = None
        self.trade_count = 0
        self.profit_loss = 0
        
        # Performance tracking
        self.trades = []
        self.daily_pnl = []
        
        # Set benchmark
        self.SetBenchmark(self.ticker)

    def EvaluateOptionStrategy(self):
        """Main strategy evaluation logic"""
        try:
            # Check if we should close existing positions
            if self.ShouldClosePosition():
                self.CloseAllPositions()
                return
            
            # Check if we should enter new positions
            if self.ShouldEnterPosition():
                self.FindAndEnterPosition()
                
        except Exception as e:
            self.Log(f"Error in EvaluateOptionStrategy: {str(e)}")

    def ShouldClosePosition(self):
        """Determine if we should close existing positions"""
        if not self.current_contract:
            return False
            
        # Check if position exists
        position = self.Portfolio[self.current_contract.Symbol]
        if not position.Invested:
            return False
        
        # Close if contract is expiring soon (within 5 days)
        days_to_expiry = (self.current_contract.Expiry - self.Time.date()).days
        if days_to_expiry <= 5:
            self.Log(f"Closing position due to expiration in {days_to_expiry} days")
            return True
        
        # Close if profit target reached (50% of max profit)
        unrealized_profit = position.UnrealizedProfit
        if unrealized_profit > 0:
            max_profit = self.current_contract.AskPrice * position.Quantity * 100
            if unrealized_profit >= 0.5 * max_profit:
                self.Log(f"Closing position due to profit target: {unrealized_profit}")
                return True
        
        # Close if stop loss hit (2x max profit)
        if unrealized_profit < -2 * abs(self.current_contract.AskPrice * position.Quantity * 100):
            self.Log(f"Closing position due to stop loss: {unrealized_profit}")
            return True
            
        return False

    def ShouldEnterPosition(self):
        """Determine if we should enter new positions"""
        # Don't enter if we have existing positions
        if self.current_contract and self.Portfolio[self.current_contract.Symbol].Invested:
            return False
        
        # Don't enter if we've traded today
        if self.last_trade_date == self.Time.date():
            return False
        
        # Check if we have enough cash
        if self.Portfolio.MarginRemaining < 10000:
            return False
            
        return True

    def FindAndEnterPosition(self):
        """Find suitable option contract and enter position"""
        chain = self.CurrentSlice.OptionChains.get(self.option.Symbol)
        if not chain:
            return
        
        # Get current underlying price
        underlying_price = chain.Underlying.Price
        if not underlying_price:
            return
        
        # Filter for put options
        puts = [x for x in chain if x.Right == OptionRight.Put]
        if not puts:
            return
        
        # Filter by delta range
        valid_puts = []
        for put in puts:
            delta = self.GetOptionDelta(put)
            if delta and self.target_delta_min <= abs(delta) <= self.target_delta_max:
                valid_puts.append(put)
        
        if not valid_puts:
            return
        
        # Filter by expiration range
        valid_puts = [put for put in valid_puts 
                     if self.days_to_expiry_min <= (put.Expiry - self.Time.date()).days <= self.days_to_expiry_max]
        
        if not valid_puts:
            return
        
        # Sort by closest to ATM
        valid_puts = sorted(valid_puts, key=lambda x: abs(x.Strike - underlying_price))
        
        # Select the best contract
        selected_contract = valid_puts[0]
        
        # Calculate position size
        quantity = self.CalculatePositionSize(selected_contract)
        if quantity <= 0:
            return
        
        # Enter the position
        self.EnterPosition(selected_contract, quantity)

    def CalculatePositionSize(self, contract):
        """Calculate appropriate position size based on risk management"""
        # Get current portfolio value
        portfolio_value = self.Portfolio.TotalPortfolioValue
        
        # Calculate maximum position value (5% of portfolio)
        max_position_value = portfolio_value * self.max_position_size
        
        # Calculate margin requirement (approximate)
        margin_requirement = contract.Strike * 100  # Simplified margin calculation
        
        # Calculate quantity based on margin requirement
        quantity = int(max_position_value / margin_requirement)
        
        # Ensure we don't exceed available margin
        available_margin = self.Portfolio.MarginRemaining
        max_quantity_by_margin = int(available_margin / margin_requirement)
        
        quantity = min(quantity, max_quantity_by_margin)
        
        # Minimum quantity check
        if quantity < 1:
            return 0
            
        return quantity

    def EnterPosition(self, contract, quantity):
        """Enter the short put position"""
        try:
            # Place the order
            order = self.Sell(contract.Symbol, quantity)
            
            if order.Status == OrderStatus.Filled:
                self.current_contract = contract
                self.last_trade_date = self.Time.date()
                self.trade_count += 1
                
                # Log the trade
                trade_info = {
                    'date': self.Time.date(),
                    'symbol': contract.Symbol.Value,
                    'strike': contract.Strike,
                    'expiry': contract.Expiry,
                    'quantity': quantity,
                    'price': order.AverageFillPrice,
                    'delta': self.GetOptionDelta(contract),
                    'underlying_price': contract.UnderlyingLastPrice
                }
                self.trades.append(trade_info)
                
                self.Log(f"Entered short put position: {contract.Symbol.Value}, "
                        f"Strike: ${contract.Strike}, Expiry: {contract.Expiry}, "
                        f"Quantity: {quantity}, Price: ${order.AverageFillPrice:.2f}, "
                        f"Delta: {self.GetOptionDelta(contract):.3f}")
                        
        except Exception as e:
            self.Log(f"Error entering position: {str(e)}")

    def CloseAllPositions(self):
        """Close all option positions"""
        if not self.current_contract:
            return
            
        position = self.Portfolio[self.current_contract.Symbol]
        if position.Invested:
            try:
                # Buy to close the short position
                order = self.Buy(self.current_contract.Symbol, position.Quantity)
                
                if order.Status == OrderStatus.Filled:
                    # Calculate P&L
                    entry_price = self.trades[-1]['price'] if self.trades else 0
                    exit_price = order.AverageFillPrice
                    pnl = (entry_price - exit_price) * position.Quantity * 100
                    self.profit_loss += pnl
                    
                    self.Log(f"Closed position: {self.current_contract.Symbol.Value}, "
                            f"Exit Price: ${exit_price:.2f}, P&L: ${pnl:.2f}")
                    
                    # Update last trade
                    if self.trades:
                        self.trades[-1]['exit_price'] = exit_price
                        self.trades[-1]['pnl'] = pnl
                        self.trades[-1]['exit_date'] = self.Time.date()
                    
                    self.current_contract = None
                    
            except Exception as e:
                self.Log(f"Error closing position: {str(e)}")

    def GetOptionDelta(self, contract):
        """Get option delta with error handling"""
        try:
            if contract.Greeks and contract.Greeks.Delta is not None:
                return contract.Greeks.Delta
            return 0
        except:
            return 0

    def OnData(self, slice: Slice):
        """Handle incoming data"""
        # Track daily P&L
        if self.current_contract:
            position = self.Portfolio[self.current_contract.Symbol]
            if position.Invested:
                daily_pnl = position.UnrealizedProfit
                self.daily_pnl.append({
                    'date': self.Time.date(),
                    'pnl': daily_pnl
                })

    def OnEndOfAlgorithm(self):
        """Called at the end of the algorithm"""
        self.Log("=== STRATEGY SUMMARY ===")
        self.Log(f"Total Trades: {self.trade_count}")
        self.Log(f"Total P&L: ${self.profit_loss:.2f}")
        self.Log(f"Final Portfolio Value: ${self.Portfolio.TotalPortfolioValue:.2f}")
        
        # Calculate additional metrics
        if self.trades:
            winning_trades = [t for t in self.trades if 'pnl' in t and t['pnl'] > 0]
            win_rate = len(winning_trades) / len([t for t in self.trades if 'pnl' in t]) * 100
            self.Log(f"Win Rate: {win_rate:.1f}%")
            
            if winning_trades:
                avg_win = np.mean([t['pnl'] for t in winning_trades])
                self.Log(f"Average Win: ${avg_win:.2f}")
            
            losing_trades = [t for t in self.trades if 'pnl' in t and t['pnl'] < 0]
            if losing_trades:
                avg_loss = np.mean([t['pnl'] for t in losing_trades])
                self.Log(f"Average Loss: ${avg_loss:.2f}") 