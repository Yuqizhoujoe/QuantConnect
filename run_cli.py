#!/usr/bin/env python3
"""
QuantConnect Options Trading Strategy CLI Runner.

This script provides a command-line interface for running different trading strategies
in QuantConnect. It is for local/command-line use only, not for Lean backtesting.
"""
import argparse
import sys
from datetime import datetime
from typing import Type, Any, Optional


def run_backtest(
    strategy_class: Type[Any],
    config_path: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> None:
    """
    Run a backtest with the specified strategy.

    Args:
        strategy_class: The strategy class to run
        config_path: Path to configuration file
        start_date: Start date for backtest (YYYY-MM-DD)
        end_date: End date for backtest (YYYY-MM-DD)
    """
    # Default dates if not provided
    if not start_date:
        start_date = "2014-01-01"
    if not end_date:
        end_date = "2014-12-31"

    # Parse dates
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    # Default config if not provided
    if not config_path:
        if "SellPut" in strategy_class.__name__:
            config_path = "sell_put_stock.json"
        else:
            config_path = "covered_call_stock.json"

    # Create and run strategy
    strategy = strategy_class()
    strategy.Initialize(start_dt, end_dt, config_path)

    print(f"Running {strategy_class.__name__} from {start_date} to {end_date}")
    print(f"Using config: {config_path}")


def get_strategy_class(strategy_name: str) -> Type[Any]:
    """
    Get the strategy class based on the strategy name.

    Args:
        strategy_name: Name of the strategy

    Returns:
        Strategy class
    """
    # Import here to avoid issues when running CLI outside QuantConnect
    try:
        if strategy_name == "sell_put":
            from strategies.sell_put.sell_put_strategy import SellPutOptionStrategy

            return SellPutOptionStrategy
        elif strategy_name == "covered_call":
            from strategies.covered_call.covered_call_strategy import (
                CoveredCallStrategy,
            )

            return CoveredCallStrategy
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")
    except ImportError as e:
        print(f"Error importing strategy {strategy_name}: {e}")
        print("Make sure you're running this in a QuantConnect environment.")
        sys.exit(1)


def main() -> None:
    """
    Main CLI entry point for running backtests.
    """
    parser = argparse.ArgumentParser(
        description="Run QuantConnect options trading strategy backtest (CLI/local only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_cli.py --strategy sell_put
  python run_cli.py --strategy covered_call --config aggressive.json
  python run_cli.py --strategy sell_put --start-date 2023-01-01 --end-date 2023-12-31
  python run_cli.py --strategy sell_put --verbose
        """,
    )

    parser.add_argument(
        "--strategy",
        choices=["sell_put", "covered_call"],
        default="sell_put",
        help="Strategy to run (default: sell_put)",
    )

    parser.add_argument(
        "--config",
        help="Path to configuration file (default: strategy-specific config)",
    )

    parser.add_argument(
        "--start-date",
        help="Start date for backtest (YYYY-MM-DD format, default: 2014-01-01)",
    )

    parser.add_argument(
        "--end-date",
        help="End date for backtest (YYYY-MM-DD format, default: 2014-12-31)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "--list-strategies",
        action="store_true",
        help="List available strategies and exit",
    )

    args = parser.parse_args()

    if args.list_strategies:
        print("Available strategies:")
        print("  sell_put      - Sell put options strategy")
        print("  covered_call  - Covered call options strategy")
        print("\nUsage:")
        print("  python run_cli.py --strategy sell_put")
        sys.exit(0)

    strategy_class = get_strategy_class(args.strategy)

    if args.verbose:
        print(f"Selected strategy: {args.strategy}")
        print(f"Strategy class: {strategy_class.__name__}")
        if args.config:
            print(f"Config file: {args.config}")
        if args.start_date:
            print(f"Start date: {args.start_date}")
        if args.end_date:
            print(f"End date: {args.end_date}")

    try:
        run_backtest(
            strategy_class=strategy_class,
            config_path=args.config,
            start_date=args.start_date,
            end_date=args.end_date,
        )
    except Exception as e:
        print(f"Error running backtest: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
