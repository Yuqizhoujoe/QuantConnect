#!/usr/bin/env python3
"""
Test runner for the quantconnet project.

This script runs all tests in the project and provides a comprehensive test report.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_tests_with_pytest(test_path, verbose=False, coverage=False):
    """
    Run tests using pytest.

    Args:
        test_path: Path to test directory or file
        verbose: Whether to run in verbose mode
        coverage: Whether to run with coverage
    """
    cmd = ["python", "-m", "pytest"]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term-missing", "--cov-report=html"])

    cmd.append(str(test_path))

    print(f"Running: {' '.join(cmd)}")
    print("-" * 80)

    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running tests: {e}")
        return False


def run_specific_test_category(category, verbose=False, coverage=False):
    """
    Run tests for a specific category.

    Args:
        category: Test category ('core', 'sell_put', 'covered_call', 'all')
        verbose: Whether to run in verbose mode
        coverage: Whether to run with coverage
    """
    test_dir = Path(__file__).parent

    if category == "all":
        return run_tests_with_pytest(test_dir, verbose, coverage)
    elif category == "core":
        return run_tests_with_pytest(test_dir / "core", verbose, coverage)
    elif category == "sell_put":
        return run_tests_with_pytest(test_dir / "sell_put", verbose, coverage)
    elif category == "covered_call":
        return run_tests_with_pytest(test_dir / "covered_call", verbose, coverage)
    else:
        print(f"Unknown test category: {category}")
        return False


def list_test_files():
    """List all test files in the project."""
    test_dir = Path(__file__).parent
    test_files = []

    for test_file in test_dir.rglob("test_*.py"):
        relative_path = test_file.relative_to(test_dir)
        test_files.append(str(relative_path))

    return sorted(test_files)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run tests for quantconnet project")
    parser.add_argument(
        "category",
        nargs="?",
        default="all",
        choices=["all", "core", "sell_put", "covered_call"],
        help="Test category to run (default: all)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Run tests in verbose mode"
    )
    parser.add_argument(
        "-c", "--coverage", action="store_true", help="Run tests with coverage report"
    )
    parser.add_argument("-l", "--list", action="store_true", help="List all test files")

    args = parser.parse_args()

    if args.list:
        print("Test files in the project:")
        test_files = list_test_files()
        for test_file in test_files:
            print(f"  {test_file}")
        return

    print(f"Running tests for category: {args.category}")
    print(f"Verbose: {args.verbose}")
    print(f"Coverage: {args.coverage}")
    print()

    success = run_specific_test_category(args.category, args.verbose, args.coverage)

    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
