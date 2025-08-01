"""
Domain-specific exceptions
"""


class GarageTrackerException(Exception):
    """Base exception for garage tracker application"""
    pass


class ParseError(GarageTrackerException):
    """Raised when file parsing fails"""
    
    def __init__(self, message: str, filename: str = "", line_number: int = 0):
        self.filename = filename or ""
        self.line_number = line_number or 0
        
        if filename:
            message = f"Error parsing {filename}: {message}"
        if line_number:
            message = f"{message} (line {line_number})"
            
        super().__init__(message)


class ValidationError(GarageTrackerException):
    """Raised when data validation fails"""
    pass


class ConfigurationError(GarageTrackerException):
    """Raised when configuration is invalid"""
    pass


class DataIntegrityError(GarageTrackerException):
    """Raised when data integrity checks fail"""
    
    def __init__(self, message: str, conflicts: list = None):
        self.conflicts = conflicts or []
        super().__init__(message)


class FileProcessingError(GarageTrackerException):
    """Raised when file processing fails"""
    
    def __init__(self, message: str, filename: str = ""):
        self.filename = filename or ""
        if filename:
            message = f"Error processing {filename}: {message}"
        super().__init__(message)
