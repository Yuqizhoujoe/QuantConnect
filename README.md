# QuantConnect Options Trading System

A professional-grade options trading system for QuantConnect with support for sell put and covered call strategies. Built with dependency injection, modular architecture, and comprehensive risk management.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Running Strategies](#running-strategies)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)

## 🎯 Project Overview

This system provides automated options trading strategies for QuantConnect with:

- **Sell Put Strategy**: Generate income by selling put options
- **Covered Call Strategy**: Enhance returns on stock positions
- **Risk Management**: Built-in position sizing, correlation limits, and drawdown protection
- **Modular Design**: Easy to extend with new strategies
- **Professional CLI**: Command-line interface for backtesting

## ✨ Features

- 🔧 **Dependency Injection**: Clean separation of concerns
- 📊 **Risk Management**: Position sizing, correlation limits, volatility thresholds
- 🎛️ **Flexible Configuration**: JSON-based configuration with sensible defaults
- 📈 **Performance Tracking**: Comprehensive metrics and reporting
- 🧪 **Testable**: Unit tests for all components
- 🚀 **Production Ready**: Used in live trading environments

## 🔧 Prerequisites

### Required Software

- **Python 3.8+** (3.11 recommended)
- **Lean CLI** (QuantConnect's local backtesting engine)
- **Git** (for version control)

### Optional

- **QuantConnect Account** (for cloud backtesting)
- **Docker** (for containerized deployment)

### System Requirements

- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space for data and logs
- **OS**: Windows, macOS, or Linux

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd quantconnet
```

### Step 2: Install Dependencies

#### Option A: Using uv (Recommended)

```bash
# Install uv if not already installed
pip install uv

# Install dependencies
uv sync
```

#### Option B: Using pip

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Install Lean CLI

```bash
# Install Lean CLI
pip install lean

# Verify installation
lean --version
```

### Step 4: Configure Lean

```bash
# Initialize Lean configuration
lean init

# Login to QuantConnect (optional, for cloud features)
lean login
```

## 🏃‍♂️ Quick Start

### 1. Run Your First Backtest

```bash
# Run sell put strategy (default)
lean backtest run_backtest.py
```

### 2. Check Results

The backtest will output:

- Portfolio performance metrics
- Trade history
- Risk statistics
- Configuration used

### 3. View Logs

```bash
# View latest backtest logs
lean logs
```

## ⚙️ Configuration

### Configuration Files

The system uses JSON configuration files:

- `sell_put_stock.json` - Default sell put strategy config
- `config/sell_put_stock.json` - Alternative config location
- `config/covered_call_stock.json` - Covered call strategy config

### Basic Configuration Structure

```json
{
  "parameters": {
    "portfolio": {
      "total_cash": 100000,
      "max_stocks": 1,
      "max_portfolio_risk": 0.02,
      "max_drawdown": 0.15
    },
    "stocks": [
      {
        "ticker": "AAPL",
        "weight": 1.0,
        "target_delta_min": 0.25,
        "target_delta_max": 0.75,
        "max_position_size": 0.2,
        "option_frequency": "monthly",
        "enabled": true
      }
    ],
    "risk_management": {
      "volatility_lookback": 20,
      "volatility_threshold": 0.4,
      "correlation_lookback": 60
    }
  }
}
```

### Key Configuration Parameters

| Parameter              | Description                     | Default | Range     |
| ---------------------- | ------------------------------- | ------- | --------- |
| `total_cash`           | Initial portfolio value         | 100000  | 10000+    |
| `max_stocks`           | Maximum stocks to trade         | 1       | 1-10      |
| `max_position_size`    | Max % of portfolio per position | 0.20    | 0.01-0.50 |
| `target_delta_min`     | Minimum delta for options       | 0.25    | 0.10-0.50 |
| `target_delta_max`     | Maximum delta for options       | 0.75    | 0.50-0.90 |
| `volatility_threshold` | Minimum volatility required     | 0.4     | 0.2-1.0   |

### Creating Custom Configurations

1. **Copy existing config**:

   ```bash
   cp sell_put_stock.json my_config.json
   ```

2. **Edit parameters**:

   ```json
   {
     "parameters": {
       "portfolio": {
         "total_cash": 50000,
         "max_stocks": 3
       },
       "stocks": [
         {
           "ticker": "AAPL",
           "target_delta_min": 0.3,
           "target_delta_max": 0.7
         },
         {
           "ticker": "MSFT",
           "target_delta_min": 0.25,
           "target_delta_max": 0.75
         }
       ]
     }
   }
   ```

3. **Run with custom config**:
   ```bash
   lean backtest run_backtest.py --config my_config.json
   ```

## 🎮 Running Strategies

### Method 1: Lean CLI (Recommended)

```bash
# Run sell put strategy
lean backtest run_backtest.py

# Run with specific configuration
lean backtest run_backtest.py --config aggressive.json

# Run with custom parameters
lean backtest run_backtest.py --config my_config.json
```

### Method 2: Python CLI (Local Testing)

```bash
# Run sell put strategy
python run_cli.py --strategy sell_put

# Run with verbose logging
python run_cli.py --strategy sell_put --verbose

# Run with custom date range
python run_cli.py --strategy sell_put --start-date 2023-01-01 --end-date 2023-12-31

# List available strategies
python run_cli.py --list-strategies
```

### Method 3: Direct Execution

```bash
# Run the main backtest file
python run_backtest.py
```

## 📁 Project Structure

```
quantconnet/
├── run_backtest.py                    # Main backtest entry point (Lean)
├── run_cli.py                         # CLI runner for local testing
├── config/
│   ├── common_config_loader.py        # Configuration loading system
│   ├── sell_put_stock.json            # Sell put strategy config
│   ├── covered_call_stock.json        # Covered call strategy config
│   └── backtest.json                  # Lean backtest configuration
├── shared/
│   ├── interfaces/                    # Common interfaces
│   ├── utils/                         # Shared utilities
│   ├── analysis/                      # Shared analysis tools
│   └── types/                         # Common type definitions
├── strategies/
│   ├── sell_put/                      # Sell put strategy
│   │   ├── components/                # Strategy components
│   │   ├── context.py                 # Strategy context
│   │   └── sell_put_strategy.py       # Main strategy class
│   └── covered_call/                  # Covered call strategy
├── tests/                             # Unit tests
├── backtests/                         # Backtest results
└── data/                              # Market data (if any)
```

## 📦 Dependencies

### Core Dependencies

```toml
# Python packages
python = "^3.8"
pandas = "^2.0.0"
numpy = "^1.24.0"
scipy = "^1.10.0"

# QuantConnect
lean = "^2.5.0"
quantconnect = "^1.0.0"

# Development
pytest = "^7.0.0"
black = "^23.0.0"
flake8 = "^6.0.0"
```

### Optional Dependencies

```toml
# Data analysis
matplotlib = "^3.7.0"
seaborn = "^0.12.0"
plotly = "^5.15.0"

# Performance
numba = "^0.57.0"
cython = "^3.0.0"
```

### Installing Dependencies

```bash
# Install all dependencies
uv sync

# Install with development tools
uv sync --dev

# Install specific version
uv add pandas==2.0.0
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Lean CLI Not Found

```bash
# Reinstall Lean CLI
pip uninstall lean
pip install lean

# Verify installation
lean --version
```

#### 2. Configuration File Not Found

```bash
# Check file exists
ls -la sell_put_stock.json

# Use absolute path
lean backtest run_backtest.py --config /full/path/to/config.json
```

#### 3. Python Import Errors

```bash
# Check Python version
python --version

# Reinstall dependencies
uv sync --reinstall

# Check virtual environment
which python
```

#### 4. Permission Errors

```bash
# Fix file permissions
chmod +x run_backtest.py
chmod +x run_cli.py

# Run with sudo (if needed)
sudo lean backtest run_backtest.py
```

### Debug Mode

```bash
# Run with debug logging
lean backtest run_backtest.py --verbose

# Check logs
lean logs --tail 100

# View detailed output
lean backtest run_backtest.py --debug
```

### Getting Help

```bash
# Lean CLI help
lean --help
lean backtest --help

# Python CLI help
python run_cli.py --help

# Check system status
lean status
```

## 📚 Documentation

### Core Documentation

- **[Architecture Guide](ARCHITECTURE.md)** - System design and architecture
- **[Finance Terms](FINANCE_TERMS.md)** - Glossary of trading terms
- **[Strategy Selection Guide](STRATEGY_SELECTION_GUIDE.md)** - How to choose strategies
- **[Comprehensive Guide](COMPREHENSIVE_GUIDE.md)** - Complete system documentation

### API Documentation

```bash
# Generate documentation
pydoc -w strategies/
pydoc -w shared/
```

### Code Examples

```python
# Load configuration
from config.common_config_loader import ConfigLoader
config = ConfigLoader.load_config('sell_put_stock.json')

# Create strategy context
from strategies.sell_put.context import StrategyContext
context = StrategyContext(config=config, ...)

# Run strategy
strategy = SellPutOptionStrategy()
strategy.Initialize(start_date, end_date, config_path)
```

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd quantconnet

# Install development dependencies
uv sync --dev

# Run tests
pytest tests/

# Format code
black .
flake8 .
```

### Code Standards

- **Python**: PEP 8 compliance
- **Type Hints**: Required for all functions
- **Documentation**: Docstrings for all classes and methods
- **Tests**: Unit tests for all components

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
