import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import logging
import os


@dataclass
class Config:
    """
    Simple configuration class to hold all strategy parameters.
    Now acts as a pure data container; all values are set by the loader.
    """

    # Portfolio settings
    total_cash: Optional[int] = None
    max_stocks: Optional[int] = None
    max_portfolio_risk: Optional[float] = None
    max_drawdown: Optional[float] = None
    correlation_threshold: Optional[float] = None

    # Stock configurations
    stocks: List[Dict[str, Any]] = field(default_factory=list)

    # Risk management settings
    volatility_lookback: Optional[int] = None
    volatility_threshold: Optional[float] = None
    correlation_lookback: Optional[int] = None

    # Market analysis settings
    rsi_period: Optional[int] = None
    moving_average_period: Optional[int] = None
    market_volatility_lookback: Optional[int] = None

    # Legacy single-stock settings (for backward compatibility)
    ticker: Optional[str] = None
    target_delta_min: Optional[float] = None
    target_delta_max: Optional[float] = None
    max_position_size: Optional[float] = None
    option_frequency: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """
        Create a Config instance from a dictionary with sensible defaults.

        Args:
            data: Dictionary containing configuration data

        Returns:
            Config: New Config instance with values from data and defaults
        """
        # Handle nested structure where config is under "parameters" key
        if "parameters" in data:
            data = data["parameters"]

        # Extract values from nested structure
        portfolio = data.get("portfolio", {})
        risk = data.get("risk_management", {})
        market = data.get("market_analysis", {})

        config = cls(
            # Portfolio settings
            total_cash=portfolio.get("total_cash", 100000),
            max_stocks=portfolio.get("max_stocks", 1),
            max_portfolio_risk=portfolio.get("max_portfolio_risk", 0.02),
            max_drawdown=portfolio.get("max_drawdown", 0.15),
            correlation_threshold=portfolio.get("correlation_threshold", 0.7),
            # Stocks configuration
            stocks=data.get("stocks", []),
            # Risk management settings
            volatility_lookback=risk.get("volatility_lookback", 20),
            volatility_threshold=risk.get("volatility_threshold", 0.4),
            correlation_lookback=risk.get("correlation_lookback", 60),
            # Market analysis settings
            rsi_period=market.get("rsi_period", 14),
            moving_average_period=market.get("moving_average_period", 50),
            market_volatility_lookback=market.get("volatility_lookback", 20),
            # Legacy single-stock settings
            ticker=data.get("ticker", "AAPL"),
            target_delta_min=data.get("target_delta_min", 0.25),
            target_delta_max=data.get("target_delta_max", 0.75),
            max_position_size=data.get("max_position_size", 0.20),
            option_frequency=data.get("option_frequency", "monthly"),
            start_date=data.get("start_date", "2020-01-01"),
            end_date=data.get("end_date", "2025-01-01"),
        )
        
        return config


class ConfigLoader:
    """
    Handles loading configuration settings from file or embedded defaults.
    This class separates the strategy's parameters from its core logic, allowing
    for easy tuning without modifying the Python code.
    """

    @staticmethod
    def _find_config_file(config_file: str) -> Optional[str]:
        """
        Find the config file in various possible locations.
        
        Args:
            config_file: The config file name or path
            
        Returns:
            str: Full path to the config file if found, None otherwise
        """
        # Get the directory of this file (config/common_config_loader.py)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Define possible paths to search
        search_paths = [
            config_file,  # Original path
            os.path.join("config", config_file),  # config/config_file
            os.path.join(project_root, config_file),  # project_root/config_file
            os.path.join(project_root, "config", config_file),  # project_root/config/config_file
        ]
        
        # Try each path
        for path in search_paths:
            if os.path.exists(path):
                return path
                
        return None

    @staticmethod
    def load_config(config_file: str) -> Config:
        """
        Loads configuration from embedded settings or tries to load from file.
        Falls back to embedded configuration if file loading fails.

        Args:
            config_file: The path to the JSON configuration file (optional).

        Returns:
            Config: The loaded configuration object.
        """
        # Try to load from file
        config_path = ConfigLoader._find_config_file(config_file)
        
        if config_path:
            try:
                with open(config_path, "r") as f:
                    file_config = json.loads(f.read())
                    logging.info(f"Successfully loaded configuration from {config_path}")
                    config = Config.from_dict(file_config)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logging.warning(f"Error loading config file {config_path}: {e}. Using default configuration.")
                config = Config()
        else:
            logging.warning(f"Config file {config_file} not found. Using default configuration.")
            config = Config()

        # Log the configuration being used
        if config.stocks:
            stock_count = len(config.stocks)
            tickers = [
                stock.get("ticker", "Unknown")
                for stock in config.stocks
                if stock.get("enabled", True)
            ]
            logging.info(
                f"Configuration loaded - {stock_count} stock(s): {', '.join(tickers)}, Delta Range: {config.target_delta_min}-{config.target_delta_max}, Position Size: {config.max_position_size}"
            )
        else:
            logging.info(
                f"Configuration loaded - Ticker: {config.ticker}, Delta Range: {config.target_delta_min}-{config.target_delta_max}, Position Size: {config.max_position_size}"
            )

        return config
