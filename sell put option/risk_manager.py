from AlgorithmImports import *
import numpy as np

class RiskManager:
    """
    Comprehensive risk management for the short put strategy.
    
    This module implements advanced risk controls including:
    - Kelly Criterion position sizing
    - Dynamic volatility adjustments
    - Portfolio risk limits
    - Drawdown protection
    - Consecutive loss monitoring
    
    The goal is to maximize returns while keeping risk within acceptable bounds.
    """
    
    def __init__(self, algorithm):
        """
        Initialize the RiskManager with risk parameters.
        
        Args:
            algorithm: Reference to the main algorithm instance
            
        Risk Parameters:
            max_portfolio_risk: Maximum 2% portfolio risk per trade
            max_drawdown: Maximum 15% portfolio drawdown before stopping
            volatility_lookback: Number of days for volatility calculation
            volatility_threshold: Threshold for high volatility detection
        """
        self.algorithm = algorithm
        
        # Risk control parameters - these can be adjusted based on risk tolerance
        self.max_portfolio_risk = 0.02      # 2% max portfolio risk per trade
        self.max_drawdown = 0.15            # 15% max drawdown before stopping
        self.volatility_lookback = 20       # Days for volatility calculation
        self.volatility_threshold = 0.4     # High volatility threshold
        
    def calculate_position_size(self, contract, underlying_price):
        """
        Calculate optimal position size using multiple risk factors.
        
        This method combines several approaches:
        1. Kelly Criterion for optimal position sizing
        2. Volatility adjustment based on market conditions
        3. Portfolio risk-based sizing
        4. Margin-based sizing
        
        Args:
            contract: Option contract to trade
            underlying_price: Current underlying price
            
        Returns:
            Optimal number of contracts to trade (minimum 1)
        """
        # Step 1: Calculate Kelly Criterion for optimal position sizing
        win_rate = self.get_historical_win_rate()
        avg_win = self.get_average_win()
        avg_loss = self.get_average_loss()
        
        # Fallback to conservative sizing if no historical data
        if avg_loss == 0:
            return self.calculate_conservative_position_size(contract)
            
        # Kelly formula: f = (bp - q) / b
        # where b = odds received, p = probability of win, q = probability of loss
        kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        
        # Cap Kelly fraction between 10-50% to avoid over-leveraging
        kelly_fraction = max(0.1, min(0.5, kelly_fraction))
        
        # Step 2: Adjust for current market volatility
        volatility_factor = self.get_volatility_adjustment()
        
        # Step 3: Calculate position size based on portfolio risk limits
        portfolio_risk_size = self.calculate_portfolio_risk_size(contract, underlying_price)
        
        # Step 4: Calculate position size based on available margin
        margin_size = self.calculate_margin_based_size(contract)
        
        # Step 5: Combine all sizing methods - take the most conservative approach
        optimal_size = min(portfolio_risk_size, margin_size, 
                          int(portfolio_risk_size * kelly_fraction * volatility_factor))
        
        # Ensure minimum position size of 1 contract
        return max(1, optimal_size)
    
    def calculate_portfolio_risk_size(self, contract, underlying_price):
        """
        Calculate position size based on maximum portfolio risk per trade.
        
        This method ensures that no single trade can lose more than a specified
        percentage of the total portfolio value.
        
        Args:
            contract: Option contract to trade
            underlying_price: Current underlying price
            
        Returns:
            Maximum number of contracts based on portfolio risk limits
        """
        portfolio_value = self.algorithm.Portfolio.TotalPortfolioValue
        max_risk_amount = portfolio_value * self.max_portfolio_risk
        
        # Calculate potential loss at different underlying price levels
        potential_loss = self.calculate_max_loss(contract, underlying_price)
        
        if potential_loss <= 0:
            return 1  # Minimum position size
            
        # Number of contracts = max risk amount / potential loss per contract
        return int(max_risk_amount / potential_loss)
    
    def calculate_max_loss(self, contract, underlying_price):
        """
        Calculate maximum potential loss for a short put position.
        
        For short puts, the maximum loss occurs if the underlying goes to zero.
        However, we use a more realistic scenario (50% drop) for risk calculation.
        
        Args:
            contract: Option contract
            underlying_price: Current underlying price
            
        Returns:
            Maximum potential loss per contract
        """
        # Use a realistic worst-case scenario: 50% drop in underlying price
        # This is more conservative than assuming the stock goes to zero
        worst_case_price = underlying_price * 0.5
        
        # Calculate intrinsic value at worst-case price
        intrinsic_value = max(0, contract.Strike - worst_case_price)
        
        # Loss per contract = intrinsic value * 100 (contract multiplier)
        return intrinsic_value * 100
    
    def calculate_margin_based_size(self, contract):
        """
        Calculate position size based on available margin.
        
        This ensures we don't exceed margin requirements and get margin called.
        
        Args:
            contract: Option contract to trade
            
        Returns:
            Maximum number of contracts based on available margin
        """
        available_margin = self.algorithm.Portfolio.MarginRemaining
        
        # Margin requirement for short puts is typically 20% of strike price
        margin_requirement = contract.Strike * 100 * 0.2
        
        return int(available_margin / margin_requirement)
    
    def calculate_conservative_position_size(self, contract):
        """
        Fallback conservative position sizing when historical data is insufficient.
        
        This method uses the original position sizing logic as a safety net.
        
        Args:
            contract: Option contract to trade
            
        Returns:
            Conservative number of contracts to trade
        """
        portfolio_value = self.algorithm.Portfolio.TotalPortfolioValue
        max_position_value = portfolio_value * self.algorithm.max_position_size
        
        # Calculate margin requirement
        margin_requirement = contract.Strike * 100 * 0.2
        
        # Conservative position size
        return max(1, int(max_position_value / margin_requirement))
    
    def get_volatility_adjustment(self):
        """
        Adjust position size based on market volatility.
        
        Higher volatility = smaller position sizes
        Lower volatility = larger position sizes
        
        Returns:
            Volatility adjustment factor (0.7 to 1.2)
        """
        if len(self.algorithm.daily_pnl) < self.volatility_lookback:
            return 1.0  # Default factor when insufficient data
            
        # Calculate volatility from recent PnL data
        recent_pnl = self.algorithm.daily_pnl[-self.volatility_lookback:]
        volatility = np.std(recent_pnl)
        
        # Adjust position size based on volatility regime
        if volatility > self.volatility_threshold:
            return 0.7  # Reduce position size in high volatility
        elif volatility < 0.1:
            return 1.2  # Increase position size in low volatility
        else:
            return 1.0  # Normal position size in moderate volatility
    
    def get_historical_win_rate(self):
        """
        Calculate historical win rate from completed trades.
        
        This is used for Kelly Criterion calculations.
        
        Returns:
            Win rate as a decimal (0.0 to 1.0)
        """
        completed_trades = [t for t in self.algorithm.trades if 'pnl' in t]
        if not completed_trades:
            return 0.6  # Default assumption for new strategies
            
        winning_trades = [t for t in completed_trades if t['pnl'] > 0]
        return len(winning_trades) / len(completed_trades)
    
    def get_average_win(self):
        """
        Calculate average winning trade amount.
        
        Returns:
            Average dollar amount of winning trades
        """
        completed_trades = [t for t in self.algorithm.trades if 'pnl' in t and t['pnl'] > 0]
        if not completed_trades:
            return 100  # Default assumption
        return np.mean([t['pnl'] for t in completed_trades])
    
    def get_average_loss(self):
        """
        Calculate average losing trade amount.
        
        Returns:
            Average dollar amount of losing trades (absolute value)
        """
        completed_trades = [t for t in self.algorithm.trades if 'pnl' in t and t['pnl'] < 0]
        if not completed_trades:
            return 200  # Default assumption
        return abs(np.mean([t['pnl'] for t in completed_trades]))
    
    def should_stop_trading(self):
        """
        Check if we should stop trading due to risk limits.
        
        This implements circuit breakers to protect the portfolio:
        1. Maximum drawdown limit
        2. Consecutive loss limit
        
        Returns:
            True if trading should be stopped, False otherwise
        """
        # Check 1: Maximum drawdown limit
        current_value = self.algorithm.Portfolio.TotalPortfolioValue
        if current_value < self.algorithm.peak_portfolio_value * (1 - self.max_drawdown):
            return True
            
        # Check 2: Consecutive losses limit
        recent_trades = [t for t in self.algorithm.trades[-5:] if 'pnl' in t]
        if len(recent_trades) >= 3:
            consecutive_losses = sum(1 for t in recent_trades if t['pnl'] < 0)
            if consecutive_losses >= 3:
                return True  # Stop after 3 consecutive losses
                
        return False
    
    def get_risk_metrics(self):
        """
        Get current risk metrics for monitoring and plotting.
        
        This provides real-time risk data for the strategy dashboard.
        
        Returns:
            Dictionary containing current risk metrics
        """
        return {
            'portfolio_value': self.algorithm.Portfolio.TotalPortfolioValue,
            'margin_used': self.algorithm.Portfolio.TotalMarginUsed,
            'margin_remaining': self.algorithm.Portfolio.MarginRemaining,
            'win_rate': self.get_historical_win_rate(),
            'avg_win': self.get_average_win(),
            'avg_loss': self.get_average_loss(),
            'volatility': self.get_volatility_adjustment()
        } 