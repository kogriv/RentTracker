"""
Garage domain model
"""

from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class Garage:
    """
    Represents a garage rental unit with its payment details
    """
    id: str
    monthly_rent: Decimal
    start_date: date
    payment_day: int
    
    def __post_init__(self):
        """Validate garage data after initialization"""
        if not self.id:
            raise ValueError("Garage ID cannot be empty")
        
        if self.monthly_rent <= 0:
            raise ValueError("Monthly rent must be positive")
        
        if not (1 <= self.payment_day <= 31):
            raise ValueError("Payment day must be between 1 and 31")
    
    @property
    def display_name(self) -> str:
        """Human-readable garage identifier"""
        return f"Garage #{self.id}"
    
    def __str__(self) -> str:
        return f"Garage(id={self.id}, rent={self.monthly_rent}, day={self.payment_day})"
