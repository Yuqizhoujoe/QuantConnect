from AlgorithmImports import *
import numpy as np

class MarketAnalyzer:
    """
    Advanced market analysis for option selection and timing.
    
    This module provides comprehensive market analysis including:
    - Technical indicators (RSI, moving averages, volatility)
    - Market regime detection (bullish/bearish, high/low volatility)
    - Support and resistance levels
    - Option premium analysis
    - Dynamic parameter adjustment based on market conditions
    
    The goal is to adapt the strategy to current market conditions for better performance.
    """
    
    def __init__(self, algorithm):
        """
        Initialize the MarketAnalyzer with analysis parameters.
        
        Args:
            algorithm: Reference to the main algorithm instance
            
        Analysis Parameters:
            volatility_lookback: Days for volatility calculation
            rsi_period: Period for RSI calculation (typically 14)
            moving_average_period: Period for trend analysis (typically 50)
        """
        self.algorithm = algorithm
        
        # Technical analysis parameters
        self.volatility_lookback = 20      # Days for volatility calculation
        self.rsi_period = 14               # Period for RSI calculation
        self.moving_average_period = 50    # Period for moving average
        
        # Data storage for analysis
        self.price_history = []            # Store recent prices for analysis
        self.volatility_history = []       # Store volatility history
        
    def analyze_market_conditions(self, underlying_price):
        """
        Comprehensive market analysis for option trading decisions.
        
        This is the main method that combines all analysis components:
        1. Price trend analysis
        2. Volatility analysis
        3. RSI momentum analysis
        4. Support/resistance levels
        5. Market regime classification
        6. Option premium analysis
        
        Args:
            underlying_price: Current underlying price
            
        Returns:
            Dictionary with complete market analysis results
        """
        # Update price history for analysis
        self.update_price_history(underlying_price)
        
        # Return default analysis if insufficient data
        if len(self.price_history) < self.moving_average_period:
            return self.get_default_analysis()
            
        # Perform comprehensive market analysis
        analysis = {
            'trend': self.analyze_trend(),
            'volatility': self.analyze_volatility(),
            'rsi': self.calculate_rsi(),
            'support_resistance': self.find_support_resistance(),
            'market_regime': self.determine_market_regime(),
            'option_premium_richness': self.analyze_option_premiums()
        }
        
        return analysis
    
    def update_price_history(self, price):
        """
        Update price history for technical analysis.
        
        Maintains a rolling window of recent prices for analysis.
        
        Args:
            price: New price to add to history
        """
        self.price_history.append(price)
        
        # Keep only recent prices to avoid memory issues
        if len(self.price_history) > self.volatility_lookback:
            self.price_history.pop(0)
    
    def analyze_trend(self):
        """
        Analyze price trend using moving averages.
        
        Compares current price to moving average to determine trend direction.
        
        Returns:
            'bullish', 'bearish', or 'neutral'
        """
        if len(self.price_history) < self.moving_average_period:
            return 'neutral'
            
        current_price = self.price_history[-1]
        
        # Calculate simple moving average
        ma = np.mean(self.price_history[-self.moving_average_period:])
        
        # Determine trend based on price vs moving average
        if current_price > ma * 1.02:  # 2% above MA = bullish
            return 'bullish'
        elif current_price < ma * 0.98:  # 2% below MA = bearish
            return 'bearish'
        else:
            return 'neutral'  # Within 2% of MA = neutral
    
    def analyze_volatility(self):
        """
        Analyze price volatility using rolling standard deviation.
        
        Calculates both current and historical volatility to determine
        the current volatility regime.
        
        Returns:
            Dictionary with volatility metrics and regime classification
        """
        if len(self.price_history) < 10:
            return {'current': 0.2, 'historical': 0.2, 'regime': 'normal'}
            
        # Calculate log returns for volatility analysis
        returns = np.diff(np.log(self.price_history))
        
        # Current volatility (last 5 days, annualized)
        current_vol = np.std(returns[-5:]) * np.sqrt(252)
        
        # Historical volatility (all available data, annualized)
        historical_vol = np.std(returns) * np.sqrt(252)
        
        # Store volatility history for analysis
        self.volatility_history.append(current_vol)
        if len(self.volatility_history) > 50:
            self.volatility_history.pop(0)
        
        # Determine volatility regime
        if current_vol > historical_vol * 1.5:
            regime = 'high'  # Current vol > 150% of historical
        elif current_vol < historical_vol * 0.7:
            regime = 'low'   # Current vol < 70% of historical
        else:
            regime = 'normal'  # Current vol within normal range
            
        return {
            'current': current_vol,
            'historical': historical_vol,
            'regime': regime
        }
    
    def calculate_rsi(self):
        """
        Calculate Relative Strength Index (RSI) momentum indicator.
        
        RSI measures the speed and magnitude of price changes.
        Values above 70 indicate overbought conditions.
        Values below 30 indicate oversold conditions.
        
        Returns:
            RSI value (0-100)
        """
        if len(self.price_history) < self.rsi_period + 1:
            return 50  # Neutral RSI when insufficient data
            
        # Calculate price changes
        gains = []
        losses = []
        
        for i in range(1, len(self.price_history)):
            change = self.price_history[i] - self.price_history[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if len(gains) < self.rsi_period:
            return 50
            
        # Calculate average gains and losses
        avg_gain = np.mean(gains[-self.rsi_period:])
        avg_loss = np.mean(losses[-self.rsi_period:])
        
        if avg_loss == 0:
            return 100  # All gains, no losses
            
        # Calculate RSI: RSI = 100 - (100 / (1 + RS))
        # where RS = Average Gain / Average Loss
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def find_support_resistance(self):
        """
        Find support and resistance levels using recent price action.
        
        Support = recent low price level
        Resistance = recent high price level
        
        Returns:
            Dictionary with support/resistance levels and distances
        """
        if len(self.price_history) < 20:
            return {'support': 0, 'resistance': float('inf')}
            
        # Find recent high and low prices
        recent_high = max(self.price_history[-20:])
        recent_low = min(self.price_history[-20:])
        current_price = self.price_history[-1]
        
        # Calculate distance to support and resistance as percentages
        distance_to_resistance = (recent_high - current_price) / current_price
        distance_to_support = (current_price - recent_low) / current_price
        
        return {
            'support': recent_low,
            'resistance': recent_high,
            'distance_to_resistance': distance_to_resistance,
            'distance_to_support': distance_to_support
        }
    
    def determine_market_regime(self):
        """
        Determine overall market regime by combining trend and volatility.
        
        Market regimes help determine optimal trading parameters:
        - bullish_low_vol: Best for aggressive short puts
        - bearish_high_vol: Most conservative approach needed
        - overbought/oversold: Avoid trading in extreme conditions
        
        Returns:
            Market regime classification string
        """
        trend = self.analyze_trend()
        volatility = self.analyze_volatility()
        rsi = self.calculate_rsi()
        
        # Classify market regime based on trend and volatility
        if trend == 'bullish' and volatility['regime'] == 'low':
            return 'bullish_low_vol'  # Ideal conditions for short puts
        elif trend == 'bullish' and volatility['regime'] == 'high':
            return 'bullish_high_vol'  # Good trend but high risk
        elif trend == 'bearish' and volatility['regime'] == 'low':
            return 'bearish_low_vol'  # Poor trend but manageable risk
        elif trend == 'bearish' and volatility['regime'] == 'high':
            return 'bearish_high_vol'  # Worst conditions for short puts
        elif rsi > 70:
            return 'overbought'  # Market may be due for correction
        elif rsi < 30:
            return 'oversold'    # Market may be due for bounce
        else:
            return 'neutral'     # Normal market conditions
    
    def analyze_option_premiums(self, chain=None):
        """
        Analyze option premium richness using implied volatility.
        
        Determines if options are expensive (high IV) or cheap (low IV)
        relative to historical volatility.
        
        Args:
            chain: Option chain data (optional)
            
        Returns:
            Dictionary indicating premium richness
        """
        if not chain:
            return {'rich': False, 'cheap': False, 'fair': True}
            
        # Get put options from chain
        puts = [x for x in chain if x.Right == OptionRight.Put]
        if len(puts) < 3:
            return {'rich': False, 'cheap': False, 'fair': True}
            
        # Sort by strike price for analysis
        puts.sort(key=lambda x: x.Strike)
        
        # Extract implied volatilities
        ivs = []
        for put in puts:
            if hasattr(put, 'ImpliedVolatility') and put.ImpliedVolatility:
                ivs.append(put.ImpliedVolatility)
        
        if len(ivs) < 3:
            return {'rich': False, 'cheap': False, 'fair': True}
            
        # Calculate average implied volatility
        avg_iv = np.mean(ivs)
        
        # Compare to historical volatility
        volatility = self.analyze_volatility()
        
        # Classify premium richness
        if avg_iv > volatility['historical'] * 1.2:
            return {'rich': True, 'cheap': False, 'fair': False}  # Expensive options
        elif avg_iv < volatility['historical'] * 0.8:
            return {'cheap': True, 'rich': False, 'fair': False}  # Cheap options
        else:
            return {'fair': True, 'rich': False, 'cheap': False}  # Fairly priced
    
    def get_optimal_delta_range(self, market_analysis):
        """
        Get optimal delta range based on market conditions.
        
        Adjusts delta targets based on market regime:
        - More aggressive in bullish low volatility
        - More conservative in bearish high volatility
        
        Args:
            market_analysis: Complete market analysis results
            
        Returns:
            Tuple of (min_delta, max_delta)
        """
        regime = market_analysis['market_regime']
        volatility = market_analysis['volatility']['regime']
        
        # Adjust delta range based on market conditions
        if regime == 'bullish_low_vol':
            return (0.15, 0.35)  # More aggressive in ideal conditions
        elif regime == 'bearish_high_vol':
            return (0.10, 0.25)  # Most conservative in worst conditions
        elif volatility == 'high':
            return (0.10, 0.30)  # Conservative in high volatility
        elif volatility == 'low':
            return (0.20, 0.45)  # More aggressive in low volatility
        else:
            return (0.15, 0.40)  # Default range for normal conditions
    
    def get_optimal_dte_range(self, market_analysis):
        """
        Get optimal days to expiration range based on market conditions.
        
        Adjusts DTE targets based on market regime:
        - Longer DTE in bearish high volatility (more time for recovery)
        - Shorter DTE in low volatility (faster time decay)
        
        Args:
            market_analysis: Complete market analysis results
            
        Returns:
            Tuple of (min_dte, max_dte)
        """
        regime = market_analysis['market_regime']
        volatility = market_analysis['volatility']['regime']
        
        # Adjust DTE range based on market conditions
        if regime == 'bearish_high_vol':
            return (45, 90)  # Longer DTE to avoid assignment risk
        elif volatility == 'high':
            return (30, 60)  # Medium DTE in high volatility
        elif volatility == 'low':
            return (21, 45)  # Shorter DTE to capture time decay
        else:
            return (30, 60)  # Default range for normal conditions
    
    def should_avoid_trading(self, market_analysis):
        """
        Determine if we should avoid trading based on market conditions.
        
        Implements trading filters to avoid unfavorable conditions:
        - Extreme RSI levels (overbought/oversold)
        - Bearish high volatility (high risk)
        - Market extremes
        
        Args:
            market_analysis: Complete market analysis results
            
        Returns:
            True if trading should be avoided, False otherwise
        """
        regime = market_analysis['market_regime']
        rsi = market_analysis['rsi']
        volatility = market_analysis['volatility']['regime']
        
        # Avoid trading in extreme conditions
        if regime in ['overbought', 'oversold']:
            return True  # Market may reverse soon
        if volatility == 'high' and regime in ['bearish_high_vol']:
            return True  # Too risky for short puts
        if rsi > 80 or rsi < 20:
            return True  # Extreme momentum conditions
            
        return False  # Safe to trade
    
    def get_default_analysis(self):
        """
        Return default analysis when insufficient data is available.
        
        Provides safe default values when the strategy starts and
        doesn't have enough historical data for analysis.
        
        Returns:
            Dictionary with default market analysis values
        """
        return {
            'trend': 'neutral',
            'volatility': {'current': 0.2, 'historical': 0.2, 'regime': 'normal'},
            'rsi': 50,
            'support_resistance': {'support': 0, 'resistance': float('inf')},
            'market_regime': 'neutral',
            'option_premium_richness': {'rich': False, 'cheap': False, 'fair': True}
        } 