from AlgorithmImports import *  # type: ignore
from datetime import date
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from shared.utils.constants import (
    DEFAULT_TARGET_DELTA_MIN,
    DEFAULT_TARGET_DELTA_MAX,
    DEFAULT_MAX_POSITION_SIZE,
    DEFAULT_OPTION_FREQUENCY,
    DEFAULT_STOCK_WEIGHT,
    MAX_PRICE_HISTORY_LENGTH,
    MAX_PNL_HISTORY_LENGTH,
)
from .data_handler import DataHandler
from .position_manager import PositionManager
from .market_analyzer import MarketAnalyzer
from .risk_manager import RiskManager
from shared.utils.option_utils import OptionTradeLogger

# Forward reference for type hinting
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .sell_put_strategy import SellPutOptionStrategy


@dataclass
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

    # Strategy reference
    strategy: "SellPutOptionStrategy"  # This is the SellPutOptionStrategy instance

    # Core stock information
    ticker: str
    config: Dict[str, Any]

    # Stock-specific state variables
    current_contract: Optional[Any] = field(default=None, init=False)
    last_trade_date: Optional[date] = field(default=None, init=False)
    trade_count: int = field(default=0, init=False)
    profit_loss: float = field(default=0.0, init=False)
    trades: List[Dict[str, Any]] = field(default_factory=list, init=False)
    daily_pnl: List[float] = field(default_factory=list, init=False)
    peak_portfolio_value: float = field(default=0.0, init=False)

    # Stock-specific data storage
    price_history: List[float] = field(default_factory=list, init=False)
    volatility_history: List[float] = field(default_factory=list, init=False)
    returns_history: List[float] = field(default_factory=list, init=False)

    # Trading parameters (set by _setup_stock_parameters)
    target_delta_min: float = field(default=DEFAULT_TARGET_DELTA_MIN, init=False)
    target_delta_max: float = field(default=DEFAULT_TARGET_DELTA_MAX, init=False)
    max_position_size: float = field(default=DEFAULT_MAX_POSITION_SIZE, init=False)
    option_frequency: str = field(default=DEFAULT_OPTION_FREQUENCY, init=False)
    weight: float = field(default=DEFAULT_STOCK_WEIGHT, init=False)
    enabled: bool = field(default=True, init=False)

    # Analysis modules (initialized in __post_init__)
    data_handler: Optional[DataHandler] = field(default=None, init=False)
    market_analyzer: Optional[MarketAnalyzer] = field(default=None, init=False)
    risk_manager: Optional[RiskManager] = field(default=None, init=False)
    position_manager: Optional[PositionManager] = field(default=None, init=False)

    def __post_init__(self):
        """Initialize modules and parameters after dataclass creation."""
        # Initialize stock-specific modules
        self.data_handler = DataHandler(strategy=self.strategy, ticker=self.ticker)
        self.market_analyzer = MarketAnalyzer(
            strategy=self.strategy, ticker=self.ticker
        )
        self.risk_manager = RiskManager(strategy=self.strategy, ticker=self.ticker)
        self.position_manager = PositionManager(
            strategy=self.strategy,
            data_handler=self.data_handler,
            ticker=self.ticker,
        )

        # Set up stock-specific parameters
        self._setup_stock_parameters()

    def _setup_stock_parameters(self) -> None:
        """Set up stock-specific trading parameters from config."""
        self.target_delta_min = self.config.get(
            "target_delta_min", DEFAULT_TARGET_DELTA_MIN
        )
        self.target_delta_max = self.config.get(
            "target_delta_max", DEFAULT_TARGET_DELTA_MAX
        )
        self.max_position_size = self.config.get(
            "max_position_size", DEFAULT_MAX_POSITION_SIZE
        )
        self.option_frequency = self.config.get(
            "option_frequency", DEFAULT_OPTION_FREQUENCY
        )
        self.weight = self.config.get("weight", DEFAULT_STOCK_WEIGHT)
        self.enabled = self.config.get("enabled", True)

    def set_current_contract(self, contract: Any) -> None:
        """
        Set the current contract for this stock.

        Args:
            contract: The option contract to set as current
        """
        self.current_contract = contract
        self.strategy.Log(
            f"{self.ticker}: Current contract set to {contract.Symbol if contract else 'None'}"
        )

    def set_last_trade_date(self, trade_date: date) -> None:
        """
        Set the last trade date for this stock.

        Args:
            trade_date: The date of the last trade
        """
        self.last_trade_date = trade_date
        self.strategy.Log(f"{self.ticker}: Last trade date set to {trade_date}")

    def clear_current_contract(self) -> None:
        """Clear the current contract for this stock."""
        if self.current_contract:
            self.strategy.Log(
                f"{self.ticker}: Clearing current contract {self.current_contract.Symbol}"
            )
        self.current_contract = None

    def increment_trade_count(self) -> None:
        """Increment the trade count for this stock."""
        self.trade_count += 1
        self.strategy.Log(
            f"{self.ticker}: Trade count incremented to {self.trade_count}"
        )

    def update_data(self, slice_data: Any) -> None:
        """
        Update stock-specific data from the latest slice.

        Args:
            slice_data: Latest data slice from the algorithm
        """
        if not self.enabled:
            return

        # Update data handler
        if self.data_handler:
            self.data_handler.update_data(slice_data)

        # Update price history for analysis using option chain data
        if (
            hasattr(slice_data, "OptionChains")
            and slice_data.OptionChains
            and self.strategy.option_symbols.get(self.ticker) in slice_data.OptionChains
        ):

            option_symbol = self.strategy.option_symbols.get(self.ticker)
            chain = slice_data.OptionChains.get(option_symbol)
            if (
                chain
                and hasattr(chain, "Underlying")
                and hasattr(chain.Underlying, "Price")
            ):
                price: float = chain.Underlying.Price
                self._update_price_history(price)

    def _update_price_history(self, price: float) -> None:
        """Update stock-specific price history."""
        self.price_history.append(price)

        # Keep only recent prices to avoid memory issues
        if len(self.price_history) > MAX_PRICE_HISTORY_LENGTH:
            self.price_history.pop(0)

    def should_trade(self) -> bool:
        """
        Determine if this stock should trade based on current conditions.

        Returns:
            True if the stock should trade, False otherwise
        """
        self.strategy.Log(f"should_trade called for {self.ticker}")

        if not self.enabled:
            self.strategy.Log(f"{self.ticker} is disabled")
            return False

        # Check if we have an open position
        if (
            self.current_contract
            and self.strategy.Portfolio[self.current_contract.Symbol].Invested
        ):
            self.strategy.Log(f"{self.ticker} has open position")
            return False

        # Check if we already traded today
        if self.last_trade_date == self.strategy.Time.date():
            self.strategy.Log(f"{self.ticker} already traded today")
            return False

        # Check if we own the underlying
        if self.strategy.Portfolio[self.ticker].Quantity != 0:
            self.strategy.Log(f"{self.ticker} owns underlying stock")
            return False

        # Check risk management conditions
        if self.risk_manager and self.risk_manager.should_stop_trading():
            self.strategy.Log(f"{self.ticker} risk manager says stop trading")
            return False

        self.strategy.Log(f"{self.ticker} should trade")
        return True

    def should_close_position(self) -> bool:
        """
        Determine if the current position should be closed.

        Returns:
            True if position should be closed, False otherwise
        """
        if self.position_manager:
            return self.position_manager.should_close_position(self.current_contract)
        return False

    def find_and_enter_position(self) -> None:
        """
        Find and enter a new position for this stock.
        """
        self.strategy.Log(f"find_and_enter_position called for {self.ticker}")

        if not self.should_trade():
            self.strategy.Log(
                f"{self.ticker} should not trade - skipping position entry"
            )
            return

        # Use position manager to find and enter position
        # The position manager will handle all the logic internally and has proper data validation
        try:
            self.strategy.Log(f"Calling position manager for {self.ticker}")
            if self.position_manager:
                self.position_manager.find_and_enter_position()
        except Exception as e:
            self.strategy.Log(
                f"Error in find_and_enter_position for {self.ticker}: {str(e)}"
            )

    def close_position(self) -> None:
        """
        Close the current position for this stock.
        """
        if not self.current_contract:
            return

        position: Any = self.strategy.Portfolio[self.current_contract.Symbol]
        if position.Invested:
            try:
                # Buy back the option contract to close the position
                order: Any = self.strategy.Buy(
                    self.current_contract.Symbol, position.Quantity
                )

                # Calculate and record the profit or loss for the trade
                if self.trades:
                    entry_price: float = self.trades[-1]["price"]
                    exit_price: float = order.AverageFillPrice
                    pnl: float = (entry_price - exit_price) * position.Quantity * 100
                    self.profit_loss += pnl

                    # Update the trade details with the exit information
                    self.trades[-1]["exit_price"] = exit_price
                    self.trades[-1]["pnl"] = pnl
                    self.trades[-1]["exit_date"] = self.strategy.Time.date()

                    # Log trade exit using option utilities
                    OptionTradeLogger.log_trade_exit(
                        self.strategy, self.current_contract, pnl
                    )

                # Reset the current contract
                self.clear_current_contract()
                self.strategy.Log(f"{self.ticker} position closed successfully")
            except Exception as e:
                self.strategy.Log(f"Error closing position: {str(e)}")
                # Reset the current contract even if there's an error
                self.clear_current_contract()

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for this stock.

        Returns:
            Dictionary with performance metrics
        """
        return {
            "ticker": self.ticker,
            "trade_count": self.trade_count,
            "profit_loss": self.profit_loss,
            "current_position": (
                self.current_contract.Symbol if self.current_contract else None
            ),
            "enabled": self.enabled,
            "weight": self.weight,
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
        if len(self.daily_pnl) > MAX_PNL_HISTORY_LENGTH:
            self.daily_pnl.pop(0)
