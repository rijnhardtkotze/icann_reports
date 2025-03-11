from typing import Dict, List, Any, Set, Tuple, Optional

from icann_reports.models.field_metadata import FieldMetadata
from icann_reports.utils.logging_setup import setup_logging

logger = setup_logging(logger_name="field_validation")


class FieldValidator:
    """Validates fields in CSV data against expected formats."""

    def __init__(self, field_metadata: Optional[FieldMetadata] = None):
        """Initialize the field validator.

        Args:
            field_metadata: FieldMetadata instance to use for validation
        """
        self.field_metadata = field_metadata or FieldMetadata()

    def validate_row(
        self, row: Dict[str, Any], expected_fields: Optional[Set[str]] = None
    ) -> Tuple[bool, List[str]]:
        """Validate a single data row against expected fields.

        Args:
            row: Dictionary representing a CSV row
            expected_fields: Set of expected field names (if None, uses all fields)

        Returns:
            Tuple of (is_valid, validation_errors)
                - is_valid: True if row is valid, False otherwise
                - validation_errors: List of error messages
        """
        validation_errors = []
        
        # Use either provided expected fields or all fields from field metadata
        fields_to_check = expected_fields or set(self.field_metadata.expected_fields.keys())
        
        # Check for missing required fields
        missing_fields = fields_to_check - set(row.keys())
        if missing_fields:
            validation_errors.append(f"Missing required fields: {', '.join(missing_fields)}")
            
        # Check data types and values
        for field_name, value in row.items():
            if field_name in fields_to_check:
                # Validate field based on expected type
                if field_name in ["Total-domains", "Total-Nameservers"] or field_name.startswith(("Net-adds-", "Net-renews-", "Transfer-", "Deleted-", "Restored-")):
                    # Should be a number
                    try:
                        # Try to convert to int (some values might be empty strings)
                        if value and not value.isspace():
                            int(value)
                    except (ValueError, TypeError):
                        validation_errors.append(f"Field '{field_name}' should be a number, got '{value}'")
                        
        return len(validation_errors) == 0, validation_errors
    
    def validate_data(
        self, data: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Dict[str, Any]]:
        """Validate all data in CSV files.

        Args:
            data: Dictionary with file names as keys and lists of row dictionaries as values

        Returns:
            Dictionary with validation results per file
        """
        validation_results = {}
        
        for file_name, rows in data.items():
            file_results = {
                "total_rows": len(rows),
                "valid_rows": 0,
                "invalid_rows": 0,
                "errors": [],
            }
            
            for i, row in enumerate(rows):
                is_valid, errors = self.validate_row(row)
                
                if is_valid:
                    file_results["valid_rows"] += 1
                else:
                    file_results["invalid_rows"] += 1
                    for error in errors:
                        file_results["errors"].append(f"Row {i+1}: {error}")
                        
            # Log summary of validation
            if file_results["invalid_rows"] > 0:
                logger.warning(
                    f"Validation for {file_name}: {file_results['invalid_rows']} "
                    f"out of {file_results['total_rows']} rows have errors"
                )
            else:
                logger.info(f"Validation for {file_name}: All {file_results['total_rows']} rows are valid")
                
            validation_results[file_name] = file_results
            
        return validation_results
    
    def get_validation_report(self, validation_results: Dict[str, Dict[str, Any]]) -> str:
        """Generate a human-readable validation report.

        Args:
            validation_results: Dictionary of validation results per file

        Returns:
            String containing formatted validation report
        """
        report = ["Validation Report:"]
        
        for file_name, results in validation_results.items():
            report.append(f"\n{file_name}:")
            report.append(f"  Total rows: {results['total_rows']}")
            report.append(f"  Valid rows: {results['valid_rows']}")
            report.append(f"  Invalid rows: {results['invalid_rows']}")
            
            if results["invalid_rows"] > 0:
                report.append(f"\n  Errors:")
                # Limit to first 10 errors to avoid overwhelming report
                for i, error in enumerate(results["errors"][:10]):
                    report.append(f"    - {error}")
                    
                if len(results["errors"]) > 10:
                    report.append(f"    ... and {len(results['errors']) - 10} more errors")
                    
        return "\n".join(report)