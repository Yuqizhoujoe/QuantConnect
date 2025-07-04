from AlgorithmImports import *
from datetime import timedelta
import numpy as np
from strategy_config import StrategyConfig

class EnhancedBroadcomShortPutStrategy(QCAlgorithm):

    def Initialize(self):
        # Load configuration
        self.config = StrategyConfig()
        
        # Strategy Parameters
        self.SetStartDate(*self.config.START_DATE)
        self.SetEndDate(*self.config.END_DATE)
        self.SetCash(self.config.INITIAL_CASH)
        
        # Asset Configuration
        self.ticker = self.config.TICKER
        self.AddEquity(self.ticker, self.config.RESOLUTION)
        self.option = self.AddOption(self.ticker, self.config.RESOLUTION)
        
        # Options Filter
        self.option.SetFilter(
            self.config.MIN_STRIKE_OFFSET, 
            self.config.MAX_STRIKE_OFFSET, 
            timedelta(self.config.MIN_DAYS_TO_EXPIRY), 
            timedelta(self.config.MAX_DAYS_TO_EXPIRY)
        )
        
        # Schedule evaluation
        self.Schedule.On(
            self.DateRules.EveryDay(self.ticker), 
            self.TimeRules.At(*self.config.EVALUATION_TIME), 
            self.EvaluateOptionStrategy
        )
        
        # State variables
        self.current_contract = None
        self.last_trade_date = None
        self.trade_count = 0
        self.profit_loss = 0
        
        # Performance tracking
        self.trades = []
        self.daily_pnl = []
        self.underlying_prices = []
        
        # Volatility tracking
        self.historical_volatility = None
        self.volatility_window = 30
        
        # Set benchmark
        self.SetBenchmark(self.ticker)

    def EvaluateOptionStrategy(self):
        """Main strategy evaluation logic"""
        try:
            # Update market data
            self.UpdateMarketData()
            
            # Check market conditions
            if not self.CheckMarketConditions():
                return
            
            # Check if we should close existing positions
            if self.ShouldClosePosition():
                self.CloseAllPositions()
                return
            
            # Check if we should enter new positions
            if self.ShouldEnterPosition():
                self.FindAndEnterPosition()
                
        except Exception as e:
            self.Log(f"Error in EvaluateOptionStrategy: {str(e)}")

    def UpdateMarketData(self):
        """Update market data and calculate indicators"""
        # Get current underlying price
        if self.Securities.ContainsKey(self.ticker):
            current_price = self.Securities[self.ticker].Price
            if current_price > 0:
                self.underlying_prices.append(current_price)
                
                # Keep only last 30 days of prices
                if len(self.underlying_prices) > self.volatility_window:
                    self.underlying_prices.pop(0)
                
                # Calculate historical volatility
                if len(self.underlying_prices) >= 2:
                    returns = np.diff(np.log(self.underlying_prices))
                    self.historical_volatility = np.std(returns) * np.sqrt(252)

    def CheckMarketConditions(self):
        """Check if market conditions are suitable for trading"""
        if not self.underlying_prices:
            return False
        
        current_price = self.underlying_prices[-1]
        
        # Check price range filter
        if self.config.ENABLE_MARKET_FILTERS:
            if current_price < self.config.MIN_UNDERLYING_PRICE or current_price > self.config.MAX_UNDERLYING_PRICE:
                return False
        
        # Check volatility filter
        if self.config.ENABLE_VOLATILITY_FILTER and self.historical_volatility:
            if (self.historical_volatility < self.config.MIN_HISTORICAL_VOL or 
                self.historical_volatility > self.config.MAX_HISTORICAL_VOL):
                return False
        
        return True

    def ShouldClosePosition(self):
        """Determine if we should close existing positions"""
        if not self.current_contract:
            return False
            
        position = self.Portfolio[self.current_contract.Symbol]
        if not position.Invested:
            return False
        
        # Close if contract is expiring soon
        days_to_expiry = (self.current_contract.Expiry - self.Time.date()).days
        if days_to_expiry <= self.config.MIN_DAYS_BEFORE_EXPIRY:
            if self.config.ENABLE_DETAILED_LOGGING:
                self.Log(f"Closing position due to expiration in {days_to_expiry} days")
            return True
        
        # Close if profit target reached
        unrealized_profit = position.UnrealizedProfit
        if unrealized_profit > 0:
            max_profit = self.current_contract.AskPrice * position.Quantity * 100
            if unrealized_profit >= self.config.PROFIT_TARGET_PCT * max_profit:
                if self.config.ENABLE_DETAILED_LOGGING:
                    self.Log(f"Closing position due to profit target: {unrealized_profit}")
                return True
        
        # Close if stop loss hit
        if unrealized_profit < -self.config.STOP_LOSS_MULTIPLIER * abs(self.current_contract.AskPrice * position.Quantity * 100):
            if self.config.ENABLE_DETAILED_LOGGING:
                self.Log(f"Closing position due to stop loss: {unrealized_profit}")
            return True
            
        return False

    def ShouldEnterPosition(self):
        """Determine if we should enter new positions"""
        if self.current_contract and self.Portfolio[self.current_contract.Symbol].Invested:
            return False
        
        if self.last_trade_date == self.Time.date():
            return False
        
        if self.Portfolio.MarginRemaining < self.config.MIN_MARGIN_REQUIRED:
            return False
            
        return True

    def FindAndEnterPosition(self):
        """Find suitable option contract and enter position"""
        chain = self.CurrentSlice.OptionChains.get(self.option.Symbol)
        if not chain:
            return
        
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
            if delta and self.config.TARGET_DELTA_MIN <= abs(delta) <= self.config.TARGET_DELTA_MAX:
                # Check implied volatility filter
                if self.config.USE_IMPLIED_VOLATILITY_FILTER:
                    iv = self.GetImpliedVolatility(put)
                    if iv and (iv < self.config.MIN_IV or iv > self.config.MAX_IV):
                        continue
                valid_puts.append(put)
        
        if not valid_puts:
            return
        
        # Filter by expiration range
        valid_puts = [put for put in valid_puts 
                     if self.config.MIN_DAYS_TO_EXPIRY <= (put.Expiry - self.Time.date()).days <= self.config.MAX_DAYS_TO_EXPIRY]
        
        if not valid_puts:
            return
        
        # Sort by closest to ATM
        valid_puts = sorted(valid_puts, key=lambda x: abs(x.Strike - underlying_price))
        
        selected_contract = valid_puts[0]
        
        # Calculate position size
        if self.config.USE_FIXED_QUANTITY:
            quantity = self.config.FIXED_QUANTITY
        else:
            quantity = self.CalculatePositionSize(selected_contract)
        
        if quantity <= 0:
            return
        
        self.EnterPosition(selected_contract, quantity)

    def CalculatePositionSize(self, contract):
        """Calculate appropriate position size based on risk management"""
        portfolio_value = self.Portfolio.TotalPortfolioValue
        max_position_value = portfolio_value * self.config.MAX_POSITION_SIZE
        
        # More sophisticated margin calculation
        margin_requirement = self.CalculateMarginRequirement(contract)
        
        quantity = int(max_position_value / margin_requirement)
        
        available_margin = self.Portfolio.MarginRemaining
        max_quantity_by_margin = int(available_margin / margin_requirement)
        
        quantity = min(quantity, max_quantity_by_margin)
        
        if quantity < 1:
            return 0
            
        return quantity

    def CalculateMarginRequirement(self, contract):
        """Calculate margin requirement for short put"""
        # Simplified margin calculation - in practice, this would be more complex
        underlying_price = contract.UnderlyingLastPrice
        strike_price = contract.Strike
        
        # Basic margin requirement for short put
        margin = max(strike_price * 0.20, strike_price - underlying_price) * 100
        return margin

    def EnterPosition(self, contract, quantity):
        """Enter the short put position"""
        try:
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
                    'underlying_price': contract.UnderlyingLastPrice,
                    'iv': self.GetImpliedVolatility(contract),
                    'historical_vol': self.historical_volatility
                }
                self.trades.append(trade_info)
                
                if self.config.ENABLE_DETAILED_LOGGING:
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
                order = self.Buy(self.current_contract.Symbol, position.Quantity)
                
                if order.Status == OrderStatus.Filled:
                    entry_price = self.trades[-1]['price'] if self.trades else 0
                    exit_price = order.AverageFillPrice
                    pnl = (entry_price - exit_price) * position.Quantity * 100
                    self.profit_loss += pnl
                    
                    if self.config.ENABLE_DETAILED_LOGGING:
                        self.Log(f"Closed position: {self.current_contract.Symbol.Value}, "
                                f"Exit Price: ${exit_price:.2f}, P&L: ${pnl:.2f}")
                    
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

    def GetImpliedVolatility(self, contract):
        """Get implied volatility with error handling"""
        try:
            if contract.ImpliedVolatility:
                return contract.ImpliedVolatility
            return None
        except:
            return None

    def OnData(self, slice: Slice):
        """Handle incoming data"""
        if self.config.TRACK_DAILY_PNL and self.current_contract:
            position = self.Portfolio[self.current_contract.Symbol]
            if position.Invested:
                daily_pnl = position.UnrealizedProfit
                self.daily_pnl.append({
                    'date': self.Time.date(),
                    'pnl': daily_pnl
                })

    def OnEndOfAlgorithm(self):
        """Called at the end of the algorithm"""
        self.Log("=== ENHANCED STRATEGY SUMMARY ===")
        self.Log(f"Total Trades: {self.trade_count}")
        self.Log(f"Total P&L: ${self.profit_loss:.2f}")
        self.Log(f"Final Portfolio Value: ${self.Portfolio.TotalPortfolioValue:.2f}")
        
        # Calculate performance metrics
        if self.trades:
            completed_trades = [t for t in self.trades if 'pnl' in t]
            if completed_trades:
                winning_trades = [t for t in completed_trades if t['pnl'] > 0]
                win_rate = len(winning_trades) / len(completed_trades) * 100
                self.Log(f"Win Rate: {win_rate:.1f}%")
                
                if winning_trades:
                    avg_win = np.mean([t['pnl'] for t in winning_trades])
                    self.Log(f"Average Win: ${avg_win:.2f}")
                
                losing_trades = [t for t in completed_trades if t['pnl'] < 0]
                if losing_trades:
                    avg_loss = np.mean([t['pnl'] for t in losing_trades])
                    self.Log(f"Average Loss: ${avg_loss:.2f}")
                
                # Calculate risk metrics
                total_return = (self.Portfolio.TotalPortfolioValue - self.config.INITIAL_CASH) / self.config.INITIAL_CASH * 100
                self.Log(f"Total Return: {total_return:.2f}%")
                
                if self.daily_pnl:
                    max_drawdown = self.CalculateMaxDrawdown()
                    self.Log(f"Maximum Drawdown: {max_drawdown:.2f}%")

    def CalculateMaxDrawdown(self):
        """Calculate maximum drawdown from daily P&L"""
        if not self.daily_pnl:
            return 0
        
        cumulative_pnl = np.cumsum([p['pnl'] for p in self.daily_pnl])
        running_max = np.maximum.accumulate(cumulative_pnl)
        drawdown = (cumulative_pnl - running_max) / running_max * 100
        return np.min(drawdown) 