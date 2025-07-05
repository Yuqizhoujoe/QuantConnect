from AlgorithmImports import *
from datetime import timedelta, date
from typing import Dict, List, Optional, Any, Union
from core.data_handler import DataHandler
from .position_manager import PositionManager
from core.market_analyzer import MarketAnalyzer
from core.risk_manager import RiskManager

class StockManager:
    """
    Manages individual stock trading logic and state.
    
    This class encapsulates all the logic for a single stock, including:
    - Stock-specific data handling
    - Position management for this stock
    - Market analysis for this stock
    - Risk management for this stock
    - Trade execution for this stock
    
    Each stock gets its own instance of this class.
    """
    
    def __init__(self, algorithm: Any, ticker: str, stock_config: Dict[str, Any]) -> None:
        """
        Initialize a StockManager for a specific ticker.
        
        Args:
            algorithm: Reference to the main algorithm instance
            ticker: Stock ticker symbol
            stock_config: Configuration dictionary for this stock
        """
        self.algorithm: Any = algorithm
        self.ticker: str = ticker
        self.config: Dict[str, Any] = stock_config
        
        # Stock-specific state variables
        self.current_contract: Optional[Any] = None
        self.last_trade_date: Optional[date] = None
        self.trade_count: int = 0
        self.profit_loss: float = 0.0
        self.trades: List[Dict[str, Any]] = []
        self.daily_pnl: List[float] = []
        self.peak_portfolio_value: float = 0.0
        
        # Stock-specific data storage
        self.price_history: List[float] = []
        self.volatility_history: List[float] = []
        self.returns_history: List[float] = []
        
        # Initialize stock-specific modules
        self.data_handler: DataHandler = DataHandler(algorithm, ticker)
        self.market_analyzer: MarketAnalyzer = MarketAnalyzer(algorithm, ticker)
        self.risk_manager: RiskManager = RiskManager(algorithm, ticker)
        self.position_manager: PositionManager = PositionManager(algorithm, self.data_handler, ticker, self)
        
        # Set up stock-specific parameters
        self._setup_stock_parameters()
        
    def _setup_stock_parameters(self) -> None:
        """Set up stock-specific trading parameters from config."""
        self.target_delta_min: float = self.config.get('target_delta_min', 0.25)
        self.target_delta_max: float = self.config.get('target_delta_max', 0.75)
        self.max_position_size: float = self.config.get('max_position_size', 0.20)
        self.option_frequency: str = self.config.get('option_frequency', 'monthly')
        self.weight: float = self.config.get('weight', 0.25)
        self.enabled: bool = self.config.get('enabled', True)
        
    def update_data(self, slice_data: Any) -> None:
        """
        Update stock-specific data from the latest slice.
        
        Args:
            slice_data: Latest data slice from the algorithm
        """
        if not self.enabled:
            return
            
        # Update data handler
        self.data_handler.update_data(slice_data)
        
        # Update price history for analysis
        if self.ticker in slice_data.Equity:
            price: float = slice_data.Equity[self.ticker].Price
            self._update_price_history(price)
            
    def _update_price_history(self, price: float) -> None:
        """Update stock-specific price history."""
        self.price_history.append(price)
        
        # Keep only recent prices to avoid memory issues
        max_history: int = 100
        if len(self.price_history) > max_history:
            self.price_history.pop(0)
            
    def should_trade(self) -> bool:
        """
        Determine if this stock should trade based on current conditions.
        
        Returns:
            True if the stock should trade, False otherwise
        """
        if not self.enabled:
            return False
            
        # Check if we have an open position
        if self.current_contract and self.algorithm.Portfolio[self.current_contract.Symbol].Invested:
            return False
            
        # Check if we already traded today
        if self.last_trade_date == self.algorithm.Time.date():
            return False
            
        # Check if we own the underlying
        if self.algorithm.Portfolio[self.ticker].Quantity != 0:
            return False
            
        # Check risk management conditions
        if self.risk_manager.should_stop_trading():
            return False
            
        return True
        
    def should_close_position(self) -> bool:
        """
        Determine if the current position should be closed.
        
        Returns:
            True if position should be closed, False otherwise
        """
        return self.position_manager.should_close_position()
        
    def find_and_enter_position(self) -> None:
        """
        Find and enter a new position for this stock.
        """
        if not self.should_trade():
            return
            
        # Use position manager to find and enter position
        # The position manager will handle all the logic internally and has proper data validation
        try:
            self.position_manager.find_and_enter_position()
        except Exception as e:
            self.algorithm.Log(f"Error in find_and_enter_position for {self.ticker}: {str(e)}")
            
    def close_position(self) -> None:
        """
        Close the current position for this stock.
        """
        if not self.current_contract:
            return
            
        position: Any = self.algorithm.Portfolio[self.current_contract.Symbol]
        if position.Invested:
            try:
                # Buy back the option contract to close the position
                order: Any = self.algorithm.Buy(self.current_contract.Symbol, position.Quantity)
                
                # Calculate and record the profit or loss for the trade
                if self.trades:
                    entry_price: float = self.trades[-1]['price']
                    exit_price: float = order.AverageFillPrice
                    pnl: float = (entry_price - exit_price) * position.Quantity * 100
                    self.profit_loss += pnl
                    
                    # Update the trade details with the exit information
                    self.trades[-1]['exit_price'] = exit_price
                    self.trades[-1]['pnl'] = pnl
                    self.trades[-1]['exit_date'] = self.algorithm.Time.date()
                    
                    self.algorithm.Log(f"Closed short put: {self.current_contract.Symbol.Value} | PnL: ${pnl:.2f}")
                
                # Reset the current contract
                self.current_contract = None
            except Exception as e:
                self.algorithm.Log(f"Error closing position: {str(e)}")
            
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for this stock.
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            'ticker': self.ticker,
            'trade_count': self.trade_count,
            'profit_loss': self.profit_loss,
            'current_position': self.current_contract.Symbol if self.current_contract else None,
            'enabled': self.enabled,
            'weight': self.weight
        }
        
    def get_correlation_data(self) -> List[float]:
        """
        Get correlation data for this stock.
        
        Returns:
            List of recent returns for correlation calculation
        """
        return self.returns_history[-60:] if len(self.returns_history) >= 60 else []
        
    def update_performance(self, pnl: float) -> None:
        """
        Update performance tracking for this stock.
        
        Args:
            pnl: Profit/loss for the current period
        """
        self.profit_loss += pnl
        self.daily_pnl.append(pnl)
        
        # Keep only recent PnL data
        if len(self.daily_pnl) > 100:
            self.daily_pnl.pop(0) 