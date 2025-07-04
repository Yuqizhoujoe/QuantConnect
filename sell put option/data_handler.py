
from AlgorithmImports import *

class DataHandler:
    """
    Enhanced data handler with efficient plotting and risk monitoring.
    This includes handling incoming data slices and providing data-related utilities
    while respecting QuantConnect's charting limits.
    """
    def __init__(self, algorithm):
        """
        Initializes the DataHandler with plotting controls.
        
        Args:
            algorithm: A reference to the main algorithm instance.
        """
        self.algorithm = algorithm
        self.latest_slice = None  # Stores the most recent data slice
        
        # Plotting controls to respect QuantConnect limits (4000 points max)
        self.plot_counter = 0
        
        # Get plotting configuration from algorithm or use defaults
        try:
            self.plotting_enabled = getattr(algorithm, 'plotting_enabled', True)
            self.plot_frequency = getattr(algorithm, 'plot_frequency', 50)
            self.max_plot_points = getattr(algorithm, 'max_plot_points', 3500)
            self.plot_risk_metrics = getattr(algorithm, 'plot_risk_metrics', True)
            self.plot_pnl = getattr(algorithm, 'plot_pnl', True)
        except:
            # Fallback to defaults if configuration not available
            self.plotting_enabled = True
            self.plot_frequency = 50
            self.max_plot_points = 3500
            self.plot_risk_metrics = True
            self.plot_pnl = True

    def on_data(self, slice: Slice):
        """
        Enhanced data handling with efficient plotting and risk monitoring.
        
        This method implements smart plotting to respect QuantConnect's charting limits
        while still providing useful visualizations for monitoring.
        
        Args:
            slice: The new data slice from the engine.
        """
        self.latest_slice = slice
        
        # Update peak portfolio value for drawdown calculation
        current_value = self.algorithm.Portfolio.TotalPortfolioValue
        if current_value > self.algorithm.peak_portfolio_value:
            self.algorithm.peak_portfolio_value = current_value
        
        # Increment plot counter
        self.plot_counter += 1
        
        # Calculate and store daily PnL
        if self.algorithm.current_contract:
            position = self.algorithm.Portfolio[self.algorithm.current_contract.Symbol]
            if position.Invested:
                daily_pnl = position.UnrealizedProfit
                self.algorithm.daily_pnl.append(daily_pnl)
                
                # Keep only recent PnL data for analysis (limit to 100 points)
                if len(self.algorithm.daily_pnl) > 100:
                    self.algorithm.daily_pnl.pop(0)
                
                # Smart plotting: only plot periodically to respect limits
                if self.should_plot("pnl"):
                    # Plot the unrealized profit and loss
                    self.plot_with_limit_check("Daily PnL", "Unrealized PnL", daily_pnl)
                    
                    # Plot drawdown (only when significant or periodic)
                    drawdown = (self.algorithm.peak_portfolio_value - current_value) / self.algorithm.peak_portfolio_value
                    if abs(drawdown) > 0.01 or self.plot_counter % (self.plot_frequency * 5) == 0:  # Plot significant drawdowns or every 5 cycles
                        self.plot_with_limit_check("Risk Metrics", "Drawdown", drawdown)
                    
                    # Plot risk metrics (less frequently to save data points)
                    if self.should_plot("risk"):
                        try:
                            risk_metrics = self.algorithm.risk_manager.get_risk_metrics()
                            self.plot_with_limit_check("Risk Metrics", "Win Rate", risk_metrics['win_rate'])
                            self.plot_with_limit_check("Risk Metrics", "Volatility Factor", risk_metrics['volatility'])
                        except Exception as e:
                            # Silently handle risk metrics errors to avoid log spam
                            pass

    def get_option_delta(self, contract):
        """
        Safely retrieves the delta of a given option contract.
        Delta is a measure of the option's price sensitivity to changes in the
        underlying asset's price.
        
        Args:
            contract: The option contract to get the delta for.
            
        Returns:
            The delta of the contract, or 0 if it's not available.
        """
        try:
            # Check if Greeks and Delta are available and not None
            return contract.Greeks.Delta if contract.Greeks and contract.Greeks.Delta is not None else 0
        except:
            # Return 0 in case of any error (e.g., Greeks not calculated yet)
            return 0
    
    def should_plot(self, plot_type="general"):
        """
        Determines if we should plot based on type and frequency.
        
        This method helps manage plotting frequency to stay within QuantConnect limits.
        
        Args:
            plot_type: Type of plot ("general", "risk", "pnl")
            
        Returns:
            True if we should plot, False otherwise
        """
        # Check if plotting is enabled
        if not self.plotting_enabled:
            return False
            
        if plot_type == "risk":
            # Risk metrics plot less frequently and only if enabled
            return (self.plot_risk_metrics and 
                   self.plot_counter % (self.plot_frequency * 3) == 0)
        elif plot_type == "pnl":
            # PnL plots more frequently but still controlled and only if enabled
            return (self.plot_pnl and 
                   self.plot_counter % self.plot_frequency == 0)
        else:
            # General plots
            return self.plot_counter % self.plot_frequency == 0
    
    def plot_with_limit_check(self, chart_name, series_name, value):
        """
        Plots data with built-in limit checking.
        
        This method provides a safe way to plot data while respecting
        QuantConnect's charting limits.
        
        Args:
            chart_name: Name of the chart
            series_name: Name of the series
            value: Value to plot
        """
        try:
            # Only plot if we're within reasonable limits and plotting is enabled
            if (self.plotting_enabled and 
                self.plot_counter < self.max_plot_points):
                self.algorithm.Plot(chart_name, series_name, value)
        except Exception as e:
            # Silently handle plotting errors to avoid log spam
            pass
