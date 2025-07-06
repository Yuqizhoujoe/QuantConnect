
import json
from typing import Dict, Any, Optional, List

class StrategyConfig:
    """
    Multi-stock configuration class for easy parameter modification.
    Modify these values to change strategy behavior.
    """
    # Portfolio settings
    TOTAL_CASH: int = 100000
    MAX_STOCKS: int = 5
    MAX_PORTFOLIO_RISK: float = 0.02
    MAX_DRAWDOWN: float = 0.15
    CORRELATION_THRESHOLD: float = 0.7
    
    # Stock configurations
    STOCKS = [
        {
            "ticker": "AVGO",
            "weight": 0.5,
            "target_delta_min": 0.25,
            "target_delta_max": 0.75,
            "max_position_size": 0.20,
            "option_frequency": "monthly",
            "enabled": True
        },
        {
            "ticker": "AAPL",
            "weight": 0.5,
            "target_delta_min": 0.25,
            "target_delta_max": 0.75,
            "max_position_size": 0.20,
            "option_frequency": "monthly",
            "enabled": True
        }
    ]
    
    # Risk management settings
    VOLATILITY_LOOKBACK: int = 20
    VOLATILITY_THRESHOLD: float = 0.4
    CORRELATION_LOOKBACK: int = 60
    
    # Market analysis settings
    RSI_PERIOD: int = 14
    MOVING_AVERAGE_PERIOD: int = 50
    MARKET_VOLATILITY_LOOKBACK: int = 20
    
    # Legacy single-stock settings (for backward compatibility)
    TICKER: str = "AVGO"
    TARGET_DELTA_MIN: float = 0.25
    TARGET_DELTA_MAX: float = 0.75
    MAX_POSITION_SIZE: float = 0.20
    OPTION_FREQUENCY: str = "monthly"
    START_DATE: str = "2020-01-01"
    END_DATE: str = "2025-01-01"
    CASH: int = TOTAL_CASH

class ConfigLoader:
    """
    Handles loading and applying configuration settings.
    This class separates the strategy's parameters from its core logic, allowing
    for easy tuning without modifying the Python code.
    """
    def __init__(self, algorithm: Any) -> None:
        """
        Initializes the ConfigLoader.
        
        Args:
            algorithm: A reference to the main algorithm instance. This allows the
                       loader to set attributes on the algorithm object.
        """
        self.algorithm: Any = algorithm

    def load_config(self, config_file: str = 'config.json') -> None:
        """
        Loads configuration from embedded settings or tries to load from file.
        Falls back to embedded configuration if file loading fails.
        
        Args:
            config_file: The path to the JSON configuration file (optional).
        """
        # Embedded configuration using StrategyConfig class
        embedded_config: Dict[str, Dict[str, Any]] = {
            "parameters": {
                "portfolio": {
                    "total_cash": StrategyConfig.TOTAL_CASH,
                    "max_stocks": StrategyConfig.MAX_STOCKS,
                    "max_portfolio_risk": StrategyConfig.MAX_PORTFOLIO_RISK,
                    "max_drawdown": StrategyConfig.MAX_DRAWDOWN,
                    "correlation_threshold": StrategyConfig.CORRELATION_THRESHOLD
                },
                "stocks": StrategyConfig.STOCKS,
                "risk_management": {
                    "max_portfolio_risk": StrategyConfig.MAX_PORTFOLIO_RISK,
                    "max_drawdown": StrategyConfig.MAX_DRAWDOWN,
                    "volatility_lookback": StrategyConfig.VOLATILITY_LOOKBACK,
                    "volatility_threshold": StrategyConfig.VOLATILITY_THRESHOLD,
                    "correlation_lookback": StrategyConfig.CORRELATION_LOOKBACK
                },
                "market_analysis": {
                    "rsi_period": StrategyConfig.RSI_PERIOD,
                    "moving_average_period": StrategyConfig.MOVING_AVERAGE_PERIOD,
                    "volatility_lookback": StrategyConfig.MARKET_VOLATILITY_LOOKBACK
                }
            }
        }
        
        # Try to load from file first
        try:
            with open(config_file, 'r') as f:
                config: Dict[str, Any] = json.load(f)
                self.algorithm.Log(f"Successfully loaded configuration from {config_file}")
        except FileNotFoundError:
            # Try with config directory path
            try:
                import os
                config_dir_path: str = os.path.join('config', config_file)
                with open(config_dir_path, 'r') as f:
                    config = json.load(f)
                self.algorithm.Log(f"Successfully loaded configuration from config directory: {config_dir_path}")
            except FileNotFoundError:
                # Try with absolute path from current file location
                try:
                    current_dir: str = os.path.dirname(os.path.abspath(__file__))
                    absolute_config_path: str = os.path.join(current_dir, config_file)
                    with open(absolute_config_path, 'r') as f:
                        config = json.load(f)
                    self.algorithm.Log(f"Successfully loaded configuration from absolute path: {absolute_config_path}")
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    self.algorithm.Log(f"Could not load config file: {e}. Using embedded configuration.")
                    config = embedded_config
            except json.JSONDecodeError as e:
                self.algorithm.Log(f"JSON parsing error in config file: {e}. Using embedded configuration.")
                config = embedded_config
        except json.JSONDecodeError as e:
            self.algorithm.Log(f"JSON parsing error in config file: {e}. Using embedded configuration.")
            config = embedded_config
        
        # Get the nested 'parameters' dictionary from the config file.
        parameters: Dict[str, Any] = config.get('parameters', {})
        
        # Store the entire parameters dictionary for access by the strategy
        self.algorithm.parameters = parameters
        
        # --- Apply each parameter to the algorithm ---
        # For each parameter, we use .get() to provide a default value in case
        # the parameter is not defined in the JSON file.
        
        # Handle multi-stock configuration
        stocks_config = parameters.get('stocks', [])
        if stocks_config:
            # Use first stock as default for backward compatibility
            first_stock = stocks_config[0]
            self.algorithm.ticker = first_stock.get('ticker', StrategyConfig.TICKER)
            self.algorithm.target_delta_min = first_stock.get('target_delta_min', StrategyConfig.TARGET_DELTA_MIN)
            self.algorithm.target_delta_max = first_stock.get('target_delta_max', StrategyConfig.TARGET_DELTA_MAX)
            self.algorithm.max_position_size = first_stock.get('max_position_size', StrategyConfig.MAX_POSITION_SIZE)
            self.algorithm.option_frequency = first_stock.get('option_frequency', StrategyConfig.OPTION_FREQUENCY)
        else:
            # Fallback to single-stock configuration
            self.algorithm.ticker = parameters.get('ticker', StrategyConfig.TICKER)
            self.algorithm.target_delta_min = parameters.get('target_delta_min', StrategyConfig.TARGET_DELTA_MIN)
            self.algorithm.target_delta_max = parameters.get('target_delta_max', StrategyConfig.TARGET_DELTA_MAX)
            self.algorithm.max_position_size = parameters.get('max_position_size', StrategyConfig.MAX_POSITION_SIZE)
            self.algorithm.option_frequency = parameters.get('option_frequency', StrategyConfig.OPTION_FREQUENCY)
        
        # Set the initial cash for the backtest.
        portfolio_config = parameters.get('portfolio', {})
        self.algorithm.SetCash(portfolio_config.get('total_cash', StrategyConfig.CASH))
        
        # Load risk management configuration
        risk_config: Dict[str, Any] = parameters.get('risk_management', {})
        self.algorithm.max_portfolio_risk = risk_config.get('max_portfolio_risk', 0.02)
        self.algorithm.max_drawdown = risk_config.get('max_drawdown', 0.15)
        self.algorithm.volatility_lookback = risk_config.get('volatility_lookback', 20)
        self.algorithm.volatility_threshold = risk_config.get('volatility_threshold', 0.4)
        
        # Load market analysis configuration
        market_config: Dict[str, Any] = parameters.get('market_analysis', {})
        self.algorithm.rsi_period = market_config.get('rsi_period', 14)
        self.algorithm.moving_average_period = market_config.get('moving_average_period', 50)
        self.algorithm.market_volatility_lookback = market_config.get('volatility_lookback', 20)
        
        # Log the configuration being used
        if stocks_config:
            stock_count = len(stocks_config)
            tickers = [stock.get('ticker', 'Unknown') for stock in stocks_config if stock.get('enabled', True)]
            self.algorithm.Log(f"Configuration loaded - {stock_count} stock(s): {', '.join(tickers)}, Delta Range: {self.algorithm.target_delta_min}-{self.algorithm.target_delta_max}, Position Size: {self.algorithm.max_position_size}")
        else:
            self.algorithm.Log(f"Configuration loaded - Ticker: {self.algorithm.ticker}, Delta Range: {self.algorithm.target_delta_min}-{self.algorithm.target_delta_max}, Position Size: {self.algorithm.max_position_size}")
