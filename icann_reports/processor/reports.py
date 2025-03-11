import json
import os
from typing import Dict, List, Any, Optional

from config import DATA_DIR
from icann_reports.utils.logging_setup import setup_logging

logger = setup_logging(logger_name="reports")


class ReportGenerator:
    """Generates reports and summaries from processed ICANN data."""

    def __init__(self, data_dir: str = DATA_DIR):
        """Initialize the report generator.

        Args:
            data_dir: Directory to store generated reports
        """
        self.data_dir = data_dir
        self.reports_dir = os.path.join(data_dir, "reports")
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_summary_by_registrar(self, data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Generate a summary of domain data grouped by registrar.

        Args:
            data: Dictionary with file names as keys and lists of row dictionaries as values

        Returns:
            Dictionary with registrar summaries
        """
        registrar_summary = {}
        
        for file_name, rows in data.items():
            for row in rows:
                # Get registrar info
                registrar_name = row.get("Registrar-name", "Unknown")
                iana_id = row.get("IANA-ID", "Unknown")
                tld = row.get("TLD", "Unknown").upper()
                
                # Create registrar key
                registrar_key = f"{registrar_name} (IANA ID: {iana_id})"
                
                if registrar_key not in registrar_summary:
                    registrar_summary[registrar_key] = {
                        "name": registrar_name,
                        "iana_id": iana_id,
                        "tlds": {},
                    }
                    
                # Ensure TLD entry exists
                if tld not in registrar_summary[registrar_key]["tlds"]:
                    registrar_summary[registrar_key]["tlds"][tld] = {
                        "total_domains": 0,
                        "total_nameservers": 0,
                        "new_additions": 0,
                        "renewals": 0,
                        "transfers_in": 0,
                        "transfers_out": 0,
                        "deletions": 0,
                    }
                    
                # Update TLD stats
                tld_stats = registrar_summary[registrar_key]["tlds"][tld]
                
                # Extract numeric values with fallback to 0 for empty or non-numeric values
                def get_numeric(field_name: str) -> int:
                    try:
                        value = row.get(field_name, "0").strip()
                        return int(value) if value else 0
                    except (ValueError, TypeError):
                        return 0
                
                # Add values to summary
                tld_stats["total_domains"] = get_numeric("Total-domains")
                tld_stats["total_nameservers"] = get_numeric("Total-Nameservers")
                
                # Sum all additions
                tld_stats["new_additions"] = sum(
                    get_numeric(f"Net-adds-{year}-yr")
                    for year in range(1, 11)
                )
                
                # Sum all renewals
                tld_stats["renewals"] = sum(
                    get_numeric(f"Net-renews-{year}-yr")
                    for year in range(1, 11)
                )
                
                # Transfers
                tld_stats["transfers_in"] = get_numeric("Transfer-gaining-successful")
                tld_stats["transfers_out"] = get_numeric("Transfer-losing-successful")
                
                # Deletions
                tld_stats["deletions"] = (
                    get_numeric("Deleted-domains-grace") +
                    get_numeric("Deleted-domains-nograce")
                )
        
        return registrar_summary
    
    def generate_summary_by_tld(self, data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Generate a summary of domain data grouped by TLD.

        Args:
            data: Dictionary with file names as keys and lists of row dictionaries as values

        Returns:
            Dictionary with TLD summaries
        """
        tld_summary = {}
        
        for file_name, rows in data.items():
            for row in rows:
                # Extract TLD
                tld = row.get("TLD", "Unknown").upper()
                
                # Create TLD entry if it doesn't exist
                if tld not in tld_summary:
                    tld_summary[tld] = {
                        "total_domains": 0,
                        "total_nameservers": 0,
                        "registrars": 0,
                        "new_additions": 0,
                        "renewals": 0,
                        "transfers": 0,
                        "deletions": 0,
                    }
                
                # Extract numeric values
                def get_numeric(field_name: str) -> int:
                    try:
                        value = row.get(field_name, "0").strip()
                        return int(value) if value else 0
                    except (ValueError, TypeError):
                        return 0
                
                # Update registrar count (unique IANA IDs)
                if "registrar_ids" not in tld_summary[tld]:
                    tld_summary[tld]["registrar_ids"] = set()
                
                iana_id = row.get("IANA-ID")
                if iana_id:
                    tld_summary[tld]["registrar_ids"].add(iana_id)
                    tld_summary[tld]["registrars"] = len(tld_summary[tld]["registrar_ids"])
                
                # Add values to summary (only for current file to avoid double counting)
                file_date = file_name.split("-")[2][:6] if len(file_name.split("-")) > 2 else ""
                
                # Store data by month if we have a date
                if file_date and len(file_date) == 6:
                    if "monthly_data" not in tld_summary[tld]:
                        tld_summary[tld]["monthly_data"] = {}
                        
                    if file_date not in tld_summary[tld]["monthly_data"]:
                        tld_summary[tld]["monthly_data"][file_date] = {
                            "total_domains": 0,
                            "new_additions": 0,
                            "renewals": 0,
                            "transfers": 0,
                            "deletions": 0,
                        }
                    
                    # Add to monthly totals
                    month_data = tld_summary[tld]["monthly_data"][file_date]
                    month_data["total_domains"] += get_numeric("Total-domains")
                    
                    month_data["new_additions"] += sum(
                        get_numeric(f"Net-adds-{year}-yr")
                        for year in range(1, 11)
                    )
                    
                    month_data["renewals"] += sum(
                        get_numeric(f"Net-renews-{year}-yr")
                        for year in range(1, 11)
                    )
                    
                    month_data["transfers"] += get_numeric("Transfer-gaining-successful")
                    
                    month_data["deletions"] += (
                        get_numeric("Deleted-domains-grace") +
                        get_numeric("Deleted-domains-nograce")
                    )
                    
                # Update overall totals with the most recent data
                if "monthly_data" in tld_summary[tld]:
                    # Sort months in descending order
                    months = sorted(tld_summary[tld]["monthly_data"].keys(), reverse=True)
                    if months:
                        latest_month = months[0]
                        latest_data = tld_summary[tld]["monthly_data"][latest_month]
                        
                        # Use the latest month's data for overall totals
                        tld_summary[tld]["total_domains"] = latest_data["total_domains"]
                        tld_summary[tld]["new_additions"] = latest_data["new_additions"]
                        tld_summary[tld]["renewals"] = latest_data["renewals"]
                        tld_summary[tld]["transfers"] = latest_data["transfers"]
                        tld_summary[tld]["deletions"] = latest_data["deletions"]
        
        # Remove the set used for counting unique registrars
        for tld in tld_summary:
            if "registrar_ids" in tld_summary[tld]:
                del tld_summary[tld]["registrar_ids"]
                
        return tld_summary
    
    def save_report(self, data: Dict[str, Any], report_name: str) -> str:
        """Save report data to a JSON file.

        Args:
            data: Report data to save
            report_name: Name for the report file (without extension)

        Returns:
            Path to the saved report file
        """
        report_path = os.path.join(self.reports_dir, f"{report_name}.json")
        
        try:
            with open(report_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Report saved to {report_path}")
            return report_path
        except Exception as e:
            logger.error(f"Error saving report to {report_path}: {e}")
            return ""
            
    def generate_all_reports(self, data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, str]:
        """Generate and save all reports.

        Args:
            data: Dictionary with file names as keys and lists of row dictionaries as values

        Returns:
            Dictionary with report names as keys and file paths as values
        """
        reports = {}
        
        # Generate registrar summary
        registrar_summary = self.generate_summary_by_registrar(data)
        reports["registrar_summary"] = self.save_report(
            registrar_summary, "registrar_summary"
        )
        
        # Generate TLD summary
        tld_summary = self.generate_summary_by_tld(data)
        reports["tld_summary"] = self.save_report(
            tld_summary, "tld_summary"
        )
        
        return reports