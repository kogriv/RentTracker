"""
Logging configuration for the application
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import sys


def setup_logging(log_level: str = "INFO", 
                 log_file: Optional[Path] = None,
                 log_format: Optional[str] = None,
                 console_level: str = "ERROR") -> None:
    """
    Setup application logging configuration
    
    Args:
        log_level: Logging level for file (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file (optional)
        log_format: Custom log format string (optional)
        console_level: Logging level for console (default: ERROR - only errors shown)
    """
    
    # Default log format
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure root logger
    root_logger = logging.getLogger()
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set log level (most permissive to capture everything)
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(logging.DEBUG)  # Capture everything at root level
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Console handler - only show errors and warnings by default
    console_numeric_level = getattr(logging, console_level.upper(), logging.ERROR)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler - log everything to file
    if log_file:
        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Reduce noise from external libraries
    logging.getLogger('openpyxl').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    logging.info("Logging configuration initialized - console shows only %s+ messages", console_level)


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance with specified name
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerMixin:
    """
    Mixin class to add logging capability to classes
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")


def log_function_call(func):
    """
    Decorator to log function calls
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Function {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Function {func.__name__} failed with error: {e}")
            raise
    
    return wrapper
