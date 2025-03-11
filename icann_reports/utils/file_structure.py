import csv
import os
from typing import Dict, List, Optional, Any

from config import HEADER_PATTERNS
from icann_reports.utils.logging_setup import setup_logging

logger = setup_logging(logger_name="file_structure")


class FileStructureAnalyzer:
    """Analyzes CSV files to determine their structure and format."""

    def __init__(self):
        """Initialize the file structure analyzer."""
        self.file_structures: Dict[str, List[Dict[str, Any]]] = {}

    def detect_file_structure(self, file_path: str) -> Dict[str, Any]:
        """Detect the structure of a CSV file by examining its header.

        Args:
            file_path: Path to the CSV file

        Returns:
            Dict containing structure information including:
                - tld: The TLD for this file
                - header_rows: Number of header rows to skip
                - header_type: Type of header (standard, icann_report, etc.)
        """
        file_name = os.path.basename(file_path)

        # Extract TLD from filename (assuming format like "com-transactions-YYYYMM-en.csv")
        tld_match = file_name.split("-")[0] if "-" in file_name else None

        # If we already know the structure for this TLD, use it
        for tld, structures in self.file_structures.items():
            if tld_match and tld == tld_match and structures:
                # Use the most recent structure for this TLD
                logger.info(f"Using known structure for {tld} file: {file_name}")
                return structures[-1]

        # Need to detect structure
        logger.info(f"Detecting file structure for: {file_name}")

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                # Read the first few lines to detect headers
                lines = []
                for _ in range(10):  # Read up to 10 lines
                    try:
                        line = next(f)
                        lines.append(line.strip())
                    except StopIteration:
                        break

            # Analyze the lines to determine structure
            header_rows = 0
            header_type = "standard"

            # Check for ICANN report header patterns
            for i, line in enumerate(lines):
                if any(pattern in line for pattern in HEADER_PATTERNS):
                    header_type = "icann_report"
                    header_rows = i + 1

                # Look for CSV header row (contains expected field names)
                if i > 0:  # Skip first row since it might be a title
                    csv_reader = csv.reader([line])
                    headers = list(next(csv_reader, []))

                    # If this looks like a proper header row with known fields
                    normalized_headers = [h.lower() for h in headers]
                    if any(
                        field.lower() in normalized_headers
                        for field in ["tld", "registrar-name", "iana-id"]
                    ):
                        header_rows = i
                        break

            # Create structure info
            structure = {
                "tld": tld_match,
                "header_rows": header_rows,
                "header_type": header_type,
                "detected_from": file_name,
            }

            # Save this structure
            if tld_match:
                if tld_match not in self.file_structures:
                    self.file_structures[tld_match] = []
                self.file_structures[tld_match].append(structure)

            return structure

        except Exception as e:
            logger.error(f"Error detecting file structure: {e}")
            # Return a default structure
            return {
                "tld": tld_match,
                "header_rows": 0,
                "header_type": "standard",
                "detected_from": file_name,
            }

    def get_file_structure_report(self) -> str:
        """Get a report of detected file structures by TLD.
        
        Returns:
            String containing a formatted report of file structures
        """
        if not self.file_structures:
            return "No file structures detected yet."

        report = ["File Structure Report by TLD:"]

        for tld, structures in self.file_structures.items():
            report.append(f"\n{tld.upper()}:")
            for structure in structures:
                report.append(f"  - From file: {structure['detected_from']}")
                report.append(f"    Header rows: {structure['header_rows']}")
                report.append(f"    Header type: {structure['header_type']}")

        return "\n".join(report)