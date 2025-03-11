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

## Contributing

### Changelog Management

This project uses [towncrier](https://github.com/twisted/towncrier) to manage the changelog. The changelog is stored in `CHANGELOG.md` and is automatically updated during releases.

#### Adding a Changelog Entry

1. Create a news fragment in the `changelog.d` directory. The fragment should be placed in the appropriate subdirectory based on the module that was worked on. If it relates to more than one module, it should be placed in the `shared/` directory

2. Name the file with a brief identifier, such as the issue number or a short description followed by the category of the change. For example:
   - `changelog.d/icann_reports/001-initial-setup.feat.md`
   - `changelog.d/shared/002-add-towncrier.chore.md`

   > [!NOTE]
   > The types of categories that are available to you:
   >   - `{file_name}.feat.md` - for new features
   >   - `{file_name}.change.md` - for changes to existing features
   >   - `{file_name}.deprecated.md` - for deprecations of features in the future
   >   - `{file_name}.removed.md` - for removals of features
   >   - `{file_name}.fix.md` - for bug fixes
   >   - `{file_name}.security.md` - for security updates
   >   - `{file_name}.chore.md` - for non-functional changes
   >   - `{file_name}.deps.md` - for dependency changes
   >   - `{file_name}.docs.md` - for documentation updates
   >   - `{file_name}.other.md` - for other tasks

3. In the file, write a brief description of the change (less than two sentences if possible)

4. When releasing a new version, run `towncrier build --version=X.Y.Z` to update the CHANGELOG.md file

## Project Structure

```text
icann_reports/
├── config.py                    # Configuration settings
├── main.py                      # Main entry point
├── docs/                        # Documentation
├── changelog.d/                 # Changelog fragments
│   ├── icann_reports/   .       # New features
│   ├── shared/                  # Bug fixes
├── CHANGELOG.md                 # Generated changelog
├── icann_reports/               # Main package
│   ├── __init__.py              # Package init
│   ├── main.py                  # CLI entry point
│   ├── data/
│   │   ├── cache/               # Cache directory
│   │   ├── logs/                # Log files
│   │   ├── reports/             # Generated reports
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
└── tests/
    ├── __init__.py              # Package init
    ├── conftest.py              # Test fixtures and configuration
    ├── README.md                # Test documentation
    ├── features/                # BDD feature files
    │   ├── url_generator.feature
    │   ├── csv_processor.feature
    │   ├── field_validation.feature
    │   └── reports_generator.feature
    └── steps/                   # Step implementations
        ├── __init__.py
        ├── test_url_generator.py
        └── test_field_validation.py
```

## Installation

```bash
# Clone the repository
git clone https://github.com/rijnhardtkotze/icann_reports.git
cd icann_reports

# Create and activate a virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
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

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.
