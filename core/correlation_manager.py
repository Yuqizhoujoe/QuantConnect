from AlgorithmImports import *
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import date

class CorrelationManager:
    """
    Manages correlation analysis between stocks for portfolio risk management.
    
    This module calculates and tracks correlations between stocks to:
    - Avoid over-concentration in correlated positions
    - Optimize portfolio diversification
    - Provide correlation-based position sizing adjustments
    - Monitor portfolio risk from correlation clustering
    
    The goal is to maintain optimal diversification while maximizing returns.
    """
    
    def __init__(self, algorithm: Any, correlation_threshold: float = 0.7) -> None:
        """
        Initialize the CorrelationManager.
        
        Args:
            algorithm: Reference to the main algorithm instance
            correlation_threshold: Threshold above which stocks are considered highly correlated
        """
        self.algorithm: Any = algorithm
        self.correlation_threshold: float = correlation_threshold
        
        # Data storage for correlation analysis
        self.returns_data: Dict[str, List[float]] = {}  # Dictionary of returns for each stock
        self.correlation_matrix: Dict[str, Dict[str, float]] = {}  # Cached correlation matrix
        self.last_update: Optional[date] = None
        
        # Correlation analysis parameters
        self.lookback_period: int = 60  # Days for correlation calculation
        self.update_frequency: int = 5  # Update correlation matrix every N days
        
    def update_correlation_data(self, stock_managers: Dict[str, Any]) -> None:
        """
        Update correlation data from all stock managers.
        
        Args:
            stock_managers: Dictionary of StockManager instances
        """
        # Check if we need to update (not every day)
        if (self.last_update and 
            (self.algorithm.Time.date() - self.last_update).days < self.update_frequency):
            return
            
        # Collect returns data from all stocks
        for ticker, stock_manager in stock_managers.items():
            if stock_manager.price_history and len(stock_manager.price_history) > 1:
                # Calculate returns from price history
                prices: List[float] = stock_manager.price_history
                returns: List[float] = []
                for i in range(1, len(prices)):
                    returns.append((prices[i] - prices[i-1]) / prices[i-1])
                    
                # Store returns data
                self.returns_data[ticker] = returns[-self.lookback_period:]
                
        # Update correlation matrix
        self._calculate_correlation_matrix()
        self.last_update = self.algorithm.Time.date()
        
    def _calculate_correlation_matrix(self) -> None:
        """
        Calculate correlation matrix for all stocks.
        """
        if len(self.returns_data) < 2:
            return
            
        # Create DataFrame for correlation calculation
        df: pd.DataFrame = pd.DataFrame(self.returns_data)
        
        # Calculate correlation matrix
        corr_matrix: pd.DataFrame = df.corr()
        
        # Store as dictionary for easier access
        self.correlation_matrix = corr_matrix.to_dict()
        
        # Log high correlations
        self._log_high_correlations()
        
    def _log_high_correlations(self) -> None:
        """Log stocks with high correlations for monitoring."""
        high_correlations: List[Tuple[str, str, float]] = []
        
        for ticker1 in self.correlation_matrix:
            for ticker2 in self.correlation_matrix[ticker1]:
                if ticker1 != ticker2:
                    corr: float = self.correlation_matrix[ticker1][ticker2]
                    if abs(corr) > self.correlation_threshold:
                        high_correlations.append((ticker1, ticker2, corr))
                        
        if high_correlations:
            self.algorithm.Log(f"High correlations detected: {high_correlations}")
            
    def get_stock_correlation(self, ticker: str) -> float:
        """
        Get the average correlation of a stock with all other stocks.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Average correlation value (0-1)
        """
        if ticker not in self.correlation_matrix:
            return 0.5  # Default moderate correlation
            
        correlations: List[float] = []
        for other_ticker, corr_dict in self.correlation_matrix.items():
            if other_ticker != ticker and ticker in corr_dict:
                correlations.append(abs(corr_dict[ticker]))
                
        return np.mean(correlations) if correlations else 0.5
        
    def get_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Get the full correlation matrix.
        
        Returns:
            Dictionary representation of correlation matrix
        """
        return self.correlation_matrix
        
    def should_reduce_trading(self) -> bool:
        """
        Determine if trading should be reduced due to high correlations.
        
        Returns:
            True if trading should be reduced, False otherwise
        """
        if not self.correlation_matrix:
            return False
            
        # Count high correlations
        high_corr_count: int = 0
        total_correlations: int = 0
        
        for ticker1 in self.correlation_matrix:
            for ticker2 in self.correlation_matrix[ticker1]:
                if ticker1 != ticker2:
                    total_correlations += 1
                    if abs(self.correlation_matrix[ticker1][ticker2]) > self.correlation_threshold:
                        high_corr_count += 1
                        
        # If more than 30% of correlations are high, reduce trading
        if total_correlations > 0:
            high_corr_ratio: float = high_corr_count / total_correlations
            if high_corr_ratio > 0.3:
                self.algorithm.Log(f"Reducing trading due to high correlations: {high_corr_ratio:.2%}")
                return True
                
        return False
        
    def get_diversification_score(self) -> float:
        """
        Calculate a diversification score for the portfolio.
        
        Returns:
            Score between 0-1 (higher is better diversification)
        """
        if not self.correlation_matrix:
            return 0.5  # Default moderate diversification
            
        # Calculate average correlation
        correlations: List[float] = []
        for ticker1 in self.correlation_matrix:
            for ticker2 in self.correlation_matrix[ticker1]:
                if ticker1 != ticker2:
                    correlations.append(abs(self.correlation_matrix[ticker1][ticker2]))
                    
        if not correlations:
            return 0.5
            
        avg_correlation: float = np.mean(correlations)
        
        # Convert to diversification score (lower correlation = higher diversification)
        diversification_score: float = 1 - avg_correlation
        
        return diversification_score
        
    def get_optimal_position_size_adjustment(self, ticker: str) -> float:
        """
        Get position size adjustment based on correlation.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Adjustment factor (0.5-1.5)
        """
        correlation: float = self.get_stock_correlation(ticker)
        
        # Higher correlation = smaller position size
        if correlation > 0.8:
            return 0.5  # Reduce position size by 50%
        elif correlation > 0.6:
            return 0.7  # Reduce position size by 30%
        elif correlation < 0.3:
            return 1.2  # Increase position size by 20%
        else:
            return 1.0  # No adjustment
            
    def get_correlation_clusters(self) -> List[List[str]]:
        """
        Identify clusters of highly correlated stocks.
        
        Returns:
            List of stock clusters (lists of tickers)
        """
        if not self.correlation_matrix:
            return []
            
        clusters: List[List[str]] = []
        used_stocks: set[str] = set()
        
        for ticker1 in self.correlation_matrix:
            if ticker1 in used_stocks:
                continue
                
            cluster: List[str] = [ticker1]
            used_stocks.add(ticker1)
            
            for ticker2 in self.correlation_matrix[ticker1]:
                if (ticker2 not in used_stocks and 
                    abs(self.correlation_matrix[ticker1][ticker2]) > self.correlation_threshold):
                    cluster.append(ticker2)
                    used_stocks.add(ticker2)
                    
            if len(cluster) > 1:
                clusters.append(cluster)
                
        return clusters
        
    def get_portfolio_risk_adjustment(self) -> float:
        """
        Get overall portfolio risk adjustment based on correlations.
        
        Returns:
            Risk adjustment factor (0.5-1.5)
        """
        diversification_score: float = self.get_diversification_score()
        
        # Lower diversification = higher risk adjustment
        if diversification_score < 0.3:
            return 0.5  # Reduce overall risk by 50%
        elif diversification_score < 0.5:
            return 0.7  # Reduce overall risk by 30%
        elif diversification_score > 0.8:
            return 1.2  # Increase overall risk by 20%
        else:
            return 1.0  # No adjustment 