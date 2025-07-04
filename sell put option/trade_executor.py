
from AlgorithmImports import *

class TradeExecutor:
    """
    Handles the execution of trades.
    This class is responsible for sending buy and sell orders to the broker.
    """
    def __init__(self, algorithm):
        """
        Initializes the TradeExecutor.
        
        Args:
            algorithm: A reference to the main algorithm instance.
        """
        self.algorithm = algorithm

    def enter_position(self, contract, quantity):
        """
        Enters a short put position by selling the specified contract.
        
        Args:
            contract: The option contract to sell.
            quantity: The number of contracts to sell.
        """
        try:
            # Sell the option contract.
            order = self.algorithm.Sell(contract.Symbol, quantity)
            
            # Update the algorithm's state variables.
            self.algorithm.current_contract = contract
            self.algorithm.last_trade_date = self.algorithm.Time.date()
            self.algorithm.trade_count += 1

            # Record the details of the trade.
            trade_info = {
                'date': self.algorithm.Time.date(),
                'symbol': contract.Symbol.Value,
                'strike': contract.Strike,
                'expiry': contract.Expiry,
                'quantity': quantity,
                'price': order.AverageFillPrice,
                'delta': self.algorithm.data_handler.get_option_delta(contract),
                'underlying_price': contract.UnderlyingLastPrice or contract.Strike
            }
            self.algorithm.trades.append(trade_info)

            self.algorithm.Log(f"Sold short put: {contract.Symbol.Value}, Strike: {contract.Strike}, Qty: {quantity}, Delta: {self.algorithm.data_handler.get_option_delta(contract):.2f}")
        except Exception as e:
            self.algorithm.Log(f"Error entering position: {str(e)}")

    def close_all_positions(self):
        """
        Closes all open positions by buying back the contracts.
        """
        if not self.algorithm.current_contract:
            return
        position = self.algorithm.Portfolio[self.algorithm.current_contract.Symbol]
        if position.Invested:
            try:
                # Buy back the option contract to close the position.
                order = self.algorithm.Buy(self.algorithm.current_contract.Symbol, position.Quantity)
                
                # Calculate and record the profit or loss for the trade.
                entry_price = self.algorithm.trades[-1]['price'] if self.algorithm.trades else 0
                exit_price = order.AverageFillPrice
                pnl = (entry_price - exit_price) * position.Quantity * 100
                self.algorithm.profit_loss += pnl
                
                # Update the trade details with the exit information.
                if self.algorithm.trades:
                    self.algorithm.trades[-1]['exit_price'] = exit_price
                    self.algorithm.trades[-1]['pnl'] = pnl
                    self.algorithm.trades[-1]['exit_date'] = self.algorithm.Time.date()
                
                self.algorithm.Log(f"Closed short put: {self.algorithm.current_contract.Symbol.Value} | PnL: ${pnl:.2f}")
                
                # Reset the state variables.
                self.algorithm.current_contract = None
                self.algorithm.last_trade_date = None
            except Exception as e:
                self.algorithm.Log(f"Error closing position: {str(e)}")
