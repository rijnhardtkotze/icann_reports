from dataclasses import dataclass
from typing import Dict, List, Optional

from config import EXPECTED_FIELDS


@dataclass
class FieldInfo:
    """Information about a CSV field."""
    name: str
    description: str
    normalized_name: str


class FieldMetadata:
    """Manages metadata for CSV fields."""
    
    def __init__(self, expected_fields: Optional[Dict[str, str]] = None):
        """Initialize field metadata.
        
        Args:
            expected_fields: Dictionary of field names and descriptions
        """
        self.expected_fields = expected_fields or EXPECTED_FIELDS
        self.field_name_mapping = self._create_field_mapping()
        self.field_validation_issues: Dict[str, List[str]] = {}
        
    def _create_field_mapping(self) -> Dict[str, Dict[str, str]]:
        """Create a mapping of normalized field names to original fields.
        
        Returns:
            Dictionary mapping normalized names to original field names and descriptions
        """
        return {
            self.normalize_string(field): {
                "column": field,
                "description": self.expected_fields[field],
            }
            for field in self.expected_fields.keys()
        }
        
    @staticmethod
    def normalize_string(text: str) -> str:
        """Normalize a string by removing special characters and making lowercase.
        
        Args:
            text: String to normalize
            
        Returns:
            Normalized string
        """
        return text.lower().replace("-", "").replace("_", "")
        
    def normalize_field_name(self, field_name: str) -> str:
        """Normalize a field name to match expected format.
        
        Args:
            field_name: The original field name from the CSV
            
        Returns:
            The standardized field name, or original if no match found
        """
        normalized = self.normalize_string(field_name)
        mapping = self.field_name_mapping.get(normalized)
        if mapping:
            return mapping["column"]
        return field_name
        
    def validate_fields(self, headers: List[str], file_name: str) -> tuple[List[str], List[str]]:
        """Validate that the headers match expected fields.
        
        Args:
            headers: The headers from the CSV file
            file_name: Name of the file being processed
            
        Returns:
            Tuple of (normalized_headers, warnings)
                - normalized_headers: List of headers with standardized names
                - warnings: List of warning messages about missing/unexpected fields
        """
        normalized_headers = [self.normalize_field_name(h.strip()) for h in headers]
        warnings = []
        
        # Check for missing required fields
        missing_fields = set(self.expected_fields.keys()) - set(normalized_headers)
        
        # If TLD is missing but can be inferred from filename, add it to normalized headers
        if "TLD" in missing_fields and "-" in file_name:
            # Extract TLD from filename (assuming format like "com-transactions-YYYYMM-en.csv")
            tld_match = file_name.split("-")[0]
            if tld_match:
                # Note that we're keeping track of the inferred TLD, but we'll keep the warning
                # to maintain transparency about the file structure
                normalized_headers.append("TLD")
                missing_fields.remove("TLD")
                warnings.append(
                    f"TLD field not found in CSV, inferred as '{tld_match}' from filename"
                )
        
        if missing_fields:
            warnings.append(f"Missing expected fields: {', '.join(missing_fields)}")
            
        # Check for unexpected fields
        unexpected_fields = set(normalized_headers) - set(self.expected_fields.keys())
        if unexpected_fields:
            warnings.append(f"Found unexpected fields: {', '.join(unexpected_fields)}")
            
            # Dynamically add unexpected fields with inferred meanings
            for field in unexpected_fields:
                if field not in self.expected_fields:
                    # Add to expected_fields with an inferred description
                    inferred_desc = self._infer_field_description(field)
                    self.expected_fields[field] = f"[Inferred] {inferred_desc}"
                    
                    # Update field name mapping
                    self.field_name_mapping[self.normalize_string(field)] = {
                        "column": field,
                        "description": self.expected_fields[field],
                    }
        
        # Store validation results
        if warnings:
            self.field_validation_issues[file_name] = warnings
            
        return normalized_headers, warnings
    
    def _infer_field_description(self, field_name: str) -> str:
        """Infer a description for an unknown field based on its name.
        
        Args:
            field_name: The field name to infer a description for
            
        Returns:
            An inferred description of the field
        """
        field = field_name.lower()
        
        # Try to infer meaning from field name parts
        if "agp-exemption" in field:
            if "request" in field:
                return "Number of Add Grace Period exemption requests"
            if "grant" in field:
                return "Number of Add Grace Period exemptions granted"
            if "domain" in field:
                return "Number of domains with Add Grace Period exemptions"
            return "Add Grace Period exemption related metric"
            
        if "consolidate-transaction" in field:
            if "day" in field:
                return "Days in the consolidate transaction period"
            return "Number of consolidate transactions"
            
        if "attempted-add" in field:
            return "Number of attempted domain additions"
            
        # General fallback for unknown fields
        words = field.replace("-", " ").split()
        if len(words) > 1:
            # Try to create a sensible description from the field name itself
            return f"{' '.join(word.capitalize() for word in words[1:])} {words[0].capitalize()}"
            
        return f"Unknown metric: {field_name}"
        
    def get_field_description(self, field: str) -> str:
        """Get a human-readable description for a field.
        
        Args:
            field: The field name
            
        Returns:
            A description of the field
        """
        # First check if field has been added to expected_fields
        if field in self.expected_fields:
            return self.expected_fields[field]
            
        # Try to infer from field name
        return self._infer_field_description(field)
        
    def get_field_validation_report(self) -> str:
        """Get a report of all field validation issues.
        
        Returns:
            String containing a formatted report of validation issues
        """
        if not self.field_validation_issues:
            return "No field validation issues found."
            
        report = ["Field Validation Issues:"]
        for file_name, warnings in self.field_validation_issues.items():
            report.append(f"\n{file_name}:")
            for warning in warnings:
                report.append(f"  - {warning}")
                
        return "\n".join(report)
        
    def get_field_metadata_by_category(self) -> Dict[str, Dict[str, str]]:
        """Get metadata about all the fields in a structured format by category.
        
        Returns:
            Dictionary with field information organized by category
        """
        # Group fields by categories
        categories = {
            "General": [
                "TLD",
                "Registrar-name",
                "IANA-ID",
                "Total-domains",
                "Total-Nameservers",
            ],
            "Additions": [
                field for field in self.expected_fields if field.startswith("Net-adds-")
            ],
            "Renewals": [
                field for field in self.expected_fields if field.startswith("Net-renews-")
            ],
            "Transfers": [
                field for field in self.expected_fields if field.startswith("Transfer-")
            ],
            "Deletions": [
                field for field in self.expected_fields if field.startswith("Deleted-")
            ],
            "Restorations": [
                field for field in self.expected_fields if field.startswith("Restored-")
            ],
        }
        
        # Add "Other" category for any fields not already categorized
        categorized_fields = set(field for fields in categories.values() for field in fields)
        uncategorized = set(self.expected_fields.keys()) - categorized_fields
        if uncategorized:
            categories["Other"] = list(uncategorized)
            
        # Build metadata structure
        metadata = {}
        for category, fields in categories.items():
            metadata[category] = {
                field: self.get_field_description(field) for field in fields
            }
            
        return metadata