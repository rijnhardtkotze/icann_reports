import logging
import os
from typing import List, Optional

from config import LOG_DIR


def setup_logging(
    logger_name: str = "icann_downloader",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    handlers: Optional[List[logging.Handler]] = None,
) -> logging.Logger:
    """Configure and return a logger with appropriate handlers.

    Args:
        logger_name: Name of the logger
        level: Logging level
        log_file: Name of the log file (if not provided, defaults to logger_name.log)
        handlers: List of custom handlers to add to the logger

    Returns:
        Configured logger
    """
    if log_file is None:
        log_file = f"{logger_name}.log"

    # Create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create default handlers if none provided
    if handlers is None:
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # Create file handler
        file_handler = logging.FileHandler(os.path.join(LOG_DIR, log_file))
        file_handler.setLevel(level)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    else:
        # Add provided handlers
        for handler in handlers:
            logger.addHandler(handler)

    return logger