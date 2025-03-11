import csv
import os
from typing import Dict, List, Any, Optional

from config import DATA_DIR
from icann_reports.models.field_metadata import FieldMetadata
from icann_reports.utils.logging_setup import setup_logging
from icann_reports.utils.file_structure import FileStructureAnalyzer
from icann_reports.utils.cache import CacheManager

logger = setup_logging(logger_name="csv_processor")


class CSVProcessor:
    """Processes CSV files from ICANN reports."""

    def __init__(self, data_dir: str = DATA_DIR):
        """Initialize the CSV processor.

        Args:
            data_dir: Directory containing CSV files to process
        """
        self.data_dir = data_dir
        self.field_metadata = FieldMetadata()
        self.file_structure_analyzer = FileStructureAnalyzer()
        self.cache_manager = CacheManager()

    def process_csv(self, file_info: tuple) -> Optional[Dict[str, List[Dict[str, Any]]]]:
        """Process a CSV file and return its data.

        Args:
            file_info: Tuple of (file_path, already_processed)

        Returns:
            Dictionary with file name as key and list of row dictionaries as value,
            or None if file could not be processed
        """
        file_path, already_processed = file_info

        if file_path is None:
            return None

        if already_processed:
            return None

        file_name = os.path.basename(file_path)

        try:
            # Detect file structure
            structure = self.file_structure_analyzer.detect_file_structure(file_path)
            header_rows = structure["header_rows"]

            result = []
            with open(file_path, "r", encoding="utf-8", errors="replace") as file:
                lines = []
                # Only read first few lines to determine headers
                for _ in range(max(5, header_rows + 1)):  # Read enough lines to cover headers
                    try:
                        lines.append(next(file))
                    except StopIteration:
                        break

                # Reset file pointer
                file.seek(0)

                # Skip header lines in the file
                for _ in range(header_rows):
                    next(file)

                # Process the file line by line to avoid loading everything into memory
                reader = csv.DictReader(file)

                # Validate and normalize field names
                field_names = reader.fieldnames or []
                normalized_headers, warnings = self.field_metadata.validate_fields(
                    field_names, file_name
                )

                # If headers don't match expected format, create a new reader with normalized headers
                if normalized_headers != field_names:
                    logger.info(f"Normalizing field names for {file_name}")
                    # Reset file position after headers
                    file.seek(0)
                    for _ in range(header_rows + 1):  # +1 to skip the header line
                        next(file)

                    # Create a custom csv reader with normalized field names
                    csv_reader = csv.reader(file)
                    for row in csv_reader:
                        # Create a dict with normalized field names
                        row_dict = {
                            normalized_headers[i]: val
                            for i, val in enumerate(row)
                            if i < len(normalized_headers)
                        }

                        # If TLD was inferred from filename, add it to the row data
                        if (
                            "TLD" not in field_names
                            and "TLD" in normalized_headers
                            and "-" in file_name
                        ):
                            tld_match = file_name.split("-")[0]
                            row_dict["TLD"] = tld_match.upper()

                        result.append(row_dict)
                else:
                    # Use the original DictReader if headers are already correct
                    for row in reader:
                        # If TLD was inferred from filename, add it to the row data
                        if "TLD" not in field_names and "-" in file_name:
                            tld_match = file_name.split("-")[0]
                            row["TLD"] = tld_match.upper()

                        result.append(row)

            # Mark as processed in cache
            self.cache_manager.add_processed_file(
                file_name,
                {
                    "row_count": len(result),
                    "structure": structure,
                },
            )

            logger.info(
                f"Processed {file_name}: {len(result)} rows, {header_rows} header rows"
            )
            return {file_name: result}

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return None