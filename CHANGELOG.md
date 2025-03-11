# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This file is managed by towncrier. When making changes, create a fragment file in the
`changelog.d` directory with an appropriate category (feature, bugfix, doc, removal, misc).

## [0.0.1](https://github.com/rijnhardtkotze/icann_reports/tree/0.0.1) - 2025-03-11

## ICANN Reports

### Feat

- Added ICANN reports downloader with comprehensive CSV processing

  1. Implemented main script for downloading and processing ICANN domain
     transaction reports
  2. Created robust CSV file handling with support for multiple TLDs and
     dynamic file structures
  3. Added logging, caching, and error handling for CSV downloads and
     processing
  4. Implemented field validation, normalization, and metadata extraction
  5. Configured .gitignore to exclude logs, cache, and CSV data files

  Issue: ([Issue #1](https://github.com/rijnhardtkotze/icann_reports/issues/1))

## Shared

No significant changes.

<!-- towncrier release notes start -->

## [0.0.2](https://github.com/rijnhardtkotze/icann_reports/tree/0.0.2) - 2025-03-11

## ICANN Reports

No significant changes.

## Shared

### Chores

- Add towncrier for automated CHANGELOG.md management

  1. Added [towncrier](https://towncrier.readthedocs.io/en/latest/) for
     changelog management.
  2. Updated CHANGELOG.md to include the towncrier start marker: `<!--
towncrier release notes start -->`
  3. Added documentation in [README.md](README.md) about how to use towncrier
     for changelog entries
  4. Created a [CONTRIBUTING.md](CONTRIBUTING.md) file with detailed
     instructions for creating changelog fragments
  5. Added a pre-commit hook and CI check to ensure PRs include changelog
     fragments when appropriate
  6. Created a [GitHub PR template](.github/pull_request_template.md) that
     reminds contributors to add changelog entries
  7. Documented the [release process](docs/RELEASE_PROCESS.md) that includes
     running towncrier to update the changelog

  Issue: ([Issue #2](https://github.com/rijnhardtkotze/icann_reports/issues/2))
