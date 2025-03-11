#!/usr/bin/env python3
"""Script to check if a pull request has appropriate changelog fragments.

This script is used by the pre-commit hook and CI workflow to ensure that
code changes are properly documented in the changelog.
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import List

# Directories and file patterns that don't require changelog fragments
EXCLUDED_PATHS = [
    r"^\.github/",
    r"^docs/",
    r"^tests/",
    r"^README\.md$",
    r"^CONTRIBUTING\.md$",
    r"^CHANGELOG\.md$",
    r"^\.pre-commit-config\.yaml$",
    r"^changelog\.d/",
    r"^\.gitignore$",
]

# Components that require changelog fragments
COMPONENTS = ["icann_reports", "shared"]

# Valid fragment types
FRAGMENT_TYPES = [
    "feat",
    "change",
    "deprecated",
    "removed",
    "fix",
    "security",
    "chore",
    "deps",
    "docs",
    "other",
]


def is_excluded_path(file_path: str) -> bool:
    """Check if a file path is excluded from requiring a changelog fragment."""
    return any(re.match(pattern, file_path) for pattern in EXCLUDED_PATHS)


def get_changed_files() -> List[str]:
    """Get a list of files changed in the current branch compared to main."""
    try:
        # For Git repositories
        try:
            # Get files changed in the current branch compared to main/master
            result = subprocess.run(
                ["git", "diff", "--name-only", "origin/main"],
                check=True,
                capture_output=True,
                text=True,
            )
            changed_files = result.stdout.strip().split("\n")
        except subprocess.CalledProcessError:
            # If origin/main doesn't exist, get all tracked files
            result = subprocess.run(
                ["git", "ls-files"],
                check=True,
                capture_output=True,
                text=True,
            )
            changed_files = result.stdout.strip().split("\n")

        # Filter out empty strings
        return [f for f in changed_files if f]
    except Exception as e:
        print(f"Warning: Failed to get changed files from git: {e}")
        # Fall back to using files passed as arguments
        return sys.argv[1:] if len(sys.argv) > 1 else []


def get_changelog_fragments() -> List[str]:
    """Get a list of all changelog fragments in the repository."""
    fragments = []
    for component in COMPONENTS:
        component_dir = Path("changelog.d") / component
        if component_dir.exists():
            fragments.extend(
                str(fragment)
                for fragment in component_dir.glob("*.md")
                if fragment.name != "README.md"
            )
    return fragments


def check_fragment_naming() -> List[str]:
    """Check that all changelog fragments follow the naming convention."""
    errors = []
    for component in COMPONENTS:
        component_dir = Path("changelog.d") / component
        if not component_dir.exists():
            continue

        for fragment in component_dir.glob("*.md"):
            # Check naming format: {issue_number}.{fragment_type}.md
            match = re.match(r"^(\d+)\.([^.]+)\.md$", fragment.name)
            if not match:
                errors.append(f"Invalid fragment name: {fragment}")
                continue

            # Check fragment type is valid
            fragment_type = match.group(2)
            if fragment_type not in FRAGMENT_TYPES:
                type_list = ", ".join(FRAGMENT_TYPES)
                errors.append(
                    f"Invalid fragment type '{fragment_type}' in {fragment}. "
                    f"Must be one of: {type_list}"
                )
    return errors


def needs_changelog_fragment(changed_files: List[str]) -> bool:
    """Determine if the changed files require a changelog fragment."""
    return any(not is_excluded_path(file_path) for file_path in changed_files)


def main() -> int:
    """Check for required changelog fragments and validate their format."""
    # Check commit message for [skip changelog]
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            check=True,
            capture_output=True,
            text=True,
        )
        commit_message = result.stdout.strip()
        if "[skip changelog]" in commit_message:
            print(
                "Changelog check skipped due to [skip changelog] "
                "to [skip changelog] in commit message"
            )
            return 0
    except Exception:
        # If we can't get the commit message, continue with the check
        pass

    # Get changed files - either from git or from command line arguments
    changed_files = get_changed_files()

    if not changed_files:
        print("No files changed or no files provided")
        return 0

    # Filter out excluded paths
    relevant_changes = [f for f in changed_files if not is_excluded_path(f)]

    if not relevant_changes:
        print("All changed files are excluded from changelog requirements")
        return 0

    # Check for new changelog fragments
    fragment_errors = check_fragment_naming()

    if fragment_errors:
        print("Errors found in changelog fragments:")
        for error in fragment_errors:
            print(f"  - {error}")
        return 1

    # Look for new changelog fragments among the changed files
    new_fragments = [f for f in changed_files if f.startswith("changelog.d/")]

    if not new_fragments and needs_changelog_fragment(changed_files):
        print("Error: No changelog fragments found.")
        print("\nRelevant files changed:")
        for file in relevant_changes:
            print(f"  - {file}")
        print("\nPlease add a changelog fragment in one of these directories:")
        for component in COMPONENTS:
            print(f"  - changelog.d/{component}/")
        print("\nFragment should be named: {issue_number}.{fragment_type}.md")
        print("Where fragment_type is one of:", ", ".join(FRAGMENT_TYPES))
        msg = (
            "\nOr include [skip changelog] in your commit message "
            "if this change doesn't require a changelog entry."
        )
        print(msg)
        return 1

    # All checks passed
    print("Changelog fragment check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
