"""
Configuration loader for trading strategies.
"""

import json
import os
from typing import Dict, Any, Optional


class ConfigLoader:
    """
    Loads and manages configuration for different trading strategies.
    """

    def __init__(self, config_dir: str = "config"):
        """
        Initialize the config loader.

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir

    def load_strategy_config(self, strategy_name: str) -> Dict[str, Any]:
        """
        Load configuration for a specific strategy.

        Args:
            strategy_name: Name of the strategy (e.g., 'sell_put', 'covered_call')

        Returns:
            Configuration dictionary
        """
        config_file = f"{strategy_name}_config.json"
        config_path = os.path.join(self.config_dir, config_file)

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r") as f:
            config = json.load(f)

        return config

    def load_backtest_config(self, strategy_name: str) -> Dict[str, Any]:
        """
        Load backtest configuration for a specific strategy.

        Args:
            strategy_name: Name of the strategy

        Returns:
            Backtest configuration dictionary
        """
        config_file = f"backtest_{strategy_name}.json"
        config_path = os.path.join(self.config_dir, config_file)

        if not os.path.exists(config_path):
            # Fall back to default backtest config
            config_path = os.path.join(self.config_dir, "backtest.json")

        if not os.path.exists(config_path):
            # Return default configuration
            return self.get_default_backtest_config(strategy_name)

        with open(config_path, "r") as f:
            config = json.load(f)

        return config

    def get_default_backtest_config(self, strategy_name: str) -> Dict[str, Any]:
        """
        Get default backtest configuration for a strategy.

        Args:
            strategy_name: Name of the strategy

        Returns:
            Default backtest configuration
        """
        return {
            "strategy": strategy_name,
            "start_date": "2014-01-01",
            "end_date": "2014-12-31",
            "initial_cash": 100000,
            "benchmark": "SPY",
            "data_resolution": "minute",
            "warmup_days": 30,
        }

    def save_config(self, config: Dict[str, Any], filename: str) -> None:
        """
        Save configuration to a file.

        Args:
            config: Configuration dictionary
            filename: Name of the file to save to
        """
        config_path = os.path.join(self.config_dir, filename)

        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

    def list_available_configs(self) -> list:
        """
        List all available configuration files.

        Returns:
            List of configuration filenames
        """
        if not os.path.exists(self.config_dir):
            return []

        configs = []
        for filename in os.listdir(self.config_dir):
            if filename.endswith(".json"):
                configs.append(filename)

        return sorted(configs)
