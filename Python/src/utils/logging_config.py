"""
Logging configuration for the infrastructure automation tool.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional

def setup_logging(
    log_file: str = "infra_automation.log",
    log_level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """Configure logging for the application.
    
    Args:
        log_file: Path to the log file
        log_level: Logging level
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Create handlers
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(file_formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set specific log levels for third-party libraries
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

class LoggingContextManager:
    """Context manager for logging operations with timing."""
    
    def __init__(self, logger: logging.Logger, operation: str):
        """Initialize the logging context manager.
        
        Args:
            logger: Logger instance
            operation: Name of the operation being logged
        """
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self) -> 'LoggingContextManager':
        """Enter the context and log the start of the operation."""
        self.start_time = logging.time.time()
        self.logger.info(f"Starting {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context and log the completion or failure of the operation."""
        duration = logging.time.time() - self.start_time
        
        if exc_type is None:
            self.logger.info(
                f"Completed {self.operation} in {duration:.2f} seconds"
            )
        else:
            self.logger.error(
                f"Failed {self.operation} after {duration:.2f} seconds",
                exc_info=(exc_type, exc_val, exc_tb)
            )

def log_sensitive_data(logger: logging.Logger, data: str) -> str:
    """Log sensitive data with masking.
    
    Args:
        logger: Logger instance
        data: Sensitive data to log
        
    Returns:
        Masked version of the data
    """
    if not data:
        return ""
    
    # Mask all but last 4 characters
    masked = '*' * (len(data) - 4) + data[-4:]
    logger.debug(f"Masked sensitive data: {masked}")
    return masked 