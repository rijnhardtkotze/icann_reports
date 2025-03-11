import os
import pytest
import tempfile
import csv
from behave import given, when, then

from icann_reports.processor.csv_processor import CSVProcessor
from icann_reports.utils.cache import CacheManager


@pytest.fixture
def csv_processor():
    return CSVProcessor()


@given('I have a CSV file with standard headers')
def step_have_csv_with_standard_headers(context):
    """Create a temporary CSV file with standard headers."""
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    context.temp_file_path = temp_file.name
    
    # Write standard headers and sample data
    with open(context.temp_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['TLD', 'Registrar-name', 'IANA-ID', 'Total-domains', 'Net-adds-1-yr'])
        writer.writerow(['COM', 'Example Registrar', '123', '100000', '500'])
        writer.writerow(['COM', 'Another Registrar', '456', '200000', '1000'])
    
    # Initialize processor
    context.csv_processor = CSVProcessor()
    context.file_info = (context.temp_file_path, False)


@given('I have a CSV file with non-standard headers')
def step_have_csv_with_non_standard_headers(context):
    """Create a temporary CSV file with non-standard headers."""
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    context.temp_file_path = temp_file.name
    
    # Write non-standard headers and sample data
    with open(context.temp_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['tld', 'registrar_name', 'iana-id', 'total-domains', 'net_adds_1yr'])
        writer.writerow(['COM', 'Example Registrar', '123', '100000', '500'])
        writer.writerow(['COM', 'Another Registrar', '456', '200000', '1000'])
    
    # Initialize processor
    context.csv_processor = CSVProcessor()
    context.file_info = (context.temp_file_path, False)


@given('I have a CSV file with name "{filename}" missing the TLD field')
def step_have_csv_missing_tld_field(context, filename):
    """Create a temporary CSV file missing the TLD field with a specific name."""
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    context.temp_file_path = temp_file.name
    
    # Create a temporary directory for the processor
    context.temp_dir = tempfile.TemporaryDirectory()
    
    # Copy the temp file to a file with the specific name in the temp directory
    context.specific_file_path = os.path.join(context.temp_dir.name, filename)
    
    # Write headers without TLD and sample data
    with open(context.specific_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Registrar-name', 'IANA-ID', 'Total-domains', 'Net-adds-1-yr'])
        writer.writerow(['Example Registrar', '123', '100000', '500'])
        writer.writerow(['Another Registrar', '456', '200000', '1000'])
    
    # Initialize processor with the temp directory
    context.csv_processor = CSVProcessor(data_dir=context.temp_dir.name)
    context.file_info = (context.specific_file_path, False)


@given('I have a CSV file that has already been processed')
def step_have_already_processed_csv(context):
    """Create a temporary CSV file and mark it as already processed."""
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    context.temp_file_path = temp_file.name
    
    # Write some data
    with open(context.temp_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['TLD', 'Registrar-name', 'IANA-ID', 'Total-domains', 'Net-adds-1-yr'])
        writer.writerow(['COM', 'Example Registrar', '123', '100000', '500'])
    
    # Initialize processor
    context.csv_processor = CSVProcessor()
    
    # Mark the file as already processed
    context.file_info = (context.temp_file_path, True)


@when('I process the CSV file')
def step_process_csv_file(context):
    """Process the CSV file."""
    context.result = context.csv_processor.process_csv(context.file_info)


@then('the field names should be normalized')
def step_field_names_normalized(context):
    """Check that field names are normalized."""
    assert context.result is not None, "Processing result is None"
    
    file_name = os.path.basename(context.temp_file_path)
    assert file_name in context.result, f"File {file_name} not found in results"
    
    # Check first row to verify field names are normalized
    first_row = context.result[file_name][0]
    assert 'TLD' in first_row, "TLD field not normalized"
    assert 'Registrar-name' in first_row, "Registrar-name field not normalized"
    assert 'IANA-ID' in first_row, "IANA-ID field not normalized"
    assert 'Total-domains' in first_row, "Total-domains field not normalized"
    assert 'Net-adds-1-yr' in first_row, "Net-adds-1-yr field not normalized"


@then('the rows should be parsed correctly')
def step_rows_parsed_correctly(context):
    """Check that rows are parsed correctly."""
    assert context.result is not None, "Processing result is None"
    
    file_name = os.path.basename(context.temp_file_path)
    rows = context.result[file_name]
    
    assert len(rows) == 2, f"Expected 2 rows, got {len(rows)}"
    
    # Check values in first row
    assert rows[0]['TLD'] == 'COM', f"Incorrect TLD value: {rows[0]['TLD']}"
    assert rows[0]['Registrar-name'] == 'Example Registrar', f"Incorrect Registrar-name value: {rows[0]['Registrar-name']}"
    assert rows[0]['IANA-ID'] == '123', f"Incorrect IANA-ID value: {rows[0]['IANA-ID']}"
    assert rows[0]['Total-domains'] == '100000', f"Incorrect Total-domains value: {rows[0]['Total-domains']}"
    assert rows[0]['Net-adds-1-yr'] == '500', f"Incorrect Net-adds-1-yr value: {rows[0]['Net-adds-1-yr']}"


@then('the field names should be mapped to standard names')
def step_field_names_mapped(context):
    """Check that non-standard field names are mapped to standard names."""
    assert context.result is not None, "Processing result is None"
    
    file_name = os.path.basename(context.temp_file_path)
    assert file_name in context.result, f"File {file_name} not found in results"
    
    # Check first row to verify field names are standardized
    first_row = context.result[file_name][0]
    assert 'TLD' in first_row, "TLD field not mapped"
    assert 'Registrar-name' in first_row, "Registrar-name field not mapped"
    assert 'IANA-ID' in first_row, "IANA-ID field not mapped"
    assert 'Total-domains' in first_row, "Total-domains field not mapped"
    assert 'Net-adds-1-yr' in first_row, "Net-adds-1-yr field not mapped"


@then('the rows should be parsed with normalized field names')
def step_rows_parsed_with_normalized_names(context):
    """Check that rows are parsed with normalized field names."""
    assert context.result is not None, "Processing result is None"
    
    file_name = os.path.basename(context.temp_file_path)
    rows = context.result[file_name]
    
    assert len(rows) == 2, f"Expected 2 rows, got {len(rows)}"
    
    # Check values in first row with normalized field names
    assert rows[0]['TLD'] == 'COM', f"Incorrect TLD value: {rows[0]['TLD']}"
    assert rows[0]['Registrar-name'] == 'Example Registrar', f"Incorrect Registrar-name value: {rows[0]['Registrar-name']}"
    assert rows[0]['IANA-ID'] == '123', f"Incorrect IANA-ID value: {rows[0]['IANA-ID']}"
    assert rows[0]['Total-domains'] == '100000', f"Incorrect Total-domains value: {rows[0]['Total-domains']}"
    assert rows[0]['Net-adds-1-yr'] == '500', f"Incorrect Net-adds-1-yr value: {rows[0]['Net-adds-1-yr']}"


@then('the TLD field should be inferred from the filename')
def step_tld_inferred_from_filename(context):
    """Check that the TLD field is inferred from the filename."""
    assert context.result is not None, "Processing result is None"
    
    file_name = os.path.basename(context.specific_file_path)
    assert file_name in context.result, f"File {file_name} not found in results"
    
    # Check that TLD field exists in the results despite not being in the original CSV
    first_row = context.result[file_name][0]
    assert 'TLD' in first_row, "TLD field not inferred from filename"


@then('the value "{tld_value}" should be set for the TLD field in all rows')
def step_tld_value_set_in_all_rows(context, tld_value):
    """Check that the TLD field has the correct value in all rows."""
    assert context.result is not None, "Processing result is None"
    
    file_name = os.path.basename(context.specific_file_path)
    rows = context.result[file_name]
    
    # Check that all rows have the correct TLD value
    for i, row in enumerate(rows):
        assert row['TLD'] == tld_value, f"Row {i}: Expected TLD value {tld_value}, got {row['TLD']}"


@then('the file should be skipped')
def step_file_should_be_skipped(context):
    """Check that the already processed file was skipped."""
    # Result should be None for already processed files
    assert context.result is None, "Result is not None, file was not skipped"


@then('no data should be returned')
def step_no_data_returned(context):
    """Check that no data was returned for the skipped file."""
    assert context.result is None, "Data was returned despite file being skipped"


# Clean up temporary files in after_scenario hook
def after_scenario(context, scenario):
    """Clean up any temporary files created during testing."""
    if hasattr(context, 'temp_file_path') and os.path.exists(context.temp_file_path):
        os.unlink(context.temp_file_path)
    
    if hasattr(context, 'temp_dir'):
        context.temp_dir.cleanup()