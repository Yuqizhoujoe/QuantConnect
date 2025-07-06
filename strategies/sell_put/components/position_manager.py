from AlgorithmImports import *  # type: ignore
from datetime import timedelta, date
from typing import Dict, List, Optional, Any, Tuple, Union, TYPE_CHECKING
from .risk_manager import RiskManager
from .market_analyzer import MarketAnalyzer
from shared.utils.option_utils import (
    OptionContractSelector,
    OptionDataValidator,
    OptionTradeLogger,
)
from .data_handler import DataHandler
from shared.utils.market_analysis_types import MarketAnalysis
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from .sell_put_strategy import SellPutOptionStrategy


@dataclass
class PositionManager:
    """
    Enhanced position manager with advanced risk management and market analysis.

    This module integrates risk management and market analysis to make intelligent
    trading decisions. It handles:
    - Dynamic parameter adjustment based on market conditions
    - Advanced contract selection using multiple criteria
    - Risk-aware position entry and exit decisions
    - Market condition filtering to avoid unfavorable trades

    The goal is to adapt the strategy to current market conditions while maintaining
    strict risk controls.
    """

    strategy: "SellPutOptionStrategy"
    data_handler: DataHandler
    ticker: str

    # These are initialized in __post_init__
    risk_manager: RiskManager = field(init=False)
    market_analyzer: MarketAnalyzer = field(init=False)

    def __post_init__(self) -> None:
        self.risk_manager = RiskManager(self.strategy, self.ticker)
        self.market_analyzer = MarketAnalyzer(self.strategy, self.ticker)

    def should_close_position(self, current_contract=None) -> bool:
        """
        Determine if the current position should be closed.
        Args:
            current_contract: The current contract for this stock (should be passed from StockManager)
        Returns:
            True if position should be closed, False otherwise
        """
        if current_contract is None:
            # No contract to check
            return False
        position = self.strategy.Portfolio[current_contract.Symbol]
        if not position.Invested:
            return False
        days_to_expiry: int = (
            current_contract.Expiry.date() - self.strategy.Time.date()
        ).days
        delta: float = abs(self.data_handler.get_option_delta(current_contract))
        # TODO: Add logic for delta and DTE checks as needed
        return False

    def find_and_enter_position(self) -> None:
        """
        Enhanced option selection with dynamic parameter adjustment and market analysis.

        This method orchestrates the position entry process by calling smaller,
        focused functions for each step of the process.
        """
        self.strategy.Log(f"find_and_enter_position called for {self.ticker}")

        # Step 1: Validate data availability
        if not self._validate_data_availability():
            return

        # Step 2: Get market analysis and dynamic parameters
        market_analysis, delta_range, dte_range = (
            self._get_market_analysis_and_parameters()
        )
        if not market_analysis:
            return

        # Step 3: Filter and select contracts
        selected_contract = self._filter_and_select_contracts(
            delta_range, dte_range, market_analysis
        )
        if not selected_contract:
            return

        # Step 4: Execute the trade
        self._execute_trade(selected_contract, market_analysis)

    def _validate_data_availability(self) -> bool:
        """
        Validate that all required data is available for trading.

        Returns:
            True if data is valid, False otherwise
        """
        slice_data: Any = self.data_handler.latest_slice
        if not slice_data:
            self.strategy.Log(f"No current slice data available for {self.ticker}")
            return False

        option_symbol: Any = self.strategy.option_symbols.get(self.ticker)
        if not option_symbol:
            self.strategy.Log(f"No option symbol found for {self.ticker}")
            return False

        # Validate slice data using option utilities
        if not OptionDataValidator.validate_slice_data(
            slice_data, self.ticker, option_symbol
        ):
            self.strategy.Log(f"Invalid slice data for {self.ticker}")
            return False

        chain: Any = slice_data.OptionChains.get(option_symbol)
        if not OptionDataValidator.validate_option_chain(chain):
            self.strategy.Log(f"Invalid option chain for {self.ticker}")
            return False

        return True

    def _get_market_analysis_and_parameters(
        self,
    ) -> Tuple[Optional[MarketAnalysis], Tuple[float, float], Tuple[int, int]]:
        """
        Perform market analysis and get dynamic trading parameters.

        Returns:
            Tuple of (market_analysis, delta_range, dte_range) or (None, None, None) if analysis fails
        """
        slice_data: Any = self.data_handler.latest_slice
        option_symbol: Any = self.strategy.option_symbols.get(self.ticker)
        chain: Any = slice_data.OptionChains.get(option_symbol)

        underlying_price: float = chain.Underlying.Price
        self.strategy.Log(f"{self.ticker} underlying price: ${underlying_price:.2f}")

        # Perform comprehensive market analysis
        market_analysis: MarketAnalysis = (
            self.market_analyzer.analyze_market_conditions(underlying_price)
        )

        # Get dynamic trading parameters based on market conditions
        optimal_delta_range: Tuple[float, float] = (
            self.market_analyzer.get_optimal_delta_range(
                market_analysis.market_regime, market_analysis.volatility
            )
        )

        optimal_dte_range: Tuple[int, int] = self.market_analyzer.get_optimal_dte_range(
            market_analysis.volatility
        )

        # Use dynamic ranges or fall back to configured ranges
        delta_min, delta_max = optimal_delta_range
        dte_min, dte_max = optimal_dte_range

        self.strategy.Log(
            f"{self.ticker} target delta range: {delta_min:.2f}-{delta_max:.2f}, DTE range: {dte_min}-{dte_max}"
        )

        return market_analysis, (delta_min, delta_max), (dte_min, dte_max)

    def _filter_and_select_contracts(
        self,
        delta_range: Tuple[float, float],
        dte_range: Tuple[int, int],
        market_analysis: MarketAnalysis,
    ) -> Optional[Any]:
        """
        Filter available contracts and select the optimal one.

        Args:
            delta_range: Target delta range (min, max)
            dte_range: Target DTE range (min, max)
            market_analysis: Current market analysis

        Returns:
            Selected contract or None if no suitable contract found
        """
        slice_data: Any = self.data_handler.latest_slice
        option_symbol: Any = self.strategy.option_symbols.get(self.ticker)
        chain: Any = slice_data.OptionChains.get(option_symbol)
        underlying_price: float = chain.Underlying.Price

        # Calculate dynamic expiry window based on market conditions
        expiry_window: Tuple[Any, Any] = (
            self.strategy.Time + timedelta(days=dte_range[0]),
            self.strategy.Time + timedelta(days=dte_range[1]),
        )

        # Filter for put options using option utilities
        puts: List[Any] = OptionContractSelector.filter_put_options(chain)
        self.strategy.Log(f"{self.ticker} found {len(puts)} put options")

        if not puts:
            self.strategy.Log(f"{self.ticker} no put options available")
            return None

        # Apply frequency filter using option utilities
        puts = OptionContractSelector.filter_by_frequency(
            puts, self.strategy.stock_manager.option_frequency
        )
        self.strategy.Log(f"{self.ticker} after frequency filter: {len(puts)} puts")

        if not puts:
            self.strategy.Log(
                f"{self.ticker} no put options available for the selected frequency"
            )
            return None

        # Filter by dynamic expiry window and delta range using option utilities
        expiry_window_dates = (expiry_window[0].date(), expiry_window[1].date())
        puts = OptionContractSelector.filter_by_expiry_window(puts, expiry_window_dates)
        self.strategy.Log(f"{self.ticker} after expiry filter: {len(puts)} puts")

        # Filter by delta range
        valid_puts = OptionContractSelector.filter_by_delta_range(
            puts, delta_range, self.data_handler.get_option_delta
        )
        self.strategy.Log(
            f"{self.ticker} after delta filter: {len(valid_puts)} valid puts"
        )

        if not valid_puts:
            # Log when no valid contracts are found using option utilities
            available_deltas = OptionContractSelector.get_available_deltas(
                puts, expiry_window_dates, self.data_handler.get_option_delta
            )
            OptionTradeLogger.log_no_valid_contracts(
                self.strategy, market_analysis, delta_range, available_deltas
            )
            return None

        self.strategy.Log(
            f"valid puts: {valid_puts}, underlying price: {underlying_price}, market analysis: {market_analysis}, delta range: {delta_range}, expiry window: {expiry_window_dates}"
        )

        # Select optimal contract using option utilities
        selected_contract: Optional[Any] = OptionContractSelector.select_best_contract(
            valid_puts,
            underlying_price,
            market_analysis,
            delta_range,
            self.data_handler.get_option_delta,
        )

        if not selected_contract:
            self.strategy.Log(f"{self.ticker} no contract selected")
            return None

        self.strategy.Log(
            f"{self.ticker} selected contract: {selected_contract.Symbol.Value}, Strike: ${selected_contract.Strike}"
        )
        return selected_contract

    def _execute_trade(
        self, selected_contract: Any, market_analysis: MarketAnalysis
    ) -> None:
        """
        Execute the trade with risk management and logging.

        Args:
            selected_contract: The selected option contract to trade
            market_analysis: Current market analysis for logging
        """
        slice_data: Any = self.data_handler.latest_slice
        option_symbol: Any = self.strategy.option_symbols.get(self.ticker)
        chain: Any = slice_data.OptionChains.get(option_symbol)
        underlying_price: float = chain.Underlying.Price

        # Calculate risk-managed position size
        quantity: int = self.risk_manager.calculate_position_size(
            selected_contract, underlying_price
        )
        self.strategy.Log(
            f"{self.ticker} calculated position size: {quantity} contracts"
        )

        if quantity > 0:
            # Execute the trade and update stock manager
            try:
                self.strategy.Log(
                    f"{self.ticker} executing sell order for {quantity} contracts"
                )
                order: Any = self.strategy.Sell(selected_contract.Symbol, quantity)
                self.strategy.Log(
                    f"{self.ticker} order executed at ${order.AverageFillPrice:.2f}"
                )

                self._update_stock_manager(
                    selected_contract, order, quantity, market_analysis
                )

                self.strategy.Log(f"{self.ticker} position successfully entered")
            except Exception as e:
                self.strategy.Log(
                    f"Error entering position for {self.ticker}: {str(e)}"
                )
        else:
            self.strategy.Log(
                f"{self.ticker} position size is 0 - not entering position"
            )

    def _update_stock_manager(
        self,
        selected_contract: Any,
        order: Any,
        quantity: int,
        market_analysis: MarketAnalysis,
    ) -> None:
        """
        Update stock manager with trade information and log trade details.

        Args:
            selected_contract: The traded contract
            order: The executed order
            quantity: Number of contracts traded
            market_analysis: Current market analysis for logging
        """
        # This method should update the StockManager instance, not self.strategy.stock_manager
        # You may need to pass the StockManager instance to PositionManager or update via a callback
        # For now, leave this as a placeholder to avoid attribute errors
        pass
