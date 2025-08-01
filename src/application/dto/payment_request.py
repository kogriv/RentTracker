"""
Data Transfer Objects for payment processing requests
"""

from dataclasses import dataclass
from pathlib import Path
from datetime import date
from typing import Optional


@dataclass
class PaymentProcessRequest:
    """
    Request object for payment processing use case
    """
    garage_file: Path
    statement_file: Path
    analysis_date: date
    output_path: Optional[Path] = None
    parser_config: Optional[dict] = None
    
    def __post_init__(self):
        """Validate request data"""
        if not self.garage_file.exists():
            raise FileNotFoundError(f"Garage file not found: {self.garage_file}")
        
        if not self.statement_file.exists():
            raise FileNotFoundError(f"Statement file not found: {self.statement_file}")
        
        # Ensure paths are Path objects
        if isinstance(self.garage_file, str):
            self.garage_file = Path(self.garage_file)
        
        if isinstance(self.statement_file, str):
            self.statement_file = Path(self.statement_file)
        
        if self.output_path and isinstance(self.output_path, str):
            self.output_path = Path(self.output_path)
