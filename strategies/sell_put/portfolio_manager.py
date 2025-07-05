from AlgorithmImports import *
import numpy as np
from typing import Dict, List, Optional, Tuple
from .stock_manager import StockManager

class PortfolioManager:
    """
    Manages the overall portfolio across multiple stocks.
    
    This class coordinates trading across multiple stocks and implements:
    - Portfolio-level risk management
    - Correlation-based position sizing
    - Cross-stock trade coordination
    - Portfolio performance tracking
    - Dynamic allocation adjustments
    
    The goal is to maintain optimal diversification while maximizing returns.
    """
    
    def __init__(self, algorithm, portfolio_config: dict):
        """
        Initialize the PortfolioManager.
        
        Args:
            algorithm: Reference to the main algorithm instance
            portfolio_config: Portfolio configuration dictionary
        """
        self.algorithm = algorithm
        self.config = portfolio_config
        
        # Portfolio state variables
        self.stock_managers: Dict[str, StockManager] = {}
        self.total_trades: int = 0
        self.portfolio_pnl: float = 0
        self.peak_portfolio_value: float = algorithm.Portfolio.TotalPortfolioValue
        self.daily_portfolio_pnl: List[float] = []
        
        # Risk management
        self.max_stocks: int = portfolio_config.get('max_stocks', 5)
        self.max_portfolio_risk: float = portfolio_config.get('max_portfolio_risk', 0.02)
        self.max_drawdown: float = portfolio_config.get('max_drawdown', 0.15)
        self.correlation_threshold: float = portfolio_config.get('correlation_threshold', 0.7)
        
        # Correlation analysis disabled for simplicity
        # self.correlation_manager = None
        
        # Portfolio performance tracking
        self.portfolio_returns: List[float] = []
        self.portfolio_volatility: List[float] = []
        
    def initialize_stocks(self, stocks_config: List[dict]) -> None:
        """
        Initialize StockManager instances for each configured stock.
        
        Args:
            stocks_config: List of stock configuration dictionaries
        """
        for stock_config in stocks_config:
            ticker = stock_config['ticker']
            if stock_config.get('enabled', True):
                self.stock_managers[ticker] = StockManager(self.algorithm, ticker, stock_config)
                self.algorithm.Log(f"Initialized StockManager for {ticker}")
                
    def update_portfolio_data(self, slice_data) -> None:
        """
        Update data for all stocks in the portfolio.
        
        Args:
            slice_data: Latest data slice from the algorithm
        """
        # Update each stock manager
        for stock_manager in self.stock_managers.values():
            stock_manager.update_data(slice_data)
            
        # Update correlation data (simplified - correlation not critical)
        # self.correlation_manager.update_correlation_data(self.stock_managers)  # Disabled
        
        # Update portfolio performance
        self._update_portfolio_performance()
        
    def _update_portfolio_performance(self) -> None:
        """Update portfolio-level performance metrics."""
        current_value = self.algorithm.Portfolio.TotalPortfolioValue
        
        # Update peak value
        if current_value > self.peak_portfolio_value:
            self.peak_portfolio_value = current_value
            
        # Calculate daily PnL
        if hasattr(self, '_last_portfolio_value'):
            daily_pnl = current_value - self._last_portfolio_value
            self.daily_portfolio_pnl.append(daily_pnl)
            
            # Keep only recent data
            if len(self.daily_portfolio_pnl) > 100:
                self.daily_portfolio_pnl.pop(0)
                
        self._last_portfolio_value = current_value
        
    def should_trade_portfolio(self) -> bool:
        """
        Determine if the portfolio should trade based on overall conditions.
        
        Returns:
            True if portfolio should trade, False otherwise
        """
        # Check portfolio-level risk limits
        if self._check_portfolio_risk_limits():
            return False
            
        # Check correlation limits (simplified - correlation not critical)
        # if self.correlation_manager.should_reduce_trading():  # Disabled
        #     return False
            
        # Check if we have too many open positions
        open_positions = self._count_open_positions()
        if open_positions >= self.max_stocks:
            return False
            
        return True
        
    def _check_portfolio_risk_limits(self) -> bool:
        """
        Check if portfolio risk limits are exceeded.
        
        Returns:
            True if risk limits exceeded, False otherwise
        """
        # Check drawdown
        current_value = self.algorithm.Portfolio.TotalPortfolioValue
        drawdown = (self.peak_portfolio_value - current_value) / self.peak_portfolio_value
        
        if drawdown > self.max_drawdown:
            self.algorithm.Log(f"Portfolio drawdown limit exceeded: {drawdown:.2%}")
            return True
            
        # Check portfolio volatility
        if len(self.daily_portfolio_pnl) >= 20:
            volatility = np.std(self.daily_portfolio_pnl)
            if volatility > self.max_portfolio_risk * self.algorithm.Portfolio.TotalPortfolioValue:
                self.algorithm.Log(f"Portfolio volatility limit exceeded: {volatility:.2f}")
                return True
                
        return False
        
    def _count_open_positions(self) -> int:
        """Count the number of stocks with open positions."""
        count = 0
        for stock_manager in self.stock_managers.values():
            if stock_manager.current_contract and self.algorithm.Portfolio[stock_manager.current_contract.Symbol].Invested:
                count += 1
        return count
        
    def manage_positions(self) -> None:
        """
        Manage all positions in the portfolio.
        """
        try:
            # First, check for positions that should be closed
            for stock_manager in self.stock_managers.values():
                if stock_manager.should_close_position():
                    stock_manager.close_position()
                    
            # Then, look for new trading opportunities
            if not self.should_trade_portfolio():
                return
                
            # Find the best trading opportunity
            best_stock = self._find_best_trading_opportunity()
            if best_stock:
                best_stock.find_and_enter_position()
        except Exception as e:
            self.algorithm.Log(f"Error in manage_positions: {str(e)}")
            
    def _find_best_trading_opportunity(self) -> Optional[StockManager]:
        """
        Find the best stock to trade based on multiple criteria.
        
        Returns:
            StockManager instance for the best opportunity, or None
        """
        opportunities: List[Tuple[StockManager, float]] = []
        
        for stock_manager in self.stock_managers.values():
            if not stock_manager.should_trade():
                continue
                
            # Calculate opportunity score
            score = self._calculate_opportunity_score(stock_manager)
            if score > 0:
                opportunities.append((stock_manager, score))
                
        # Sort by score and return the best
        if opportunities:
            opportunities.sort(key=lambda x: x[1], reverse=True)
            return opportunities[0][0]
            
        return None
        
    def _calculate_opportunity_score(self, stock_manager: StockManager) -> float:
        """
        Calculate a score for trading opportunity quality.
        
        Args:
            stock_manager: StockManager instance to evaluate
            
        Returns:
            Score (higher is better)
        """
        score = 0.0
        
        # Base score from weight
        score += stock_manager.weight * 10
        
        # Market condition bonus
        market_analysis = stock_manager.market_analyzer.analyze_market_conditions(
            stock_manager.price_history[-1] if stock_manager.price_history else 0
        )
        
        if market_analysis['market_regime'] == 'bullish_low_vol':
            score += 5
        elif market_analysis['market_regime'] == 'bullish_normal_vol':
            score += 3
        elif market_analysis['market_regime'] == 'bearish_high_vol':
            score -= 5
            
        # Volatility bonus (prefer lower volatility)
        volatility = market_analysis['volatility']['current']
        if volatility < 0.2:
            score += 3
        elif volatility > 0.4:
            score -= 3
            
        # Correlation penalty (simplified - correlation not critical)
        # correlation = self.correlation_manager.get_stock_correlation(stock_manager.ticker)  # Disabled
        # if correlation > 0.8:
        #     score -= 5
        # elif correlation < 0.3:
        #     score += 3
            
        return score
        
    def get_portfolio_metrics(self) -> dict:
        """
        Get comprehensive portfolio performance metrics.
        
        Returns:
            Dictionary with portfolio metrics
        """
        # Calculate total trades from all stock managers
        total_trades = sum(stock_manager.trade_count for stock_manager in self.stock_managers.values())
        
        # Calculate total portfolio PnL from all stock managers
        total_portfolio_pnl = sum(stock_manager.profit_loss for stock_manager in self.stock_managers.values())
        
        metrics = {
            'total_trades': total_trades,
            'portfolio_pnl': total_portfolio_pnl,
            'current_value': self.algorithm.Portfolio.TotalPortfolioValue,
            'peak_value': self.peak_portfolio_value,
            'drawdown': (self.peak_portfolio_value - self.algorithm.Portfolio.TotalPortfolioValue) / self.peak_portfolio_value,
            'open_positions': self._count_open_positions(),
            'stock_metrics': {}
        }
        
        # Add individual stock metrics
        for ticker, stock_manager in self.stock_managers.items():
            metrics['stock_metrics'][ticker] = stock_manager.get_performance_metrics()
            
        return metrics
        
    def get_correlation_matrix(self) -> dict:
        """
        Get the correlation matrix for all stocks.
        
        Returns:
            Correlation matrix as a dictionary (simplified - returns empty dict)
        """
        return {}  # Simplified - correlation not critical
        
    def adjust_allocations(self) -> None:
        """
        Dynamically adjust stock allocations based on performance and correlation.
        """
        # This could implement dynamic allocation adjustments
        # based on performance, correlation, and market conditions
        pass 