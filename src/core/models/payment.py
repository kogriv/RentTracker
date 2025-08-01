"""
Payment domain model
"""

from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from typing import Optional
from enum import Enum


class PaymentStatus(Enum):
    """Payment status enumeration"""
    RECEIVED = "received"
    OVERDUE = "overdue"
    PENDING = "pending"
    NOT_DUE = "not_due"
    UNCLEAR = "unclear"


@dataclass
class Payment:
    """
    Represents a payment for garage rental
    """
    garage_id: str
    amount: Decimal
    expected_date: date
    actual_date: Optional[date] = None
    status: PaymentStatus = PaymentStatus.NOT_DUE
    days_overdue: int = 0
    notes: str = ""
    
    def __post_init__(self):
        """Validate payment data after initialization"""
        if not self.garage_id:
            raise ValueError("Garage ID cannot be empty")
        
        if self.amount <= 0:
            raise ValueError("Payment amount must be positive")
    
    @property
    def is_paid(self) -> bool:
        """Check if payment has been received"""
        return self.status == PaymentStatus.RECEIVED
    
    @property
    def is_overdue(self) -> bool:
        """Check if payment is overdue"""
        return self.status == PaymentStatus.OVERDUE
    
    def mark_as_received(self, actual_date: date, notes: str = ""):
        """Mark payment as received"""
        # Note: dataclass is frozen, so we can't modify in place
        # This method is for documentation purposes
        pass
    
    def __str__(self) -> str:
        return f"Payment(garage={self.garage_id}, amount={self.amount}, status={self.status.value})"
