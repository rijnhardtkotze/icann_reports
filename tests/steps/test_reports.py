import os
import json
import tempfile
import pytest
from behave import given, when, then

from icann_reports.processor.reports import ReportGenerator


@pytest.fixture
def report_generator():
    return ReportGenerator()


@given('I have processed data from multiple files')
def step_have_processed_data(context):
    """Create sample processed data from multiple files."""
    context.processed_data = {
        "com-transactions-202401-en.csv": [
            {
                "TLD": "COM",
                "Registrar-name": "Example Registrar",
                "IANA-ID": "123",
                "Total-domains": "100000",
                "Total-Nameservers": "500",
                "Net-adds-1-yr": "1000",
                "Net-renews-1-yr": "500",
                "Transfer-gaining-successful": "50",
                "Transfer-losing-successful": "30",
                "Deleted-domains-grace": "20",
                "Deleted-domains-nograce": "10"
            },
            {
                "TLD": "COM",
                "Registrar-name": "Another Registrar",
                "IANA-ID": "456",
                "Total-domains": "200000",
                "Total-Nameservers": "800",
                "Net-adds-1-yr": "2000",
                "Net-renews-1-yr": "1000",
                "Transfer-gaining-successful": "100",
                "Transfer-losing-successful": "80",
                "Deleted-domains-grace": "40",
                "Deleted-domains-nograce": "20"
            }
        ],
        "net-transactions-202401-en.csv": [
            {
                "TLD": "NET",
                "Registrar-name": "Example Registrar",
                "IANA-ID": "123",
                "Total-domains": "50000",
                "Total-Nameservers": "300",
                "Net-adds-1-yr": "500",
                "Net-renews-1-yr": "300",
                "Transfer-gaining-successful": "25",
                "Transfer-losing-successful": "15",
                "Deleted-domains-grace": "10",
                "Deleted-domains-nograce": "5"
            }
        ]
    }
    
    # Create a temporary directory for the reports
    context.temp_dir = tempfile.TemporaryDirectory()
    context.report_generator = ReportGenerator(data_dir=context.temp_dir.name)


@when('I generate a registrar summary report')
def step_generate_registrar_summary(context):
    """Generate a registrar summary report from the processed data."""
    context.registrar_summary = context.report_generator.generate_summary_by_registrar(context.processed_data)


@when('I generate a TLD summary report')
def step_generate_tld_summary(context):
    """Generate a TLD summary report from the processed data."""
    context.tld_summary = context.report_generator.generate_summary_by_tld(context.processed_data)


@then('the report should group data by registrar')
def step_check_data_grouped_by_registrar(context):
    """Check that the report groups data by registrar."""
    assert context.registrar_summary is not None, "Registrar summary is None"
    
    # Check that we have entries for both registrars
    assert "Example Registrar (IANA ID: 123)" in context.registrar_summary, "Example Registrar not in summary"
    assert "Another Registrar (IANA ID: 456)" in context.registrar_summary, "Another Registrar not in summary"
    
    # Check that each registrar has the correct data structure
    example_reg = context.registrar_summary["Example Registrar (IANA ID: 123)"]
    assert example_reg["name"] == "Example Registrar", "Incorrect registrar name"
    assert example_reg["iana_id"] == "123", "Incorrect IANA ID"
    assert "tlds" in example_reg, "Missing TLDs section for Example Registrar"


@then('each registrar should have information organized by TLD')
def step_check_registrar_info_by_tld(context):
    """Check that each registrar's info is organized by TLD."""
    example_reg = context.registrar_summary["Example Registrar (IANA ID: 123)"]
    
    # Should have both COM and NET for Example Registrar
    assert "COM" in example_reg["tlds"], "COM TLD missing for Example Registrar"
    assert "NET" in example_reg["tlds"], "NET TLD missing for Example Registrar"
    
    # Another Registrar should only have COM
    another_reg = context.registrar_summary["Another Registrar (IANA ID: 456)"]
    assert "COM" in another_reg["tlds"], "COM TLD missing for Another Registrar"
    assert "NET" not in another_reg["tlds"], "NET TLD incorrectly present for Another Registrar"


@then('each TLD should have domain statistics')
def step_check_tld_domain_stats(context):
    """Check that each TLD has domain statistics."""
    example_reg = context.registrar_summary["Example Registrar (IANA ID: 123)"]
    
    # Check COM stats for Example Registrar
    com_stats = example_reg["tlds"]["COM"]
    assert "total_domains" in com_stats, "Missing total_domains for COM"
    assert "total_nameservers" in com_stats, "Missing total_nameservers for COM"
    assert "new_additions" in com_stats, "Missing new_additions for COM"
    assert "renewals" in com_stats, "Missing renewals for COM"
    assert "transfers_in" in com_stats, "Missing transfers_in for COM"
    assert "transfers_out" in com_stats, "Missing transfers_out for COM"
    assert "deletions" in com_stats, "Missing deletions for COM"
    
    # Check specific values from test data
    assert com_stats["total_domains"] == 100000, "Incorrect total_domains value"
    assert com_stats["new_additions"] == 1000, "Incorrect new_additions value"
    assert com_stats["renewals"] == 500, "Incorrect renewals value"
    assert com_stats["transfers_in"] == 50, "Incorrect transfers_in value"
    assert com_stats["transfers_out"] == 30, "Incorrect transfers_out value"
    assert com_stats["deletions"] == 30, "Incorrect deletions value"


@then('the report should group data by TLD')
def step_check_data_grouped_by_tld(context):
    """Check that the report groups data by TLD."""
    assert context.tld_summary is not None, "TLD summary is None"
    
    # Check that we have entries for both TLDs
    assert "COM" in context.tld_summary, "COM TLD not in summary"
    assert "NET" in context.tld_summary, "NET TLD not in summary"


@then('each TLD should have aggregated domain statistics')
def step_check_tld_aggregated_stats(context):
    """Check that each TLD has aggregated domain statistics."""
    com_stats = context.tld_summary["COM"]
    
    assert "total_domains" in com_stats, "Missing total_domains for COM"
    assert "new_additions" in com_stats, "Missing new_additions for COM"
    assert "renewals" in com_stats, "Missing renewals for COM"
    assert "transfers" in com_stats, "Missing transfers for COM"
    assert "deletions" in com_stats, "Missing deletions for COM"


@then('each TLD should show registrar counts')
def step_check_tld_registrar_counts(context):
    """Check that each TLD shows registrar counts."""
    com_stats = context.tld_summary["COM"]
    net_stats = context.tld_summary["NET"]
    
    assert "registrars" in com_stats, "Missing registrars count for COM"
    assert "registrars" in net_stats, "Missing registrars count for NET"
    
    assert com_stats["registrars"] == 2, f"Expected 2 registrars for COM, got {com_stats['registrars']}"
    assert net_stats["registrars"] == 1, f"Expected 1 registrar for NET, got {net_stats['registrars']}"


@then('monthly data should be included when available')
def step_check_monthly_data(context):
    """Check that monthly data is included when available."""
    com_stats = context.tld_summary["COM"]
    
    assert "monthly_data" in com_stats, "Missing monthly_data for COM"
    assert "202401" in com_stats["monthly_data"], "Missing data for January 2024"
    
    jan_data = com_stats["monthly_data"]["202401"]
    assert "total_domains" in jan_data, "Missing total_domains in monthly data"
    assert "new_additions" in jan_data, "Missing new_additions in monthly data"
    assert "renewals" in jan_data, "Missing renewals in monthly data"
    assert "transfers" in jan_data, "Missing transfers in monthly data"
    assert "deletions" in jan_data, "Missing deletions in monthly data"


@given('I have generated report data')
def step_have_generated_report_data(context):
    """Create sample report data for saving."""
    # Reuse the context from the earlier step
    step_have_processed_data(context)
    
    # Generate sample reports
    context.registrar_summary = context.report_generator.generate_summary_by_registrar(context.processed_data)
    context.tld_summary = context.report_generator.generate_summary_by_tld(context.processed_data)
    
    context.report_data = {
        "registrar_summary": context.registrar_summary,
        "tld_summary": context.tld_summary
    }


@when('I save the report data')
def step_save_report_data(context):
    """Save the report data to files."""
    context.saved_reports = {}
    
    for report_name, report_data in context.report_data.items():
        context.saved_reports[report_name] = context.report_generator.save_report(
            report_data, report_name
        )


@then('JSON files should be created in the reports directory')
def step_check_json_files_created(context):
    """Check that JSON files were created in the reports directory."""
    reports_dir = os.path.join(context.temp_dir.name, "reports")
    
    assert os.path.exists(reports_dir), "Reports directory does not exist"
    assert os.path.isfile(os.path.join(reports_dir, "registrar_summary.json")), "registrar_summary.json not created"
    assert os.path.isfile(os.path.join(reports_dir, "tld_summary.json")), "tld_summary.json not created"


@then('the JSON files should contain the correct data structure')
def step_check_json_file_structure(context):
    """Check that the JSON files contain the correct data structure."""
    for report_name, report_path in context.saved_reports.items():
        assert os.path.exists(report_path), f"Report file {report_path} does not exist"
        
        with open(report_path, 'r') as f:
            data = json.load(f)
            
        if report_name == "registrar_summary":
            assert "Example Registrar (IANA ID: 123)" in data, "Missing Example Registrar in saved data"
            assert "COM" in data["Example Registrar (IANA ID: 123)"]["tlds"], "Missing COM TLD in saved data"
        elif report_name == "tld_summary":
            assert "COM" in data, "Missing COM TLD in saved data"
            assert "monthly_data" in data["COM"], "Missing monthly_data in saved data"


# Clean up temporary files in after_scenario hook
def after_scenario(context, scenario):
    """Clean up any temporary files created during testing."""
    if hasattr(context, 'temp_dir'):
        context.temp_dir.cleanup()