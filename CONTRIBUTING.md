# Contributing to ICANN Reports Downloader

Thank you for considering contributing to the ICANN Reports Downloader project! This document provides guidelines to help make the contribution process smooth and effective for everyone.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We value creating a positive and inclusive environment.

## Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature-name`)
3. Make your changes
4. Add tests if applicable
5. Run tests
6. Create changelog fragments (see below)
7. Commit your changes
8. Push to your branch (`git push origin feature-name`)
9. Open a Pull Request

## Changelog Management

This project uses [towncrier](https://towncrier.readthedocs.io/) to manage the changelog. When making changes that need to be documented in the changelog, you must create a changelog fragment.

### Creating Changelog Fragments

1. **Fragment Location**: All changelog fragments should be placed in the `changelog.d` directory, within a subdirectory that matches the component you're updating:
   - `changelog.d/icann_reports/` - For changes to the core ICANN Reports functionality
   - `changelog.d/shared/` - For changes that affect multiple components or project infrastructure

2. **File Naming**: Fragment files should be named according to this pattern:
   ```
   {issue_number}.{fragment_type}.md
   ```

   Where:
   - `issue_number` is the GitHub issue number (use a sequential number if no issue exists)
   - `fragment_type` is one of the types described below

3. **Fragment Types**:
   - `feat`: New features
   - `change`: Changes in existing functionality
   - `deprecated`: Soon-to-be removed features
   - `removed`: Removed features
   - `fix`: Bug fixes
   - `security`: Security fixes
   - `chore`: Maintenance tasks
   - `deps`: Dependency updates
   - `docs`: Documentation updates
   - `other`: Other tasks

4. **Fragment Content**: The content of the fragment should be written in Markdown and should describe the change concisely. Include issue references if applicable.

### Automated Checks for Changelog Fragments

We use automatic checks to ensure that PRs include changelog fragments when appropriate:

1. **Pre-commit Hook**: A pre-commit hook is provided to check for changelog fragments locally before committing.

   To set up pre-commit:
   ```bash
   # Install pre-commit
   pip install pre-commit

   # Install the git hook scripts
   pre-commit install
   ```

   The pre-commit hook will check if your changes require a changelog fragment and will fail the commit if one is missing.

2. **CI Check**: Our GitHub Actions workflow automatically checks PRs to ensure they include changelog fragments when needed.

   The CI checks will:
   - Detect what files were modified
   - Determine if changes require a changelog fragment
   - Validate that appropriate changelog fragments exist
   - Fail the check if fragments are missing

3. **Exemptions**: Some changes don't require a changelog fragment:
   - Documentation-only changes (when only affecting README, docs/, etc.)
   - CI configuration changes
   - Test-only changes
   - Changes to changelog fragments themselves

   In such cases, you can skip the changelog check by including `[skip changelog]` in your commit message.

### Example Fragments

For a new feature (issue #42):
```markdown
# changelog.d/icann_reports/42.feat.md
Added support for processing CCTLD reports with enhanced validation and normalization.
```

For a bug fix (issue #43):
```markdown
# changelog.d/icann_reports/43.fix.md
Fixed issue where date fields in certain CSV formats were not correctly parsed.
```

For a documentation update:
```markdown
# changelog.d/shared/44.docs.md
Updated installation instructions to include virtual environment setup.
```

### Generating the Changelog

The maintainers will generate the changelog during the release process using:

```bash
python -m towncrier --version {version}
```

This will compile all fragment files into the CHANGELOG.md and remove the fragment files.

To preview what the changelog will look like without removing the fragment files:

```bash
python -m towncrier --draft --version {version}
```

## Pull Request Process

1. Ensure your code follows the project's coding style
2. Update documentation as needed
3. Make sure tests pass
4. Include changelog fragments
5. The PR will be merged once it receives approval from the maintainers

## Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/rijnhardtkotze/icann_reports.git
cd icann_reports

# Create a virtual environment using uv
uv venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate

# Install dependencies
uv sync

# Install dev dependencies
uv pip install -r requirements-dev.txt
```

## Running Tests

```bash
behave tests/features/
```

Thank you for contributing to ICANN Reports!
