# ICANN Reports Downloader - Tests

This directory contains BDD (Behavior-Driven Development) tests for the ICANN Reports Downloader project, using the Gherkin syntax and behave framework.

## Test Structure

The tests are organized as follows:

- `features/`: Contains Gherkin feature files that describe scenarios in human-readable format
- `steps/`: Contains Python step definitions that implement the scenarios
- `conftest.py`: Contains pytest fixtures for the tests

## Running the Tests

### Prerequisites

To run the tests, you need to install the following dependencies:

```bash
pip install pytest behave pytest-bdd
```

### Running BDD Tests

To run all BDD tests:

```bash
cd icann-reports-downloader
behave tests/features
```

To run a specific feature:

```bash
behave tests/features/url_generator.feature
```

### Running with pytest

You can also run the tests using pytest:

```bash
cd icann-reports-downloader
python -m pytest tests/steps
```

## Test Coverage

The tests cover the following areas:

1. **URL Generator**: Tests for generating URLs for ICANN reports based on TLD configurations
2. **CSV Processor**: Tests for processing CSV files, normalizing field names, and extracting data
3. **Field Validation**: Tests for validating field names and data types in CSV rows
4. **Reports Generator**: Tests for generating summary reports from processed data

## Adding New Tests

To add a new test:

1. Create a feature file in the `features/` directory describing the behavior
2. Implement the step definitions in the `steps/` directory
3. Add any required fixtures to `conftest.py`