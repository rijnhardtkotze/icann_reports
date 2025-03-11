# Release Process

This document outlines the steps to create a new release of the ICANN Reports Downloader.

## Pre-release Checklist

1. [ ] Ensure all tests pass on the main branch
2. [ ] Check that documentation is up to date
3. [ ] Review open pull requests that should be included
4. [ ] Verify all CI checks are passing

## Release Steps

### 1. Update Version

The project uses `hatch-vcs` for version management, which automatically determines the version based on git tags. You don't need to manually update version numbers in files.

### 2. Generate the Changelog

1. First, review the changelog fragments in `changelog.d/`:
   ```bash
   ls changelog.d/icann_reports/
   ls changelog.d/shared/
   ```

2. Generate the changelog for the new version:
   ```bash
   # For a production release
   python -m towncrier build --version X.Y.Z

   # For a pre-release
   python -m towncrier build --version X.Y.ZaN  # alpha
   # or
   python -m towncrier build --version X.Y.ZbN  # beta
   # or
   python -m towncrier build --version X.Y.ZrcN # release candidate
   ```

   This will:
   - Compile all fragments into a new section in CHANGELOG.md
   - Delete the used fragment files
   - Stage the changes in git

3. Review the generated changelog section in CHANGELOG.md
   - Ensure all changes are properly categorized
   - Check that the formatting is correct
   - Verify that issue/PR references are correct

### 3. Create the Release

1. Commit the changelog changes:
   ```bash
   git commit -m "Release version X.Y.Z"
   ```

2. Create and push a signed tag:
   ```bash
   git tag -s vX.Y.Z -m "Version X.Y.Z"
   git push origin vX.Y.Z
   ```

3. Push the changelog changes:
   ```bash
   git push origin main
   ```

### 4. Build and Publish

1. Clean the build directory:
   ```bash
   rm -rf dist/ build/ *.egg-info/
   ```

2. Set up a clean environment and install build dependencies:
   ```bash
   # Create a fresh venv for building
   uv venv .venv-build
   source .venv-build/bin/activate  # On Windows: .venv-build\Scripts\activate

   # Install build dependencies
   uv pip install build hatch-vcs
   ```

3. Build the package:
   ```bash
   uv pip build .
   ```

4. Verify the built distributions:
   ```bash
   ls dist/
   ```

5. Upload to PyPI:
   ```bash
   # Install twine using uv
   uv pip install twine

   # Upload to PyPI
   twine upload dist/*
   ```

6. Clean up build environment:
   ```bash
   deactivate
   rm -rf .venv-build
   ```

### 5. Post-release Tasks

1. Create a GitHub release:
   - Go to GitHub Releases
   - Create a new release from the tag
   - Copy the relevant section from CHANGELOG.md
   - Add any additional release notes or binary attachments

2. Verify the release:
   - Create a fresh environment to test installation:
     ```bash
     uv venv .venv-test
     source .venv-test/bin/activate  # On Windows: .venv-test\Scripts\activate

     # Install the package from PyPI
     uv pip install icann-reports

     # Run basic tests
     python -c "import icann_reports; print(icann_reports.__version__)"

     # Clean up test environment
     deactivate
     rm -rf .venv-test
     ```
   - Check PyPI listing
   - Verify documentation links

3. Announce the release (if applicable):
   - Update documentation site
   - Notify users/stakeholders
   - Post announcements in relevant channels

## Handling Pre-releases

For pre-releases (alpha, beta, release candidates):

1. Follow the same process but use appropriate version suffixes:
   - Alpha: `X.Y.ZaN` (e.g., `1.2.3a1`)
   - Beta: `X.Y.ZbN` (e.g., `1.2.3b1`)
   - Release Candidate: `X.Y.ZrcN` (e.g., `1.2.3rc1`)

2. When generating the changelog, use the full version including the suffix:
   ```bash
   python -m towncrier build --version 1.2.3b1
   ```

3. Tag names should include the full version:
   ```bash
   git tag -s v1.2.3b1 -m "Version 1.2.3 Beta 1"
   ```

## Troubleshooting

### Common Issues

1. **Towncrier fails to find fragments**:
   - Verify fragment files are in the correct directories
   - Check file naming follows the convention
   - Ensure fragment types are valid

2. **Version conflicts**:
   - Check git tags for existing versions
   - Verify version format matches PEP 440

3. **Build failures**:
   - Clean build directories
   - Verify Python environment
   - Check dependencies are up to date
   - Try rebuilding the virtual environment:
     ```bash
     rm -rf .venv-build
     uv venv .venv-build
     source .venv-build/bin/activate
     uv pip install build hatch-vcs
     ```

### Emergency Fixes

If issues are discovered immediately after a release:

1. Create a hotfix branch from the release tag
2. Fix the issue
3. Add a changelog fragment
4. Release a patch version following the normal process

## Notes

- Always use signed tags for releases
- Keep changelog entries clear and user-focused
- Follow [Semantic Versioning](https://semver.org/)
- Test the release process in a clean environment when possible
- Use `uv` for all Python package management operations for consistency and speed
