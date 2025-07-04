# region imports
from AlgorithmImports import *
from datetime import timedelta
import numpy as np
# endregion

class BroadcomMonthlyShortPutStrategy(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2025, 1, 1)
        self.SetCash(100000)

        self.ticker = "AVGO"
        self.AddEquity(self.ticker, Resolution.Minute)
        self.option = self.AddOption(self.ticker, Resolution.Minute)
        self.option.SetFilter(-2, +1, timedelta(14), timedelta(45))

        self.target_delta_min = 0.30
        self.target_delta_max = 0.50
        self.max_position_size = 0.20

        self.Schedule.On(self.DateRules.EveryDay(self.ticker),
                         self.TimeRules.At(11, 0),
                         self.EvaluateOptionStrategy)

        self.current_contract = None
        self.last_trade_date = None
        self.trade_count = 0
        self.profit_loss = 0
        self.trades = []
        self.daily_pnl = []
        self.latest_slice = None  # Store latest data slice

        self.SetBenchmark(self.ticker)

    def EvaluateOptionStrategy(self):
        try:
            # Use stored slice data instead of CurrentSlice
            if self.latest_slice is None:
                self.Debug("No data available for evaluation")
                return
                
            if self.ShouldClosePosition():
                self.CloseAllPositions()
                return

            if self.ShouldEnterPosition():
                self.FindAndEnterPosition(self.latest_slice)
        except Exception as e:
            self.Log(f"Error in EvaluateOptionStrategy: {str(e)}")

    def ShouldClosePosition(self):
        if not self.current_contract:
            return False

        position = self.Portfolio[self.current_contract.Symbol]
        if not position.Invested:
            return False

        days_to_expiry = (self.current_contract.Expiry.date() - self.Time.date()).days
        delta = abs(self.GetOptionDelta(self.current_contract))

        if days_to_expiry <= 14:
            self.Log(f"Rolling before expiry (DTE={days_to_expiry}, delta={delta:.2f})")
            return True

        return False

    def ShouldEnterPosition(self):
        if self.Portfolio[self.ticker].Quantity != 0:
            return False
        if self.current_contract and self.Portfolio[self.current_contract.Symbol].Invested:
            return False
        if self.last_trade_date == self.Time.date():
            return False
        if self.Portfolio.MarginRemaining < 10000:
            return False
        return True

    def FindAndEnterPosition(self, slice_data):
        chain = slice_data.OptionChains.get(self.option.Symbol)
        if not chain:
            self.Debug("No option chain available")
            return

        underlying_price = chain.Underlying.Price
        monthly_puts = [x for x in chain
                        if x.Right == OptionRight.Put and self.IsMonthlyOption(x.Expiry)]

        if not monthly_puts:
            self.Debug("No monthly put options available")
            return

        # Rolling → find new expiry ~6 weeks out (42–45 days)
        expiry_window = (self.Time + timedelta(days=42), self.Time + timedelta(days=45))
        valid_puts = [p for p in monthly_puts
                      if expiry_window[0].date() <= p.Expiry.date() <= expiry_window[1].date()
                      and self.target_delta_min <= abs(self.GetOptionDelta(p)) <= self.target_delta_max]

        if not valid_puts:
            self.Debug(f"No valid puts found. Available monthly puts: {len(monthly_puts)}, target delta: {self.target_delta_min}-{self.target_delta_max}")
            return

        selected_contract = sorted(valid_puts, key=lambda x: abs(x.Strike - underlying_price))[0]
        quantity = self.CalculatePositionSize(selected_contract)
        if quantity > 0:
            self.EnterPosition(selected_contract, quantity)

    def IsMonthlyOption(self, expiry):
        return expiry.weekday() == 4 and 15 <= expiry.day <= 21  # 3rd Friday of the month

    def CalculatePositionSize(self, contract):
        portfolio_value = self.Portfolio.TotalPortfolioValue
        max_position_value = portfolio_value * self.max_position_size
        margin_requirement = contract.Strike * 100 * 0.2
        quantity = int(max_position_value / margin_requirement)
        available_margin = self.Portfolio.MarginRemaining
        max_quantity_by_margin = int(available_margin / margin_requirement)
        quantity = min(quantity, max_quantity_by_margin)
        return quantity if quantity >= 1 else 0

    def EnterPosition(self, contract, quantity):
        try:
            order = self.Sell(contract.Symbol, quantity)
            self.current_contract = contract
            self.last_trade_date = self.Time.date()
            self.trade_count += 1

            trade_info = {
                'date': self.Time.date(),
                'symbol': contract.Symbol.Value,
                'strike': contract.Strike,
                'expiry': contract.Expiry,
                'quantity': quantity,
                'price': order.AverageFillPrice,
                'delta': self.GetOptionDelta(contract),
                'underlying_price': contract.UnderlyingLastPrice or contract.Strike
            }
            self.trades.append(trade_info)

            self.Log(f"Sold short put: {contract.Symbol.Value}, Strike: {contract.Strike}, Qty: {quantity}, Delta: {self.GetOptionDelta(contract):.2f}")
        except Exception as e:
            self.Log(f"Error entering position: {str(e)}")

    def CloseAllPositions(self):
        if not self.current_contract:
            return
        position = self.Portfolio[self.current_contract.Symbol]
        if position.Invested:
            try:
                order = self.Buy(self.current_contract.Symbol, position.Quantity)
                entry_price = self.trades[-1]['price'] if self.trades else 0
                exit_price = order.AverageFillPrice
                pnl = (entry_price - exit_price) * position.Quantity * 100
                self.profit_loss += pnl
                if self.trades:
                    self.trades[-1]['exit_price'] = exit_price
                    self.trades[-1]['pnl'] = pnl
                    self.trades[-1]['exit_date'] = self.Time.date()
                self.Log(f"Closed short put: {self.current_contract.Symbol.Value} | PnL: ${pnl:.2f}")
                self.current_contract = None
                self.last_trade_date = None  # Allow immediate re-entry
            except Exception as e:
                self.Log(f"Error closing position: {str(e)}")

    def GetOptionDelta(self, contract):
        try:
            return contract.Greeks.Delta if contract.Greeks and contract.Greeks.Delta is not None else 0
        except:
            return 0

    def OnData(self, slice: Slice):
        # Store the latest slice for use in scheduled events
        self.latest_slice = slice
        
        # Update daily PnL tracking
        if self.current_contract:
            position = self.Portfolio[self.current_contract.Symbol]
            if position.Invested:
                daily_pnl = position.UnrealizedProfit
                self.Plot("Daily PnL", "Unrealized PnL", daily_pnl)

    def OnEndOfAlgorithm(self):
        self.Log("=== STRATEGY COMPLETE ===")
        self.Log(f"Ticker: {self.ticker}")
        self.Log(f"Total Trades: {self.trade_count}")
        self.Log(f"Final Portfolio Value: ${self.Portfolio.TotalPortfolioValue:.2f}")
        self.Log(f"Total P&L: ${self.profit_loss:.2f}")

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


# Main strategy class
class SellPutOption(BroadcomMonthlyShortPutStrategy):
    """Main strategy class - using Broadcom Monthly Short Put Strategy"""
    pass
