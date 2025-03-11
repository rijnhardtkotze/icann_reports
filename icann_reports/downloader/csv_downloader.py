import os
import time
import urllib.request
import urllib.error
from typing import Tuple, Optional

from config import (
    DATA_DIR,
    DOWNLOAD_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
)
from icann_reports.utils.logging_setup import setup_logging
from icann_reports.utils.cache import CacheManager

logger = setup_logging(logger_name="csv_downloader")


class CSVDownloader:
    """Downloads CSV files from ICANN with retry logic."""

    def __init__(
        self,
        data_dir: str = DATA_DIR,
        download_timeout: int = DOWNLOAD_TIMEOUT,
        max_retries: int = MAX_RETRIES,
        retry_delay: int = RETRY_DELAY,
    ):
        """Initialize the CSV downloader.

        Args:
            data_dir: Directory to store downloaded files
            download_timeout: Timeout for downloads in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retry attempts in seconds
        """
        self.data_dir = data_dir
        self.download_timeout = download_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.cache_manager = CacheManager()

    def download_csv(self, url: str, retry_count: int = 0) -> Tuple[Optional[str], bool]:
        """Download a CSV file with retries and timeouts.

        Args:
            url: URL to download
            retry_count: Current retry attempt (used internally)

        Returns:
            Tuple of (file_path, already_processed)
                - file_path: Path to the downloaded file or None if download failed
                - already_processed: True if file was already processed
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        file_name = url.split("/")[-1]
        file_path = os.path.join(self.data_dir, file_name)

        # Skip if file has been processed
        if self.cache_manager.is_file_processed(file_name):
            logger.info(f"Already processed: {file_name}")
            return file_path, True

        # Skip download if file exists
        if os.path.exists(file_path):
            logger.info(f"File exists: {file_path}")
            return file_path, False

        req = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=self.download_timeout) as response:
                if response.status == 200:
                    with open(file_path, "wb") as out_file:
                        out_file.write(response.read())
                    logger.info(f"Downloaded: {file_path}")
                    return file_path, False
                else:
                    raise urllib.error.HTTPError(
                        url, response.status, "Download failed", None, None
                    )
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            if retry_count < self.max_retries:
                logger.warning(
                    f"Error downloading {url}: {e}. Retrying in {self.retry_delay}s..."
                )
                time.sleep(self.retry_delay)
                return self.download_csv(url, retry_count + 1)
            else:
                logger.error(
                    f"Failed to download {url} after {self.max_retries} attempts: {e}"
                )
                return None, False