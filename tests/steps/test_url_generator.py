import pytest
from behave import given, when, then

from icann_reports.downloader.url_generator import URLGenerator


@pytest.fixture
def url_generator():
    return URLGenerator()


@given('I have a TLD configuration for "{tld}" from "{start_date}" to "{end_date}"')
def step_have_tld_configuration(context, tld, start_date, end_date):
    """Create a TLD configuration with the specified parameters."""
    if not hasattr(context, 'tld_configs'):
        context.tld_configs = []
    
    context.tld_configs.append({
        'tld': tld,
        'base_url': f'https://www.icann.org/sites/default/files/mrr/{tld}/{tld}-transactions-{{date}}-en.csv',
        'start_date': start_date,
        'end_date': end_date,
    })


@when('I generate the URLs')
def step_generate_urls(context):
    """Generate URLs from the TLD configurations."""
    context.url_generator = URLGenerator()
    context.urls = context.url_generator.generate_tld_urls(context.tld_configs)


@then('I should get {count:d} URLs for the "{tld}" TLD')
def step_check_url_count_for_tld(context, count, tld):
    """Check that the correct number of URLs were generated for the specified TLD."""
    tld_urls = [url for url in context.urls if f'/{tld}/' in url]
    assert len(tld_urls) == count, f"Expected {count} URLs for {tld}, got {len(tld_urls)}"


@then('I should get {count:d} URLs for the specified TLDs')
def step_check_total_url_count(context, count):
    """Check that the correct total number of URLs were generated."""
    assert len(context.urls) == count, f"Expected {count} URLs, got {len(context.urls)}"


@then('each URL should follow the correct format for ICANN reports')
def step_check_url_format(context):
    """Check that all URLs follow the expected format."""
    for url in context.urls:
        assert url.startswith('https://www.icann.org/sites/default/files/mrr/'), f"URL has incorrect prefix: {url}"
        assert url.endswith('-en.csv'), f"URL has incorrect suffix: {url}"
        assert '-transactions-' in url, f"URL is missing 'transactions' part: {url}"


@then('the URLs should include the months "{month1}", "{month2}", and "{month3}"')
def step_check_months_in_urls(context, month1, month2, month3):
    """Check that the URLs include all specified months."""
    months = [month1, month2, month3]
    for month in months:
        found = False
        for url in context.urls:
            if f'-transactions-{month}-' in url:
                found = True
                break
        assert found, f"No URL found containing month {month}"


@then('{count:d} URLs should be for the "{tld}" TLD')
def step_check_tld_url_count(context, count, tld):
    """Check that the correct number of URLs were generated for the specified TLD."""
    tld_urls = [url for url in context.urls if f'/{tld}/' in url]
    assert len(tld_urls) == count, f"Expected {count} URLs for {tld}, got {len(tld_urls)}"


@given('I have a filename "{filename}"')
def step_have_filename(context, filename):
    """Set a filename for parsing."""
    context.filename = filename


@when('I parse the date from the filename')
def step_parse_date_from_filename(context):
    """Parse the date from the filename."""
    context.url_generator = URLGenerator()
    context.parsed_date = context.url_generator.parse_filename_date(context.filename)


@then('I should get the date "{expected_date}"')
def step_check_parsed_date(context, expected_date):
    """Check that the parsed date matches the expected date."""
    assert context.parsed_date == expected_date, f"Expected date {expected_date}, got {context.parsed_date}"