# Test Suite for QuantConnet

This directory contains comprehensive tests for the QuantConnet algorithmic trading system. The tests are organized by component and strategy to ensure thorough coverage of all functionality.

## Test Structure

```
tests/
├── core/                           # Core module tests
│   ├── test_data_handler.py       # DataHandler tests
│   ├── test_market_analyzer.py    # MarketAnalyzer tests
│   ├── test_risk_manager.py       # RiskManager tests
│   ├── test_correlation_manager.py # CorrelationManager tests
│   └── test_scheduler.py          # Scheduler tests
├── sell_put/                       # Sell Put strategy tests
│   ├── test_portfolio_manager.py  # PortfolioManager tests
│   ├── test_stock_manager.py      # StockManager tests
│   ├── test_position_manager.py   # PositionManager tests
│   └── test_evaluator.py          # Evaluator tests
├── covered_call/                   # Covered Call strategy tests
│   └── test_covered_call_strategy.py # Placeholder for future tests
├── run_tests.py                    # Test runner script
└── README.md                       # This file
```

## Running Tests

### Using the Test Runner Script

The easiest way to run tests is using the provided test runner:

```bash
# Run all tests
python tests/run_tests.py

# Run specific test categories
python tests/run_tests.py core          # Core modules only
python tests/run_tests.py sell_put      # Sell put strategy only
python tests/run_tests.py covered_call  # Covered call strategy only

# Run with verbose output
python tests/run_tests.py -v

# Run with coverage report
python tests/run_tests.py -c

# List all test files
python tests/run_tests.py -l
```

### Using pytest directly

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/core/test_data_handler.py

# Run specific test class
pytest tests/sell_put/test_portfolio_manager.py::TestPortfolioManager

# Run specific test method
pytest tests/core/test_risk_manager.py::TestRiskManager::test_calculate_position_size

# Run with coverage
pytest --cov=. --cov-report=html

# Run with verbose output
pytest -v
```

## Test Coverage

### Core Modules

#### DataHandler (`tests/core/test_data_handler.py`)

- Initialization and configuration
- Data update functionality
- Option delta retrieval
- Plotting decision logic
- Error handling for missing data

#### MarketAnalyzer (`tests/core/test_market_analyzer.py`)

- Market condition analysis
- Trend analysis (bullish/bearish/neutral)
- Volatility analysis and regime detection
- RSI calculation
- Support/resistance level finding
- Market regime determination
- Option premium analysis
- Dynamic parameter adjustment
- Trading avoidance logic

#### RiskManager (`tests/core/test_risk_manager.py`)

- Position size calculation using Kelly Criterion
- Portfolio risk-based sizing
- Margin-based sizing
- Maximum loss calculation
- Volatility adjustment
- Historical win rate calculation
- Average win/loss calculation
- Trading stop conditions
- Risk metrics calculation

#### CorrelationManager (`tests/core/test_correlation_manager.py`)

- Correlation data update
- Correlation matrix calculation
- Stock correlation retrieval
- High correlation stock identification
- Trading reduction decisions
- Correlation summary generation
- Memory management

#### Scheduler (`tests/core/test_scheduler.py`)

- Task addition and removal
- Task execution timing (daily/weekly/monthly)
- Task execution logic
- Multiple task handling
- Exception handling
- Task management utilities

### Sell Put Strategy

#### PortfolioManager (`tests/sell_put/test_portfolio_manager.py`)

- Portfolio initialization and configuration
- Stock manager initialization
- Portfolio data updates
- Portfolio performance tracking
- Risk limit checking
- Position management
- Trading opportunity identification
- Portfolio metrics calculation

#### StockManager (`tests/sell_put/test_stock_manager.py`)

- Stock-specific initialization
- Data updates and price history management
- Trading condition evaluation
- Position entry and exit logic
- Performance tracking
- Risk management integration

#### PositionManager (`tests/sell_put/test_position_manager.py`)

- Position entry and exit decisions
- Option contract selection
- Market condition filtering
- Dynamic parameter adjustment
- Option frequency validation
- Contract selection criteria

#### Evaluator (`tests/sell_put/test_evaluator.py`)

- End-of-algorithm performance evaluation
- Trade statistics calculation
- Win rate and profit factor analysis
- Trade duration analysis
- Sharpe ratio calculation
- Risk metrics summary
- Exception handling

### Covered Call Strategy

Currently contains placeholder tests for future implementation.

## Test Features

### Comprehensive Coverage

- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **Edge Cases**: Boundary condition testing
- **Error Handling**: Exception and error scenario testing

### Mocking Strategy

- Uses `unittest.mock` for external dependencies
- Mocks QuantConnect algorithm objects
- Mocks market data and option chains
- Mocks portfolio and position objects

### Test Data

- Realistic market scenarios
- Various volatility regimes
- Different market conditions
- Edge cases and error conditions

### Assertions

- Functional correctness
- State validation
- Method call verification
- Return value validation
- Exception handling verification

## Best Practices

### Writing New Tests

1. Follow the existing naming convention: `test_*.py`
2. Use descriptive test method names
3. Test both success and failure scenarios
4. Include edge cases and boundary conditions
5. Mock external dependencies appropriately
6. Use meaningful assertions

### Test Organization

1. Group related tests in classes
2. Use setup and teardown methods when needed
3. Keep tests independent and isolated
4. Use descriptive docstrings

### Running Tests

1. Run tests before committing changes
2. Use coverage reports to identify untested code
3. Fix failing tests before merging
4. Add new tests for new functionality

## Continuous Integration

The test suite is designed to work with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    python -m pip install pytest pytest-cov
    python tests/run_tests.py -c
```

## Coverage Reports

Generate coverage reports to identify untested code:

```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html

# Generate terminal coverage report
pytest --cov=. --cov-report=term-missing
```

The HTML report will be generated in `htmlcov/index.html`.

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the project root is in the Python path
2. **Mock Issues**: Check that external dependencies are properly mocked
3. **Test Failures**: Verify that the code under test hasn't changed significantly

### Debugging Tests

```bash
# Run specific test with debug output
pytest tests/core/test_risk_manager.py::TestRiskManager::test_calculate_position_size -v -s

# Run with print statements visible
pytest -s

# Run with maximum verbosity
pytest -vvv
```

## Contributing

When adding new functionality:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve test coverage
4. Update this README if adding new test categories

## Test Dependencies

The tests require the following packages:

- `pytest`
- `pytest-cov` (for coverage reports)
- `numpy` (for numerical calculations)
- `unittest.mock` (for mocking)

Install with:

```bash
pip install pytest pytest-cov numpy
```
