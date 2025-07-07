from AlgorithmImports import *  # type: ignore
from datetime import timedelta
from typing import List, Optional, Any, Tuple, TYPE_CHECKING
from .risk_manager import RiskManager
from .market_analyzer import MarketAnalyzer
from shared.utils.option_utils import (
    OptionContractSelector,
    OptionDataValidator,
    OptionTradeLogger,
)
from shared.utils.trading_criteria import TradingContext
from .data_handler import DataHandler
from shared.utils.market_analysis_types import MarketAnalysis
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from ..sell_put_strategy import SellPutOptionStrategy


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
        Simplified parameter selection focused on delta-based decisions.

        Returns:
            Tuple of (market_analysis, delta_range, dte_range) or (None, None, None) if analysis fails
        """
        slice_data: Any = self.data_handler.latest_slice
        option_symbol: Any = self.strategy.option_symbols.get(self.ticker)
        chain: Any = slice_data.OptionChains.get(option_symbol)

        underlying_price: float = chain.Underlying.Price
        self.strategy.Log(f"{self.ticker} underlying price: ${underlying_price:.2f}")

        # Perform simplified market analysis (now just checks if we have price data)
        market_analysis: MarketAnalysis = (
            self.market_analyzer.analyze_market_conditions(underlying_price)
        )

        # Use fixed delta and DTE ranges for all conditions
        delta_range: Tuple[float, float] = (0.25, 0.75)  # Fixed range
        dte_range: Tuple[int, int] = (14, 45)  # Fixed range

        self.strategy.Log(
            f"{self.ticker} target delta range: {delta_range[0]:.2f}-{delta_range[1]:.2f}, DTE range: {dte_range[0]}-{dte_range[1]}"
        )

        return market_analysis, delta_range, dte_range

    def _filter_and_select_contracts(
        self,
        delta_range: Tuple[float, float],
        dte_range: Tuple[int, int],
        market_analysis: MarketAnalysis,
    ) -> Optional[Any]:
        """
        Simplified contract selection focused on delta-based filtering.

        Args:
            delta_range: Target delta range (min, max)
            dte_range: Target DTE range (min, max)
            market_analysis: Current market analysis (simplified)

        Returns:
            Selected contract or None if no suitable contract found
        """
        slice_data: Any = self.data_handler.latest_slice
        option_symbol: Any = self.strategy.option_symbols.get(self.ticker)
        chain: Any = slice_data.OptionChains.get(option_symbol)
        underlying_price: float = chain.Underlying.Price

        # Calculate expiry window
        expiry_window: Tuple[Any, Any] = (
            self.strategy.Time + timedelta(days=dte_range[0]),
            self.strategy.Time + timedelta(days=dte_range[1]),
        )

        # Filter for put options
        puts: List[Any] = OptionContractSelector.filter_put_options(chain)
        self.strategy.Log(f"{self.ticker} found {len(puts)} put options")

        if not puts:
            self.strategy.Log(f"{self.ticker} no put options available")
            return None

        # Filter by expiry window
        expiry_window_dates = (expiry_window[0].date(), expiry_window[1].date())
        puts = OptionContractSelector.filter_by_expiry_window(puts, expiry_window_dates)
        self.strategy.Log(f"{self.ticker} after expiry filter: {len(puts)} puts")

        # Filter by delta range (primary criteria)
        valid_puts = OptionContractSelector.filter_by_delta_range(
            puts, delta_range, self.data_handler.get_option_delta
        )
        self.strategy.Log(
            f"{self.ticker} after delta filter: {len(valid_puts)} valid puts"
        )

        if not valid_puts:
            # Log available deltas for debugging
            available_deltas = OptionContractSelector.get_available_deltas(
                puts, expiry_window_dates, self.data_handler.get_option_delta
            )
            self.strategy.Log(
                f"{self.ticker} no valid puts found. Target delta: {delta_range[0]:.2f}-{delta_range[1]:.2f}, Available: {available_deltas[0]:.2f}-{available_deltas[1]:.2f}"
            )
            return None

        # Select the best contract based primarily on delta proximity
        selected_contract = self._select_best_contract_by_delta(valid_puts, delta_range)

        if selected_contract:
            delta = abs(self.data_handler.get_option_delta(selected_contract))
            self.strategy.Log(
                f"{self.ticker} selected contract: {selected_contract.Symbol.Value}, Strike: ${selected_contract.Strike}, Delta: {delta:.3f}"
            )

        return selected_contract

    def _select_best_contract_by_delta(
        self, valid_puts: List[Any], delta_range: Tuple[float, float]
    ) -> Optional[Any]:
        """
        Select the best contract using criteria-based evaluation.
        
        Args:
            valid_puts: List of valid put contracts
            delta_range: Target delta range

        Returns:
            Best contract or None
        """
        if not valid_puts:
            return None

        # Score contracts using criteria system
        scored_contracts = []
        for contract in valid_puts:
            delta = abs(self.data_handler.get_option_delta(contract))
            dte = (contract.Expiry.date() - self.strategy.Time.date()).days
            
            # Create context for criteria evaluation
            underlying_price = self._get_underlying_price()
            
            # Get market analysis for additional context
            market_analysis = None
            if self.market_analyzer:
                market_analysis = self.market_analyzer.analyze_market_conditions(underlying_price)
            
            # Create TradingContext
            context = TradingContext(
                delta=delta,
                dte=dte,
                strike=contract.Strike,
                underlying_price=underlying_price,
                volatility=market_analysis.volatility.current if market_analysis else 0.0,
                market_regime=market_analysis.market_regime.value if market_analysis else "unknown",
                rsi=market_analysis.rsi if market_analysis else 50.0,
                trend_direction=market_analysis.trend.direction if market_analysis else "neutral",
                trend_strength=market_analysis.trend.strength if market_analysis else 0.5,
                contract=contract,
                timestamp=str(self.strategy.Time)
            )
            
            # Evaluate using criteria manager if available
            if self.market_analyzer and self.market_analyzer.criteria_manager:
                should_trade, score, message = self.market_analyzer.criteria_manager.should_trade(context)
                if should_trade:
                    scored_contracts.append((contract, score))
                    self.strategy.Log(f"{self.ticker}: Contract {contract.Symbol.Value} scored {score:.3f} - {message}")
                else:
                    self.strategy.Log(f"{self.ticker}: Contract {contract.Symbol.Value} rejected - {message}")
            else:
                # Fallback to simple delta-based scoring
                target_delta = (delta_range[0] + delta_range[1]) / 2
                delta_score = 1.0 - abs(delta - target_delta) / target_delta
                if delta_range[0] <= delta <= delta_range[1]:
                    delta_score += 0.2
                scored_contracts.append((contract, delta_score))

        # Sort by score and return the best
        if scored_contracts:
            scored_contracts.sort(key=lambda x: x[1], reverse=True)
            return scored_contracts[0][0]
        
        return None

    def _get_underlying_price(self) -> float:
        """Get the current underlying price."""
        try:
            slice_data = self.data_handler.latest_slice
            if not slice_data or not hasattr(slice_data, 'OptionChains'):
                return 0.0
                
            option_symbol = self.strategy.option_symbols.get(self.ticker)
            if not option_symbol:
                return 0.0
                
            chain = slice_data.OptionChains.get(option_symbol)
            if not chain or not hasattr(chain, 'Underlying'):
                return 0.0
                
            return chain.Underlying.Price
        except:
            return 0.0

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

