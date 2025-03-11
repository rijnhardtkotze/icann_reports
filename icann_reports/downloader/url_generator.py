from datetime import datetime, timedelta
from typing import Dict, List, Any

from config import BASE_URL


class URLGenerator:
    """Generates URLs for ICANN reports based on TLD configurations."""
    
    def __init__(self, base_url: str = BASE_URL):
        """Initialize URL generator.
        
        Args:
            base_url: Base URL template for reports
        """
        self.base_url = base_url
        
    def generate_tld_urls(self, tlds: List[Dict[str, Any]]) -> List[str]:
        """Generate URLs for TLD data based on date ranges.
        
        Args:
            tlds: List of dictionaries with 'base_url', 'start_date', and 'end_date'
                 Each TLD dict should have format:
                 {
                    'base_url': 'https://icann.org/sites/default/files/mrr/{tld}/com-transactions-{date}-en.csv',
                    'start_date': '2019-01',
                    'end_date': '2023-12'
                 }
                 
        Returns:
            List of complete URLs to download
        """
        urls = []
        for tld in tlds:
            start_date = datetime.strptime(tld["start_date"], "%Y-%m")
            end_date = datetime.strptime(tld["end_date"], "%Y-%m")
            
            # Use provided base URL or default
            tld_base_url = tld.get("base_url") or self.base_url
            
            # Set TLD in URL if present
            if "{tld}" in tld_base_url and "tld" in tld:
                tld_base_url = tld_base_url.replace("{tld}", tld["tld"])
                
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime("%Y%m")
                url = tld_base_url.replace("{date}", date_str)
                urls.append(url)
                
                # Move to next month
                current_date += timedelta(days=32)
                current_date = current_date.replace(day=1)
                
        return urls
        
    @staticmethod
    def parse_filename_date(file_name: str) -> str:
        """Extract date from a report filename.
        
        Args:
            file_name: Name of the report file (e.g., "com-transactions-202401-en.csv")
            
        Returns:
            Date string in YYYY-MM format
        """
        # Extract date part from the filename
        parts = file_name.split("-")
        if len(parts) >= 3:
            date_part = parts[2]
            if len(date_part) >= 6:  # Must have at least YYYYMM
                year = date_part[:4]
                month = date_part[4:6]
                return f"{year}-{month}"
        return ""