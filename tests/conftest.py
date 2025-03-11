import os
import shutil
import tempfile
import pytest
from behave.runner import Context

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing."""
    return (
        "TLD,Registrar-name,IANA-ID,Total-domains,Total-Nameservers,Net-adds-1-yr\n"
        "COM,Example Registrar Inc.,123,100000,500,1000\n"
        "COM,Another Registrar LLC,456,50000,250,500\n"
    )

@pytest.fixture
def sample_csv_data_nonstandard():
    """Sample CSV data with non-standard headers for testing."""
    return (
        "tld,registrar,iana_id,domains,nameservers,additions_1yr\n"
        "COM,Example Registrar Inc.,123,100000,500,1000\n"
        "COM,Another Registrar LLC,456,50000,250,500\n"
    )

@pytest.fixture
def sample_csv_missing_tld():
    """Sample CSV data missing TLD field."""
    return (
        "Registrar-name,IANA-ID,Total-domains,Total-Nameservers,Net-adds-1-yr\n"
        "Example Registrar Inc.,123,100000,500,1000\n"
        "Another Registrar LLC,456,50000,250,500\n"
    )

@pytest.fixture
def behave_context():
    """Create a behave context for testing."""
    return Context(runner=None)