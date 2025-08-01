"""
Application settings and constants
"""

from pathlib import Path
from typing import List, Dict, Any
from enum import Enum


class OutputFormat(Enum):
    """Supported output formats"""
    XLSX = "xlsx"
    CSV = "csv"
    JSON = "json"


class ParserType(Enum):
    """Supported parser types"""
    EXCEL = "excel"
    SBERBANK_EXCEL = "sberbank_excel"
    LLM = "llm"  # For future implementation


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Settings:
    """
    Application settings and constants
    """
    
    # Application info
    APP_NAME = "Garage Payment Tracker"
    APP_VERSION = "1.0.0"
    
    # File paths
    CONFIG_DIR = Path("config")
    OUTPUT_DIR = Path("output")
    LOG_DIR = Path("logs")
    
    # Default configuration files
    DEFAULT_CONFIG_FILE = CONFIG_DIR / "default_config.yaml"
    PARSER_RULES_FILE = CONFIG_DIR / "parser_rules.yaml"
    
    # Localization
    LOCALIZATION_DIR = Path("src/infrastructure/localization")
    DEFAULT_LANGUAGE = "en"
    SUPPORTED_LANGUAGES = ["en", "ru"]
    
    # Parsing defaults
    DEFAULT_GRACE_PERIOD_DAYS = 3
    DEFAULT_SEARCH_WINDOW_DAYS = 7
    DEFAULT_AMOUNT_TOLERANCE = 0.01
    
    # File formats
    SUPPORTED_EXCEL_FORMATS = [".xlsx", ".xls"]
    SUPPORTED_OUTPUT_FORMATS = [OutputFormat.XLSX, OutputFormat.CSV, OutputFormat.JSON]
    
    # Date formats for parsing
    SUPPORTED_DATE_FORMATS = [
        "%d.%m.%Y",    # DD.MM.YYYY
        "%d/%m/%Y",    # DD/MM/YYYY  
        "%Y-%m-%d",    # YYYY-MM-DD
        "%d-%m-%Y",    # DD-MM-YYYY
        "%m/%d/%Y"     # MM/DD/YYYY
    ]
    
    # Excel-specific settings
    EXCEL_MAX_COLUMN_WIDTH = 50
    EXCEL_DEFAULT_FONT = "Calibri"
    EXCEL_HEADER_COLOR = "CCCCCC"
    
    # Status colors for Excel reports
    STATUS_COLORS = {
        "received": "90EE90",   # Light green
        "overdue": "FFB6C1",    # Light red
        "pending": "FFFFE0",    # Light yellow
        "not_due": "E6E6FA",    # Light purple
        "unclear": "FFA500"     # Orange
    }
    
    # Logging configuration
    DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DEFAULT_LOG_LEVEL = LogLevel.INFO
    LOG_FILE_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT = 5
    
    @classmethod
    def get_config_paths(cls) -> List[Path]:
        """Get list of configuration file search paths"""
        return [
            cls.DEFAULT_CONFIG_FILE,
            Path("./config.yaml"),
            Path("./default_config.yaml"),
            Path.home() / ".garage-tracker" / "config.yaml"
        ]
    
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist"""
        directories = [cls.CONFIG_DIR, cls.OUTPUT_DIR, cls.LOG_DIR]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_output_filename(cls, base_name: str, format_type: OutputFormat = OutputFormat.XLSX) -> str:
        """
        Generate output filename with timestamp
        
        Args:
            base_name: Base name for file
            format_type: Output format
            
        Returns:
            Formatted filename with timestamp
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}.{format_type.value}"
