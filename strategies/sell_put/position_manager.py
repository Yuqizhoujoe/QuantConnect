
from AlgorithmImports import *
from datetime import timedelta, date
from typing import Dict, List, Optional, Any, Tuple, Union
from core.risk_manager import RiskManager
from core.market_analyzer import MarketAnalyzer

# Ensure OptionRight is available
from AlgorithmImports import OptionRight

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
    def __init__(self, algorithm: Any, data_handler: Any, ticker: str, stock_manager: Any) -> None:
        """
        Initialize the PositionManager with integrated risk and market analysis.
        
        Args:
            algorithm: Reference to the main algorithm instance
            data_handler: Reference to the data handler instance
            ticker: Stock ticker symbol for this position manager
            stock_manager: Reference to the stock manager instance
        """
        self.algorithm: Any = algorithm
        self.data_handler: Any = data_handler
        self.ticker: str = ticker
        self.stock_manager: Any = stock_manager
        
        # Initialize integrated analysis modules
        self.risk_manager: RiskManager = RiskManager(algorithm, ticker)
        self.market_analyzer: MarketAnalyzer = MarketAnalyzer(algorithm, ticker)

    def should_close_position(self) -> bool:
        """
        Enhanced position exit logic with risk management considerations.
        
        Determines if the currently held position should be closed based on:
        1. Days to expiration (DTE) - avoid assignment risk
        2. Risk management rules
        3. Market condition changes
        
        Returns:
            True if the position should be closed, False otherwise
        """
        # Basic position check
        if not self.stock_manager.current_contract:
            return False

        position: Any = self.algorithm.Portfolio[self.stock_manager.current_contract.Symbol]
        if not position.Invested:
            return False

        # Calculate days to expiration and current delta
        days_to_expiry: int = (self.stock_manager.current_contract.Expiry.date() - self.algorithm.Time.date()).days
        delta: float = abs(self.data_handler.get_option_delta(self.stock_manager.current_contract))

        # Check if delta is out of the target range
        delta_out_of_range: bool = delta < self.stock_manager.target_delta_min or delta > self.stock_manager.target_delta_max
        
        # Close position if within 14 days of expiry AND delta is out of range
        # This ensures we only roll when both conditions are met
        if days_to_expiry <= 14 and delta_out_of_range:
            self.algorithm.Log(f"Rolling position - DTE={days_to_expiry}, delta={delta:.2f} (target: {self.stock_manager.target_delta_min:.2f}-{self.stock_manager.target_delta_max:.2f})")
            return True

        return False

    def should_enter_position(self) -> bool:
        """
        Enhanced position entry logic with comprehensive risk and market analysis.
        
        This method implements multiple layers of checks:
        1. Basic position and timing checks
        2. Risk management circuit breakers
        3. Market condition analysis
        4. Trading filter evaluation
        
        Returns:
            True if a new position should be opened, False otherwise
        """
        # Layer 1: Basic position and timing checks
        if self.algorithm.Portfolio[self.ticker].Quantity != 0:
            return False  # Don't trade if we own the underlying
        if self.stock_manager.current_contract and self.algorithm.Portfolio[self.stock_manager.current_contract.Symbol].Invested:
            return False  # Don't trade if we have an open position
        if self.stock_manager.last_trade_date == self.algorithm.Time.date():
            return False  # Don't trade multiple times per day
        if self.algorithm.Portfolio.MarginRemaining < 10000:
            return False  # Ensure sufficient margin
            
        # Layer 2: Risk management circuit breakers
        if self.risk_manager.should_stop_trading():
            self.algorithm.Log("Trading stopped due to risk limits")
            return False
            
        # Layer 3: Market data availability check
        slice_data: Any = self.data_handler.latest_slice
        if not slice_data:
            return False
            
        chain: Any = slice_data.OptionChains.get(self.algorithm.option_symbols.get(self.ticker))
        if not chain:
            return False
            
        # Layer 4: Market condition analysis
        underlying_price: float = chain.Underlying.Price
        market_analysis: Dict[str, Any] = self.market_analyzer.analyze_market_conditions(underlying_price)
        
        # Check if we should avoid trading based on market conditions
        if self.market_analyzer.should_avoid_trading(market_analysis):
            self.algorithm.Log(f"Avoiding trade due to market conditions: {market_analysis['market_regime']}")
            return False
            
        return True

    def find_and_enter_position(self) -> None:
        """
        Enhanced option selection with dynamic parameter adjustment and market analysis.
        
        This method represents the core intelligence of the strategy:
        1. Analyzes current market conditions
        2. Adjusts trading parameters dynamically
        3. Selects optimal contracts using multiple criteria
        4. Applies risk-managed position sizing
        5. Executes trades with comprehensive logging
        
        The strategy adapts to market conditions rather than using fixed parameters.
        """
        # Step 1: Validate data availability - use latest slice from data handler
        slice_data: Any = self.data_handler.latest_slice
        if not slice_data:
            self.algorithm.Debug(f"No current slice data available for {self.ticker}")
            return
            
        if not hasattr(slice_data, 'OptionChains') or slice_data.OptionChains is None:
            self.algorithm.Debug(f"No option chains data available for {self.ticker}")
            return

        option_symbol: Any = self.algorithm.option_symbols.get(self.ticker)
        if not option_symbol:
            self.algorithm.Debug(f"No option symbol found for {self.ticker}")
            return

        chain: Any = slice_data.OptionChains.get(option_symbol)
        if not chain:
            self.algorithm.Debug(f"No option chain available for {self.ticker}")
            return

        underlying_price: float = chain.Underlying.Price
        
        # Step 2: Perform comprehensive market analysis
        market_analysis: Dict[str, Any] = self.market_analyzer.analyze_market_conditions(underlying_price)
        
        # Step 3: Get dynamic trading parameters based on market conditions
        optimal_delta_range: Tuple[float, float] = self.market_analyzer.get_optimal_delta_range(market_analysis)
        optimal_dte_range: Tuple[int, int] = self.market_analyzer.get_optimal_dte_range(market_analysis)
        
        # Use dynamic ranges or fall back to configured ranges
        delta_min: float = optimal_delta_range[0]
        delta_max: float = optimal_delta_range[1]
        dte_min: int = optimal_dte_range[0]
        dte_max: int = optimal_dte_range[1]
        
        # Step 4: Calculate dynamic expiry window based on market conditions
        expiry_window: Tuple[Any, Any] = (self.algorithm.Time + timedelta(days=dte_min), 
                        self.algorithm.Time + timedelta(days=dte_max))
        
        # Step 5: Filter for put options
        puts: List[Any] = [x for x in chain if x.Right == OptionRight.Put]
        
        if not puts:
            self.algorithm.Debug("No put options available")
            return

        # Step 6: Apply frequency filter if specified (monthly, weekly, etc.)
        if self.stock_manager.option_frequency != "any":
            puts = [p for p in puts if self.is_valid_option(p.Expiry)]
            
        if not puts:
            self.algorithm.Debug("No put options available for the selected frequency")
            return

        # Step 7: Filter by dynamic expiry window and delta range
        valid_puts: List[Any] = [p for p in puts
                      if expiry_window[0].date() <= p.Expiry.date() <= expiry_window[1].date()
                      and delta_min <= abs(self.data_handler.get_option_delta(p)) <= delta_max]

        if not valid_puts:
            # Enhanced logging with market analysis context
            available_deltas: List[float] = [abs(self.data_handler.get_option_delta(p)) for p in puts 
                              if expiry_window[0].date() <= p.Expiry.date() <= expiry_window[1].date()]
            if available_deltas:
                min_delta: float = min(available_deltas)
                max_delta: float = max(available_deltas)
                self.algorithm.Log(f"No valid puts found. Market: {market_analysis['market_regime']}, "
                                 f"Target delta: {delta_min:.2f}-{delta_max:.2f}, "
                                 f"Available: {min_delta:.2f}-{max_delta:.2f}")
            return

        # Step 8: Select optimal contract using advanced criteria
        selected_contract: Optional[Any] = self.select_best_contract(valid_puts, underlying_price, market_analysis)
        
        if selected_contract:
            # Step 9: Calculate risk-managed position size
            quantity: int = self.risk_manager.calculate_position_size(selected_contract, underlying_price)
            if quantity > 0:
                # Step 10: Log comprehensive trade information
                self.algorithm.Log(f"Market conditions: {market_analysis['market_regime']}, "
                                 f"Volatility: {market_analysis['volatility']['regime']}, "
                                 f"RSI: {market_analysis['rsi']:.1f}")
                
                # Execute the trade and update stock manager
                try:
                    order: Any = self.algorithm.Sell(selected_contract.Symbol, quantity)
                    self.stock_manager.current_contract = selected_contract
                    self.stock_manager.last_trade_date = self.algorithm.Time.date()
                    self.stock_manager.trade_count += 1
                    
                    # Record trade details
                    trade_info: Dict[str, Any] = {
                        'date': self.algorithm.Time.date(),
                        'symbol': selected_contract.Symbol.Value,
                        'strike': selected_contract.Strike,
                        'expiry': selected_contract.Expiry,
                        'quantity': quantity,
                        'price': order.AverageFillPrice,
                        'delta': self.data_handler.get_option_delta(selected_contract),
                        'underlying_price': selected_contract.UnderlyingLastPrice or selected_contract.Strike
                    }
                    self.stock_manager.trades.append(trade_info)
                    
                    self.algorithm.Log(f"Sold short put: {selected_contract.Symbol.Value}, Strike: {selected_contract.Strike}, Qty: {quantity}, Delta: {self.data_handler.get_option_delta(selected_contract):.2f}")
                except Exception as e:
                    self.algorithm.Log(f"Error entering position: {str(e)}")

    def select_best_contract(self, valid_puts: List[Any], underlying_price: float, market_analysis: Dict[str, Any]) -> Optional[Any]:
        """
        Advanced contract selection using multiple criteria and market analysis.
        
        This method scores each contract based on multiple factors:
        1. Strike proximity to current price
        2. Delta alignment with target range
        3. Days to expiration optimization
        4. Market regime adjustments
        
        The scoring system adapts to market conditions to select the most
        suitable contract for the current environment.
        
        Args:
            valid_puts: List of put contracts that meet basic criteria
            underlying_price: Current underlying price
            market_analysis: Complete market analysis results
            
        Returns:
            Best contract to trade based on scoring system
        """
        if not valid_puts:
            return None
            
        # Score each contract based on multiple criteria
        scored_contracts: List[Tuple[Any, float]] = []
        
        for contract in valid_puts:
            # Get contract characteristics
            delta: float = abs(self.data_handler.get_option_delta(contract))
            dte: int = (contract.Expiry.date() - self.algorithm.Time.date()).days
            
            # Criterion 1: Strike proximity score (prefer strikes closer to current price)
            # This helps select strikes that are more likely to be at-the-money
            strike_distance: float = abs(contract.Strike - underlying_price) / underlying_price
            strike_score: float = 1 - min(strike_distance, 0.1) / 0.1  # Normalize to 0-1
            
            # Criterion 2: Delta score (prefer middle of target range)
            # This optimizes for the sweet spot of our delta range
            target_delta_mid: float = (self.stock_manager.target_delta_min + self.stock_manager.target_delta_max) / 2
            delta_score: float = 1 - abs(delta - target_delta_mid) / target_delta_mid
            
            # Criterion 3: DTE score (prefer optimal DTE)
            # This balances time decay with assignment risk
            optimal_dte: int = 45  # Middle of typical range (30-60 days)
            dte_score: float = 1 - abs(dte - optimal_dte) / optimal_dte
            
            # Criterion 4: Market regime adjustments
            # Adjust scoring based on current market conditions
            regime: str = market_analysis['market_regime']
            if regime == 'bullish_low_vol':
                # Prefer higher strikes in bullish low vol (more aggressive)
                strike_score *= 1.2
            elif regime == 'bearish_high_vol':
                # Prefer lower strikes in bearish high vol (more conservative)
                strike_score *= 0.8
                
            # Calculate weighted total score
            # Weights: 40% strike proximity, 40% delta alignment, 20% DTE optimization
            total_score: float = strike_score * 0.4 + delta_score * 0.4 + dte_score * 0.2
            scored_contracts.append((contract, total_score))
        
        # Return contract with highest score
        scored_contracts.sort(key=lambda x: x[1], reverse=True)
        return scored_contracts[0][0] if scored_contracts else None

    def is_valid_option(self, expiry: date) -> bool:
        """
        Check if an option's expiry matches the configured frequency.
        
        This method filters options based on their expiration pattern:
        - Monthly: 3rd Friday of the month
        - Weekly: Any Friday
        - Any: No filtering
        
        Args:
            expiry: The expiry date of the option contract
            
        Returns:
            True if the option matches the frequency, False otherwise
        """
        if self.stock_manager.option_frequency == "monthly":
            # Monthly options typically expire on the 3rd Friday of the month
            # Friday = weekday 4 (Monday=0, Sunday=6)
            return expiry.weekday() == 4 and 15 <= expiry.day <= 21
        elif self.stock_manager.option_frequency == "weekly":
            # Weekly options typically expire on Fridays
            return expiry.weekday() == 4
        elif self.stock_manager.option_frequency == "any":
            # No filter for 'any' frequency - accept all expiries
            return True
        return False
