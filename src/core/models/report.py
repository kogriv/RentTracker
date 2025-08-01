"""
Report domain model
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Dict, Any
from .payment import Payment


@dataclass
class PaymentSummary:
    """Summary statistics for payment report"""
    total_garages: int
    received_count: int
    overdue_count: int
    pending_count: int
    not_due_count: int
    unclear_count: int
    total_expected: float
    total_received: float
    
    @property
    def collection_rate(self) -> float:
        """Calculate payment collection rate as percentage"""
        if self.total_garages == 0:
            return 0.0
        return (self.received_count / self.total_garages) * 100


@dataclass
class PaymentReport:
    """
    Complete payment analysis report
    """
    generated_at: datetime
    analysis_date: date
    garage_file: str
    statement_file: str
    payments: List[Payment]
    summary: PaymentSummary
    notes: List[str]
    
    def __post_init__(self):
        """Validate report data after initialization"""
        if not self.payments:
            raise ValueError("Report must contain at least one payment")
        
        if not self.garage_file or not self.statement_file:
            raise ValueError("Source files must be specified")
    
    @classmethod
    def create(cls, 
               garage_file: str, 
               statement_file: str, 
               payments: List[Payment],
               analysis_date: date = None,
               notes: List[str] = None) -> 'PaymentReport':
        """Create a payment report with calculated summary"""
        
        if analysis_date is None:
            analysis_date = date.today()
        
        if notes is None:
            notes = []
        
        # Calculate summary statistics
        summary = cls._calculate_summary(payments)
        
        return cls(
            generated_at=datetime.now(),
            analysis_date=analysis_date,
            garage_file=garage_file,
            statement_file=statement_file,
            payments=payments,
            summary=summary,
            notes=notes
        )
    
    @staticmethod
    def _calculate_summary(payments: List[Payment]) -> PaymentSummary:
        """Calculate summary statistics from payments"""
        from .payment import PaymentStatus
        
        total_garages = len(payments)
        received_count = sum(1 for p in payments if p.status == PaymentStatus.RECEIVED)
        overdue_count = sum(1 for p in payments if p.status == PaymentStatus.OVERDUE)
        pending_count = sum(1 for p in payments if p.status == PaymentStatus.PENDING)
        not_due_count = sum(1 for p in payments if p.status == PaymentStatus.NOT_DUE)
        unclear_count = sum(1 for p in payments if p.status == PaymentStatus.UNCLEAR)
        
        total_expected = float(sum(p.amount for p in payments))
        total_received = float(sum(p.amount for p in payments if p.status == PaymentStatus.RECEIVED))
        
        return PaymentSummary(
            total_garages=total_garages,
            received_count=received_count,
            overdue_count=overdue_count,
            pending_count=pending_count,
            not_due_count=not_due_count,
            unclear_count=unclear_count,
            total_expected=total_expected,
            total_received=total_received
        )
    
    def get_overdue_payments(self) -> List[Payment]:
        """Get all overdue payments"""
        from .payment import PaymentStatus
        return [p for p in self.payments if p.status == PaymentStatus.OVERDUE]
    
    def get_pending_payments(self) -> List[Payment]:
        """Get all pending payments"""
        from .payment import PaymentStatus
        return [p for p in self.payments if p.status == PaymentStatus.PENDING]
    
    def __str__(self) -> str:
        return f"PaymentReport(garages={self.summary.total_garages}, received={self.summary.received_count})"
