import os
from typing import Dict

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "processed_files.json")
LOG_DIR = os.path.join(DATA_DIR, "logs")

# Network settings
DOWNLOAD_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Processing settings
MAX_WORKERS = 12
CUTOFF_FILE = "com-transactions-201003-en.csv"

# Base URL for reports
BASE_URL = "https://www.icann.org/sites/default/files/mrr/{tld}/{tld}-transactions-{date}-en.csv"

# Expected field names and their descriptions for validation
EXPECTED_FIELDS: Dict[str, str] = {
    "TLD": "Identifies whether data is for COM or NET",
    "Registrar-name": "Registrar's Full Corporate Name",
    "IANA-ID": "IANA Registrar ID",
    "Total-domains": "Total domains under sponsorship",
    "Total-Nameservers": "Total Nameservers Registered",
    "Net-adds-1-yr": "Domains successfully added with 1-year term",
    "Net-adds-2-yr": "Domains successfully added with 2-year term",
    "Net-adds-3-yr": "Domains successfully added with 3-year term",
    "Net-adds-4-yr": "Domains successfully added with 4-year term",
    "Net-adds-5-yr": "Domains successfully added with 5-year term",
    "Net-adds-6-yr": "Domains successfully added with 6-year term",
    "Net-adds-7-yr": "Domains successfully added with 7-year term",
    "Net-adds-8-yr": "Domains successfully added with 8-year term",
    "Net-adds-9-yr": "Domains successfully added with 9-year term",
    "Net-adds-10-yr": "Domains successfully added with 10-year term",
    "Net-renews-1-yr": "Domains renewed with 1-year term",
    "Net-renews-2-yr": "Domains renewed with 2-year term",
    "Net-renews-3-yr": "Domains renewed with 3-year term",
    "Net-renews-4-yr": "Domains renewed with 4-year term",
    "Net-renews-5-yr": "Domains renewed with 5-year term",
    "Net-renews-6-yr": "Domains renewed with 6-year term",
    "Net-renews-7-yr": "Domains renewed with 7-year term",
    "Net-renews-8-yr": "Domains renewed with 8-year term",
    "Net-renews-9-yr": "Domains renewed with 9-year term",
    "Net-renews-10-yr": "Domains renewed with 10-year term",
    "Transfer-gaining-successful": "Transfers initiated and accepted by other registrar",
    "Transfer-gaining-nacked": "Transfers initiated and rejected by other registrar",
    "Transfer-losing-successful": "Transfers initiated by others and accepted by this registrar",
    "Transfer-losing-nacked": "Transfers initiated by others and rejected by this registrar",
    "Transfer-disputed-won": "Transfer disputes won",
    "Transfer-disputed-lost": "Transfer disputes lost",
    "Transfer-disputed-nodecision": "Transfer disputes with split or no decision",
    "Deleted-domains-grace": "Domains deleted within add grace period",
    "Deleted-domains-nograce": "Domains deleted outside add grace period",
    "Restored-domains": "Domain names restored from redemption period",
    "Restored-noreport": "Restored names without a registrar report submission",
}

# Known header patterns to identify in files
HEADER_PATTERNS = [
    "ICANN Monthly Consolidated Data Report",
    "<TLD>,<registrar-name>,<iana-id>",
]

# Create necessary directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)