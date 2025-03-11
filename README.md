# ICANN Reports Downloader

## Project Description
This project downloads the transaction reports for each registrar at ICANN and processes it for further analysis. It fetches CSV files from ICANN's website, normalizes field names, validates data, and generates summary reports.

## Features

- Download transaction reports for specified TLDs and date ranges
- Normalize field names for consistent processing
- Validate data fields and types
- Generate summary reports by registrar and TLD
- Concurrent processing for improved performance
- Robust error handling and logging
- Caching to avoid reprocessing files

## Project Structure

```text
icann-reports-downloader/
├── config.py                    # Configuration settings
├── main.py                      # Main entry point
├── docs/                        # Documentation
├── icann_reports/               # Main package
│   ├── __init__.py              # Package init
│   ├── main.py                  # CLI entry point
│   ├── utils/
│   │   ├── __init__.py          # Package init
│   │   ├── logging_setup.py     # Logging configuration 
│   │   ├── cache.py             # Cache management
│   │   └── file_structure.py    # File structure detection
│   ├── downloader/
│   │   ├── __init__.py          # Package init
│   │   ├── url_generator.py     # URL generation logic
│   │   └── csv_downloader.py    # CSV downloading functionality
│   ├── processor/
│   │   ├── __init__.py          # Package init
│   │   ├── csv_processor.py     # CSV processing logic
│   │   ├── field_validation.py  # Field validation logic
│   │   └── reports.py           # Reporting functionality
│   ├── models/
│   │   ├── __init__.py          # Package init
│   │   └── field_metadata.py    # Field definitions and metadata
├── tests/
│   ├── __init__.py              # Package init
│   ├── conftest.py              # Test fixtures and configuration
│   ├── README.md                # Test documentation
│   ├── features/                # BDD feature files
│   │   ├── url_generator.feature
│   │   ├── csv_processor.feature
│   │   ├── field_validation.feature
│   │   └── reports_generator.feature
│   └── steps/                   # Step implementations
│       ├── __init__.py
│       ├── test_url_generator.py
│       └── test_field_validation.py
└── data/
    ├── cache/                   # Cache directory
    ├── logs/                    # Log files
    └── reports/                 # Generated reports
```

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/icann-reports-downloader.git
cd icann-reports-downloader

# Create and activate a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Usage

### Basic Usage

```bash
python main.py
```

### Command Line Options

The script supports the following command line options:

- `--tld`: TLD to process (default: com)
- `--start-date`: Start date in YYYY-MM format (default: 2024-01)
- `--end-date`: End date in YYYY-MM format (default: 2024-11)
- `--max-workers`: Maximum number of worker threads (default: 12)
- `--validate`: Validate the data after processing
- `--generate-reports`: Generate summary reports after processing
- `--verbose`: Enable verbose logging

Example:

```bash
python main.py --tld net --start-date 2023-01 --end-date 2023-12 --validate --generate-reports
```

## Testing

The project uses Behavior-Driven Development (BDD) with the `behave` framework. See the [test readme](tests/README.md) for details on running tests.

Basic test command:

```bash
behave tests/features
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.