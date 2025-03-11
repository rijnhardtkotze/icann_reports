import json
import os
import time
from typing import Dict, Any, Optional

from config import CACHE_FILE
from icann_reports.utils.logging_setup import setup_logging

logger = setup_logging(logger_name="cache")


class CacheManager:
    """Manages caching of processed files and other persistent data."""
    
    def __init__(self, cache_file: str = CACHE_FILE):
        """Initialize the cache manager.
        
        Args:
            cache_file: Path to the cache file
        """
        self.cache_file = cache_file
        self.cache_data = self._load_cache()
        
    def _load_cache(self) -> Dict[str, Any]:
        """Load processing cache from disk.
        
        Returns:
            Dictionary containing cached data
        """
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            return {}
        
    def save_cache(self) -> bool:
        """Save processing cache to disk.
        
        Returns:
            True if save was successful, False otherwise
        """
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache_data, f)
            return True
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
            return False
            
    def add_processed_file(self, file_name: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a file to the processed files cache.
        
        Args:
            file_name: Name of the processed file
            metadata: Additional metadata to store with the file record
        """
        if "processed_files" not in self.cache_data:
            self.cache_data["processed_files"] = {}
            
        self.cache_data["processed_files"][file_name] = {
            "timestamp": time.time(),
            **(metadata or {})
        }
        self.save_cache()
        
    def is_file_processed(self, file_name: str) -> bool:
        """Check if a file has been processed.
        
        Args:
            file_name: Name of the file to check
            
        Returns:
            True if the file has been processed, False otherwise
        """
        return (
            "processed_files" in self.cache_data 
            and file_name in self.cache_data["processed_files"]
        )
        
    def get_processed_file_metadata(self, file_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a processed file.
        
        Args:
            file_name: Name of the file
            
        Returns:
            Metadata dictionary if file exists in cache, None otherwise
        """
        if self.is_file_processed(file_name):
            return self.cache_data["processed_files"][file_name]
        return None
        
    def store_data(self, key: str, data: Any) -> None:
        """Store arbitrary data in the cache.
        
        Args:
            key: Key to store the data under
            data: Data to store (must be JSON serializable)
        """
        self.cache_data[key] = data
        self.save_cache()
        
    def get_data(self, key: str) -> Optional[Any]:
        """Retrieve data from the cache.
        
        Args:
            key: Key to retrieve
            
        Returns:
            The stored data if present, None otherwise
        """
        return self.cache_data.get(key)