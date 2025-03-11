import pytest
from behave import given, when, then

from icann_reports.processor.field_validation import FieldValidator
from icann_reports.models.field_metadata import FieldMetadata


@pytest.fixture
def field_validator():
    return FieldValidator()


@given('I have a row with all required fields')
def step_row_with_all_fields(context):
    """Create a sample row with all required fields."""
    # Create a row with all the fields from the expected fields in config.py
    from config import EXPECTED_FIELDS
    
    # Create a dictionary with all expected fields
    context.row = {
        field: "100" for field in EXPECTED_FIELDS.keys()
    }
    
    # Set a few specific values
    context.row["TLD"] = "COM"
    context.row["Registrar-name"] = "Example Registrar"
    context.row["IANA-ID"] = "123"
    context.row["Total-domains"] = "100000"
    context.row["Total-Nameservers"] = "500"
    context.row["Net-adds-1-yr"] = "1000"
    context.row["Net-renews-1-yr"] = "500"
    
    context.field_validator = FieldValidator()


@given('I have a row missing some required fields')
def step_row_missing_fields(context):
    """Create a sample row missing some required fields."""
    context.row = {
        "TLD": "COM",
        "Registrar-name": "Example Registrar",
        # Missing IANA-ID
        "Total-domains": "100000",
        # Missing Total-Nameservers
    }
    context.field_validator = FieldValidator()
    # Define only certain fields as required for this test
    context.expected_fields = {"TLD", "Registrar-name", "IANA-ID", "Total-domains", "Total-Nameservers"}


@given('I have a row with non-numeric values in numeric fields')
def step_row_with_invalid_types(context):
    """Create a sample row with invalid data types."""
    context.row = {
        "TLD": "COM",
        "Registrar-name": "Example Registrar",
        "IANA-ID": "123",
        "Total-domains": "invalid",  # Should be a number
        "Total-Nameservers": "N/A",  # Should be a number
        "Net-adds-1-yr": "1000",
    }
    context.field_validator = FieldValidator()


@when('I validate the row')
def step_validate_row(context):
    """Validate the sample row."""
    if hasattr(context, 'expected_fields'):
        context.is_valid, context.validation_errors = context.field_validator.validate_row(
            context.row, context.expected_fields
        )
    else:
        context.is_valid, context.validation_errors = context.field_validator.validate_row(
            context.row
        )


@then('the row should be valid')
def step_row_should_be_valid(context):
    """Check that the row is considered valid."""
    assert context.is_valid, f"Row should be valid, but got errors: {context.validation_errors}"


@then('the row should be invalid')
def step_row_should_be_invalid(context):
    """Check that the row is considered invalid."""
    assert not context.is_valid, "Row should be invalid but was considered valid"


@then('no validation errors should be reported')
def step_no_validation_errors(context):
    """Check that there are no validation errors."""
    assert len(context.validation_errors) == 0, f"Unexpected validation errors: {context.validation_errors}"


@then('validation errors should list the missing fields')
def step_validation_errors_missing_fields(context):
    """Check that validation errors include missing fields."""
    assert len(context.validation_errors) > 0, "No validation errors reported"
    missing_fields_error = any("Missing required fields" in error for error in context.validation_errors)
    assert missing_fields_error, "No error about missing fields"
    # Check specific fields in error message
    for field in ["IANA-ID", "Total-Nameservers"]:
        field_in_error = any(field in error for error in context.validation_errors)
        assert field_in_error, f"Field '{field}' not mentioned in validation errors"


@then('validation errors should report the type mismatches')
def step_validation_errors_type_mismatches(context):
    """Check that validation errors include type mismatches."""
    assert len(context.validation_errors) > 0, "No validation errors reported"
    for field in ["Total-domains", "Total-Nameservers"]:
        field_in_error = any(field in error for error in context.validation_errors)
        assert field_in_error, f"Field '{field}' type mismatch not reported in validation errors"


@given('I have validation results for multiple files')
def step_have_validation_results(context):
    """Create sample validation results for multiple files."""
    context.validation_results = {
        "file1.csv": {
            "total_rows": 100,
            "valid_rows": 95,
            "invalid_rows": 5,
            "errors": [
                "Row 10: Field 'Total-domains' should be a number, got 'invalid'",
                "Row 20: Missing required fields: IANA-ID",
                "Row 30: Field 'Total-Nameservers' should be a number, got 'N/A'",
                "Row 40: Missing required fields: TLD",
                "Row 50: Field 'Net-adds-1-yr' should be a number, got 'many'",
            ]
        },
        "file2.csv": {
            "total_rows": 50,
            "valid_rows": 50,
            "invalid_rows": 0,
            "errors": []
        }
    }
    context.field_validator = FieldValidator()


@when('I generate a validation report')
def step_generate_validation_report(context):
    """Generate a validation report from the validation results."""
    context.report = context.field_validator.get_validation_report(context.validation_results)


@then('the report should include a summary for each file')
def step_report_includes_file_summaries(context):
    """Check that the report includes a summary for each file."""
    for file_name in context.validation_results.keys():
        assert file_name in context.report, f"Report does not include summary for {file_name}"


@then('the report should list the number of valid and invalid rows')
def step_report_includes_row_counts(context):
    """Check that the report includes valid and invalid row counts."""
    for file_name, results in context.validation_results.items():
        assert f"Total rows: {results['total_rows']}" in context.report, f"Missing total rows for {file_name}"
        assert f"Valid rows: {results['valid_rows']}" in context.report, f"Missing valid rows for {file_name}"
        assert f"Invalid rows: {results['invalid_rows']}" in context.report, f"Missing invalid rows for {file_name}"


@then('the report should include details of validation errors')
def step_report_includes_error_details(context):
    """Check that the report includes details of validation errors."""
    # Check that file1 errors are included (file2 has no errors)
    for error in context.validation_results["file1.csv"]["errors"][:5]:  # Check first 5 errors
        assert error in context.report, f"Error not included in report: {error}"