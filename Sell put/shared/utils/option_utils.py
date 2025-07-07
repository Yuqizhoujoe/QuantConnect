# region imports
from AlgorithmImports import *
# endregion
"""
Option Utilities

This module provides reusable option contract selection and filtering utilities
that can be used across different option strategies.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date, timedelta
from .technical_indicators import OptionAnalysis
from shared.utils.market_analysis_types import MarketAnalysis


class OptionContractSelector:
    """Option contract selection utilities."""

    @staticmethod
    def filter_put_options(chain: List[Any]) -> List[Any]:
        """Filter for put options from option chain."""
        return [x for x in chain if x.Right == "Put"]

    @staticmethod
    def filter_by_expiry_window(
        contracts: List[Any], expiry_window: Tuple[date, date]
    ) -> List[Any]:
        """Filter contracts by expiry window."""
        return [
            c
            for c in contracts
            if expiry_window[0] <= c.Expiry.date() <= expiry_window[1]
        ]

    @staticmethod
    def filter_by_delta_range(
        contracts: List[Any], delta_range: Tuple[float, float], get_delta_func
    ) -> List[Any]:
        """Filter contracts by delta range."""
        delta_min, delta_max = delta_range
        return [
            c for c in contracts if delta_min <= abs(get_delta_func(c)) <= delta_max
        ]

    @staticmethod
    def filter_by_frequency(contracts: List[Any], frequency: str) -> List[Any]:
        """Filter contracts by expiration frequency."""
        if frequency == "any":
            return contracts

        return [
            c
            for c in contracts
            if OptionAnalysis.is_valid_option_expiry(c.Expiry, frequency)
        ]

    @staticmethod
    def select_best_contract(
        valid_contracts: List[Any],
        underlying_price: float,
        market_analysis: MarketAnalysis,
        target_delta_range: Tuple[float, float],
        get_delta_func,
    ) -> Optional[Any]:
        """
        Simplified contract selection focused primarily on delta.
        
        Removes complex market analysis and focuses on delta proximity to target range.
        """
        if not valid_contracts:
            return None

        # Calculate target delta (middle of range)
        target_delta = (target_delta_range[0] + target_delta_range[1]) / 2

        # Score each contract based primarily on delta
        scored_contracts = []

        for contract in valid_contracts:
            delta = abs(get_delta_func(contract))
            
            # Primary criterion: Delta proximity to target
            delta_score = 1.0 - abs(delta - target_delta) / target_delta
            
            # Bonus for being in the middle of the target range
            if target_delta_range[0] <= delta <= target_delta_range[1]:
                delta_score += 0.3
            
            # Secondary criterion: DTE (prefer middle range)
            dte = (contract.Expiry.date() - date.today()).days
            optimal_dte = 30  # Middle of typical range
            dte_score = 1.0 - abs(dte - optimal_dte) / optimal_dte
            
            # Weighted score (80% delta, 20% DTE)
            total_score = delta_score * 0.8 + dte_score * 0.2
            scored_contracts.append((contract, total_score))

        # Return contract with highest score
        scored_contracts.sort(key=lambda x: x[1], reverse=True)
        return scored_contracts[0][0] if scored_contracts else None

    @staticmethod
    def get_available_deltas(
        contracts: List[Any], expiry_window: Tuple[date, date], get_delta_func
    ) -> Tuple[float, float]:
        """Get available delta range for contracts in expiry window."""
        filtered_contracts = OptionContractSelector.filter_by_expiry_window(
            contracts, expiry_window
        )

        if not filtered_contracts:
            return (0.0, 0.0)

        deltas = [abs(get_delta_func(c)) for c in filtered_contracts]
        return (min(deltas), max(deltas))


class OptionDataValidator:
    """Option data validation utilities."""

    @staticmethod
    def validate_slice_data(slice_data: Any, ticker: str, option_symbol: Any) -> bool:
        """Validate that slice data contains required option information."""
        if not slice_data:
            return False

        if not hasattr(slice_data, "OptionChains") or slice_data.OptionChains is None:
            return False

        chain = slice_data.OptionChains.get(option_symbol)
        if not chain:
            return False

        return True

    @staticmethod
    def validate_contract_data(contract: Any) -> bool:
        """Validate that contract has required data."""
        required_attrs = ["Symbol", "Strike", "Expiry", "Right", "UnderlyingLastPrice"]

        for attr in required_attrs:
            if not hasattr(contract, attr):
                return False

        return True

    @staticmethod
    def validate_option_chain(chain: Any) -> bool:
        """Validate option chain data."""
        if not chain:
            return False

        # Check if chain has underlying price
        if not hasattr(chain, "Underlying") or not hasattr(chain.Underlying, "Price"):
            return False

        # Check if contracts have required data
        contracts = list(chain)[:5]  # Get first 5 contracts
        for contract in contracts:
            if not OptionDataValidator.validate_contract_data(contract):
                return False

        return True


class OptionTradeLogger:
    """Option trade logging utilities."""

    @staticmethod
    def log_trade_entry(
        algorithm: Any,
        contract: Any,
        quantity: int,
        market_analysis: MarketAnalysis,
        get_delta_func,
    ) -> None:
        """Log trade entry information with focus on delta."""
        delta = get_delta_func(contract)
        algorithm.Log(
            f"Sold short put: {contract.Symbol.Value}, "
            f"Strike: ${contract.Strike}, Qty: {quantity}, "
            f"Delta: {delta:.3f}"
        )

    @staticmethod
    def log_trade_exit(algorithm: Any, contract: Any, pnl: float) -> None:
        """Log trade exit information."""
        algorithm.Log(f"Closed short put: {contract.Symbol.Value} | PnL: ${pnl:.2f}")

    @staticmethod
    def log_no_valid_contracts(
        algorithm: Any,
        market_analysis: MarketAnalysis,
        target_delta: Tuple[float, float],
        available_deltas: Tuple[float, float],
    ) -> None:
        """Log when no valid contracts are found, focusing on delta ranges."""
        algorithm.Log(
            f"No valid puts found. "
            f"Target delta: {target_delta[0]:.3f}-{target_delta[1]:.3f}, "
            f"Available: {available_deltas[0]:.3f}-{available_deltas[1]:.3f}"
        )

    @staticmethod
    def create_trade_record(
        contract: Any, quantity: int, price: float, get_delta_func, current_date: date
    ) -> Dict[str, Any]:
        """Create a trade record for tracking."""
        return {
            "date": current_date,
            "symbol": contract.Symbol.Value,
            "strike": contract.Strike,
            "expiry": contract.Expiry,
            "quantity": quantity,
            "price": price,
            "delta": get_delta_func(contract),
            "underlying_price": getattr(
                contract, "UnderlyingLastPrice", contract.Strike
            ),
        }

