"""
Transaction domain model
"""

from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class Transaction:
    """
    Represents a bank transaction from statement
    """
    date: date
    amount: Decimal
    category: str
    source: str = "bank_statement"
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate transaction data after initialization"""
        if self.amount <= 0:
            raise ValueError("Transaction amount must be positive")
        
        if not self.category:
            raise ValueError("Transaction category cannot be empty")
    
    @property
    def is_incoming(self) -> bool:
        """Check if transaction is incoming money"""
        return self.amount > 0
    
    def matches_amount(self, target_amount: Decimal, tolerance: Decimal = Decimal('0.01')) -> bool:
        """Check if transaction amount matches target amount within tolerance"""
        return abs(self.amount - target_amount) <= tolerance
    
    def __str__(self) -> str:
        return f"Transaction(date={self.date}, amount={self.amount}, category={self.category})"
