#!/usr/bin/env python3
"""
ICANN Reports Downloader - Main Module

This script downloads and processes ICANN transaction reports for domain registrars,
normalizes field names, and generates summary reports.
"""

import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any

from config import MAX_WORKERS, BASE_URL
from icann_reports.downloader.url_generator import URLGenerator
from icann_reports.downloader.csv_downloader import CSVDownloader
from icann_reports.processor.csv_processor import CSVProcessor
from icann_reports.processor.field_validation import FieldValidator
from icann_reports.processor.reports import ReportGenerator
from icann_reports.utils.logging_setup import setup_logging


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Download and process ICANN registrar transaction reports."
    )
    parser.add_argument(
        "--tld", type=str, default="com",
        help="TLD to process (default: com)"
    )
    parser.add_argument(
        "--start-date", type=str, default="2024-01",
        help="Start date in YYYY-MM format (default: 2024-01)"
    )
    parser.add_argument(
        "--end-date", type=str, default="2024-11",
        help="End date in YYYY-MM format (default: 2024-11)"
    )
    parser.add_argument(
        "--max-workers", type=int, default=MAX_WORKERS,
        help=f"Maximum number of worker threads (default: {MAX_WORKERS})"
    )
    parser.add_argument(
        "--validate", action="store_true",
        help="Validate the data after processing"
    )
    parser.add_argument(
        "--generate-reports", action="store_true",
        help="Generate summary reports after processing"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()


def download_and_process_csv_files(
    urls: List[str], 
    max_workers: int
) -> Dict[str, List[Dict[str, Any]]]:
    """Download and process CSV files concurrently.

    Args:
        urls: List of URLs to download
        max_workers: Maximum number of concurrent workers

    Returns:
        Dictionary with file names as keys and processed data as values
    """
    consolidated_data = {}
    csv_downloader = CSVDownloader()
    csv_processor = CSVProcessor()
    
    # Download files concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(csv_downloader.download_csv, url): url for url in urls
        }
        file_infos = []

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                file_info = future.result()
                if file_info[0]:  # If file_path is not None
                    file_infos.append(file_info)
            except Exception as e:
                logger.error(f"Exception for {url}: {e}")

        # Process files concurrently
        futures = [
            executor.submit(csv_processor.process_csv, file_info) for file_info in file_infos
        ]

        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    consolidated_data.update(result)
            except Exception as e:
                logger.error(f"Processing error: {e}")

    return consolidated_data


def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    global logger
    logger = setup_logging(level=log_level)
    
    logger.info("Starting ICANN Reports Downloader")
    
    # Configure TLD and date range
    tlds = [
        {
            "tld": args.tld,
            "base_url": BASE_URL,
            "start_date": args.start_date,
            "end_date": args.end_date,
        }
    ]
    
    # Generate URLs
    url_generator = URLGenerator()
    urls = url_generator.generate_tld_urls(tlds)
    logger.info(f"Generated {len(urls)} URLs for downloading")
    
    # Download and process files
    data = download_and_process_csv_files(urls, args.max_workers)
    logger.info(f"Processed {len(data)} files")
    
    # Validate data if requested
    if args.validate:
        field_validator = FieldValidator()
        validation_results = field_validator.validate_data(data)
        validation_report = field_validator.get_validation_report(validation_results)
        print("\n" + validation_report)
    
    # Generate reports if requested
    if args.generate_reports:
        report_generator = ReportGenerator()
        reports = report_generator.generate_all_reports(data)
        logger.info(f"Generated reports: {', '.join(reports.keys())}")
        
        # Print report file paths
        print("\nGenerated Reports:")
        for report_name, report_path in reports.items():
            print(f"  - {report_name}: {report_path}")


if __name__ == "__main__":
    main()
