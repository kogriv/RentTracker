"""
Payment period model
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class PaymentPeriod:
    """
    Represents a payment period extracted from bank statement
    """
    start_date: date
    end_date: date
    source_text: str
    
    def __post_init__(self):
        """Validate payment period"""
        if self.start_date > self.end_date:
            raise ValueError(f"Start date {self.start_date} cannot be after end date {self.end_date}")
    
    @property
    def duration_days(self) -> int:
        """Calculate duration in days"""
        return (self.end_date - self.start_date).days + 1
    
    @property
    def target_month(self) -> date:
        """Get the target month for payment analysis (typically start month)"""
        return date(self.start_date.year, self.start_date.month, 1)
    
    def contains_date(self, check_date: date) -> bool:
        """Check if a date falls within this period"""
        return self.start_date <= check_date <= self.end_date
    
    def __str__(self) -> str:
        return f"Period from {self.start_date} to {self.end_date}"