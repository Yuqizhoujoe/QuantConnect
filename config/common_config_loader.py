
import json
from typing import Dict, Any, Optional, List

class StrategyConfig:
    """
    Simple configuration class for easy parameter modification.
    Modify these values to change strategy behavior.
    """
    TICKER: str = "AVGO"
    TARGET_DELTA_MIN: float = 0.20  # More flexible delta range
    TARGET_DELTA_MAX: float = 0.60  # More flexible delta range
    MAX_POSITION_SIZE: float = 0.20
    OPTION_FREQUENCY: str = "monthly"
    START_DATE: str = "2020-01-01"
    END_DATE: str = "2025-01-01"
    CASH: int = 100000

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
                "ticker": StrategyConfig.TICKER,
                "target_delta_min": StrategyConfig.TARGET_DELTA_MIN,
                "target_delta_max": StrategyConfig.TARGET_DELTA_MAX,
                "max_position_size": StrategyConfig.MAX_POSITION_SIZE,
                "option_frequency": StrategyConfig.OPTION_FREQUENCY,
                "start_date": StrategyConfig.START_DATE,
                "end_date": StrategyConfig.END_DATE,
                "cash": StrategyConfig.CASH
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
                config_path: str = os.path.join('config', config_file)
                with open(config_path, 'r') as f:
                    config = json.load(f)
                self.algorithm.Log(f"Successfully loaded configuration from config directory: {config_path}")
            except FileNotFoundError:
                # Try with absolute path from current file location
                try:
                    current_dir: str = os.path.dirname(os.path.abspath(__file__))
                    config_path: str = os.path.join(current_dir, config_file)
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    self.algorithm.Log(f"Successfully loaded configuration from absolute path: {config_path}")
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
        
        self.algorithm.ticker = parameters.get('ticker', StrategyConfig.TICKER)
        self.algorithm.target_delta_min = parameters.get('target_delta_min', StrategyConfig.TARGET_DELTA_MIN)
        self.algorithm.target_delta_max = parameters.get('target_delta_max', StrategyConfig.TARGET_DELTA_MAX)
        self.algorithm.max_position_size = parameters.get('max_position_size', StrategyConfig.MAX_POSITION_SIZE)
        self.algorithm.option_frequency = parameters.get('option_frequency', StrategyConfig.OPTION_FREQUENCY)
        
        # Parse the start and end dates from string format (YYYY-MM-DD).
        start_date: List[str] = parameters.get('start_date', StrategyConfig.START_DATE).split('-')
        self.algorithm.SetStartDate(int(start_date[0]), int(start_date[1]), int(start_date[2]))
        
        end_date: List[str] = parameters.get('end_date', StrategyConfig.END_DATE).split('-')
        self.algorithm.SetEndDate(int(end_date[0]), int(end_date[1]), int(end_date[2]))
        
        # Set the initial cash for the backtest.
        self.algorithm.SetCash(parameters.get('cash', StrategyConfig.CASH))
        
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
        self.algorithm.Log(f"Configuration loaded - Ticker: {self.algorithm.ticker}, Delta Range: {self.algorithm.target_delta_min}-{self.algorithm.target_delta_max}, Position Size: {self.algorithm.max_position_size}")
