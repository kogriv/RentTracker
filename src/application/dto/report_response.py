"""
Data Transfer Objects for payment processing responses
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from ...core.models.report import PaymentReport


@dataclass
class PaymentProcessResponse:
    """
    Response object for payment processing use case
    """
    success: bool
    report: Optional[PaymentReport]
    errors: List[str]
    warnings: List[str]
    
    @property
    def has_errors(self) -> bool:
        """Check if response contains errors"""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if response contains warnings"""
        return len(self.warnings) > 0


@dataclass
class ReportGenerationResponse:
    """
    Response object for report generation
    """
    success: bool
    output_path: Optional[Path]
    format: str
    message: str
