#!/usr/bin/env python3
"""
Management script for the Options Backtesting Strategy project.
Provides convenient commands for common tasks.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description=""):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def install_dependencies():
    """Install project dependencies."""
    return run_command("pip install -r requirements.txt", "Installing dependencies")

def run_local_backtest():
    """Run a local backtest."""
    return run_command('lean backtest "Options Backtesting Strategy"', "Running local backtest")

def run_cloud_backtest():
    """Run a cloud backtest."""
    commands = [
        ('lean cloud push "Options Backtesting Strategy"', "Pushing to cloud"),
        ('lean cloud backtest "Options Backtesting Strategy"', "Running cloud backtest")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True

def sync_with_cloud():
    """Sync project with QuantConnect cloud."""
    return run_command('lean cloud pull', "Syncing with cloud")

def validate_project():
    """Validate project structure and files."""
    print("🔍 Validating project structure...")
    
    required_files = [
        "main.py",
        "enhanced_broadcom_strategy.py", 
        "strategy_config.py",
        "requirements.txt",
        "config.json"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ Project structure is valid")
    return True

def show_project_info():
    """Show project information."""
    print("📊 Options Backtesting Strategy Project")
    print("=" * 50)
    
    # Read main.py to extract configuration
    try:
        with open("main.py", "r") as f:
            content = f.read()
            
        # Extract ticker
        if 'TICKER = "AVGO"' in content:
            ticker = "AVGO (Broadcom)"
        else:
            ticker = "Custom"
            
        print(f"📈 Underlying Asset: {ticker}")
        print(f"📅 Strategy Type: Short Put Options")
        print(f"🎯 Target Delta: 0.44-0.50")
        print(f"⏰ Expiration Range: 20-60 days")
        print(f"💰 Position Size: 5% per trade")
        
    except Exception as e:
        print(f"⚠️ Could not read project configuration: {e}")
    
    print("\n📁 Project Files:")
    for file in os.listdir("."):
        if file.endswith((".py", ".json", ".txt", ".md")):
            print(f"  - {file}")

def create_strategy_variant(name, ticker, delta_min=0.44, delta_max=0.50):
    """Create a new strategy variant."""
    print(f"🔧 Creating strategy variant: {name}")
    
    # Read the main.py template
    with open("main.py", "r") as f:
        content = f.read()
    
    # Create variant content
    variant_content = f'''# region imports
from AlgorithmImports import *
from enhanced_broadcom_strategy import EnhancedBroadcomShortPutStrategy
# endregion

class {name.replace(" ", "")}Strategy(EnhancedBroadcomShortPutStrategy):
    """
    {name} strategy variant.
    Inherits from EnhancedBroadcomShortPutStrategy for all functionality.
    """
    
    def Initialize(self):
        """
        Initialize the strategy with custom configuration.
        """
        # Load configuration
        self.config = StrategyConfig()
        
        # Customize parameters for this specific backtest
        self.config.START_DATE = (2020, 1, 1)
        self.config.END_DATE = (2024, 12, 31)
        self.config.INITIAL_CASH = 100000
        self.config.TICKER = "{ticker}"
        
        # Strategy parameters
        self.config.MAX_POSITION_SIZE = 0.05  # 5% per trade
        self.config.TARGET_DELTA_MIN = {delta_min}
        self.config.TARGET_DELTA_MAX = {delta_max}
        self.config.MIN_DAYS_TO_EXPIRY = 20
        self.config.MAX_DAYS_TO_EXPIRY = 60
        
        # Risk management
        self.config.PROFIT_TARGET_PCT = 0.50
        self.config.STOP_LOSS_MULTIPLIER = 2.0
        self.config.MIN_DAYS_BEFORE_EXPIRY = 5
        
        # Enable detailed logging
        self.config.ENABLE_DETAILED_LOGGING = True
        self.config.TRACK_DAILY_PNL = True
        
        # Call parent Initialize to set up the strategy
        super().Initialize()
'''
    
    # Write variant file
    variant_filename = f"{name.lower().replace(' ', '_')}_strategy.py"
    with open(variant_filename, "w") as f:
        f.write(variant_content)
    
    print(f"✅ Created strategy variant: {variant_filename}")
    return variant_filename

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Options Backtesting Strategy Management")
    parser.add_argument("command", choices=[
        "install", "backtest", "cloud-backtest", "sync", "validate", 
        "info", "create-variant"
    ], help="Command to execute")
    
    parser.add_argument("--name", help="Strategy variant name (for create-variant)")
    parser.add_argument("--ticker", help="Stock ticker (for create-variant)")
    parser.add_argument("--delta-min", type=float, default=0.44, help="Minimum delta (for create-variant)")
    parser.add_argument("--delta-max", type=float, default=0.50, help="Maximum delta (for create-variant)")
    
    args = parser.parse_args()
    
    # Change to project directory
    project_dir = Path("Options Backtesting Strategy")
    if project_dir.exists():
        os.chdir(project_dir)
    
    if args.command == "install":
        install_dependencies()
    elif args.command == "backtest":
        run_local_backtest()
    elif args.command == "cloud-backtest":
        run_cloud_backtest()
    elif args.command == "sync":
        sync_with_cloud()
    elif args.command == "validate":
        validate_project()
    elif args.command == "info":
        show_project_info()
    elif args.command == "create-variant":
        if not args.name or not args.ticker:
            print("❌ --name and --ticker are required for create-variant")
            sys.exit(1)
        create_strategy_variant(args.name, args.ticker, args.delta_min, args.delta_max)

if __name__ == "__main__":
    main() 