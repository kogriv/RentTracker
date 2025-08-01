"""
Unit tests for Payment model
"""

import pytest
from decimal import Decimal
from datetime import date

from src.core.models.payment import Payment, PaymentStatus


class TestPayment:
    """Test cases for Payment model"""
    
    def test_payment_creation_minimal(self):
        """Test creating payment with minimal required data"""
        payment = Payment(
            garage_id="1",
            amount=Decimal("3500.00"),
            expected_date=date(2025, 1, 15)
        )
        
        assert payment.garage_id == "1"
        assert payment.amount == Decimal("3500.00")
        assert payment.expected_date == date(2025, 1, 15)
        assert payment.actual_date is None
        assert payment.status == PaymentStatus.NOT_DUE
        assert payment.days_overdue == 0
        assert payment.notes == ""
    
    def test_payment_creation_complete(self):
        """Test creating payment with all data"""
        payment = Payment(
            garage_id="1",
            amount=Decimal("3500.00"),
            expected_date=date(2025, 1, 15),
            actual_date=date(2025, 1, 16),
            status=PaymentStatus.RECEIVED,
            days_overdue=1,
            notes="Payment received with 1 day delay"
        )
        
        assert payment.garage_id == "1"
        assert payment.amount == Decimal("3500.00")
        assert payment.expected_date == date(2025, 1, 15)
        assert payment.actual_date == date(2025, 1, 16)
        assert payment.status == PaymentStatus.RECEIVED
        assert payment.days_overdue == 1
        assert payment.notes == "Payment received with 1 day delay"
    
    def test_payment_validation_empty_garage_id(self):
        """Test validation with empty garage ID"""
        with pytest.raises(ValueError, match="Garage ID cannot be empty"):
            Payment(
                garage_id="",
                amount=Decimal("3500.00"),
                expected_date=date(2025, 1, 15)
            )
    
    def test_payment_validation_negative_amount(self):
        """Test validation with negative amount"""
        with pytest.raises(ValueError, match="Payment amount must be positive"):
            Payment(
                garage_id="1",
                amount=Decimal("-100.00"),
                expected_date=date(2025, 1, 15)
            )
    
    def test_payment_validation_zero_amount(self):
        """Test validation with zero amount"""
        with pytest.raises(ValueError, match="Payment amount must be positive"):
            Payment(
                garage_id="1",
                amount=Decimal("0.00"),
                expected_date=date(2025, 1, 15)
            )
    
    def test_payment_status_properties(self):
        """Test payment status property methods"""
        # Test received payment
        received_payment = Payment(
            garage_id="1",
            amount=Decimal("3500.00"),
            expected_date=date(2025, 1, 15),
            status=PaymentStatus.RECEIVED
        )
        
        assert received_payment.is_paid is True
        assert received_payment.is_overdue is False
        
        # Test overdue payment
        overdue_payment = Payment(
            garage_id="2",
            amount=Decimal("3500.00"),
            expected_date=date(2025, 1, 15),
            status=PaymentStatus.OVERDUE
        )
        
        assert overdue_payment.is_paid is False
        assert overdue_payment.is_overdue is True
        
        # Test pending payment
        pending_payment = Payment(
            garage_id="3",
            amount=Decimal("3500.00"),
            expected_date=date(2025, 1, 15),
            status=PaymentStatus.PENDING
        )
        
        assert pending_payment.is_paid is False
        assert pending_payment.is_overdue is False
    
    def test_payment_status_enum_values(self):
        """Test PaymentStatus enum values"""
        assert PaymentStatus.RECEIVED.value == "received"
        assert PaymentStatus.OVERDUE.value == "overdue"
        assert PaymentStatus.PENDING.value == "pending"
        assert PaymentStatus.NOT_DUE.value == "not_due"
        assert PaymentStatus.UNCLEAR.value == "unclear"
    
    def test_payment_string_representation(self):
        """Test string representation"""
        payment = Payment(
            garage_id="1",
            amount=Decimal("3500.00"),
            expected_date=date(2025, 1, 15),
            status=PaymentStatus.RECEIVED
        )
        
        str_repr = str(payment)
        assert "Payment(" in str_repr
        assert "garage=1" in str_repr
        assert "amount=3500.00" in str_repr
        assert "status=received" in str_repr
    
    def test_payment_with_notes(self):
        """Test payment with various notes"""
        notes_cases = [
            "",
            "Payment matched automatically",
            "Multiple matches found, selected closest date",
            "Amount conflict with garage #6",
            "No matching payment found in statement"
        ]
        
        for note in notes_cases:
            payment = Payment(
                garage_id="1",
                amount=Decimal("3500.00"),
                expected_date=date(2025, 1, 15),
                notes=note
            )
            assert payment.notes == note
    
    def test_payment_different_statuses(self):
        """Test payment with different statuses"""
        base_payment_data = {
            "garage_id": "1",
            "amount": Decimal("3500.00"),
            "expected_date": date(2025, 1, 15)
        }
        
        for status in PaymentStatus:
            payment = Payment(**base_payment_data, status=status)
            assert payment.status == status
    
    def test_payment_days_overdue_scenarios(self):
        """Test various days overdue scenarios"""
        test_cases = [
            (0, PaymentStatus.RECEIVED),
            (0, PaymentStatus.PENDING),
            (0, PaymentStatus.NOT_DUE),
            (5, PaymentStatus.OVERDUE),
            (30, PaymentStatus.OVERDUE)
        ]
        
        for days_overdue, status in test_cases:
            payment = Payment(
                garage_id="1",
                amount=Decimal("3500.00"),
                expected_date=date(2025, 1, 15),
                status=status,
                days_overdue=days_overdue
            )
            
            assert payment.days_overdue == days_overdue
            assert payment.status == status
    
    def test_payment_with_actual_date_scenarios(self):
        """Test payment with different actual date scenarios"""
        expected_date = date(2025, 1, 15)
        
        # Early payment
        early_payment = Payment(
            garage_id="1",
            amount=Decimal("3500.00"),
            expected_date=expected_date,
            actual_date=date(2025, 1, 10),
            status=PaymentStatus.RECEIVED
        )
        assert early_payment.actual_date < early_payment.expected_date
        
        # On-time payment  
        ontime_payment = Payment(
            garage_id="2",
            amount=Decimal("3500.00"),
            expected_date=expected_date,
            actual_date=expected_date,
            status=PaymentStatus.RECEIVED
        )
        assert ontime_payment.actual_date == ontime_payment.expected_date
        
        # Late payment
        late_payment = Payment(
            garage_id="3",
            amount=Decimal("3500.00"),
            expected_date=expected_date,
            actual_date=date(2025, 1, 20),
            status=PaymentStatus.RECEIVED
        )
        assert late_payment.actual_date > late_payment.expected_date
    
    def test_payment_mark_as_received_documentation(self):
        """Test that mark_as_received method exists for documentation"""
        payment = Payment(
            garage_id="1",
            amount=Decimal("3500.00"),
            expected_date=date(2025, 1, 15)
        )
        
        # Method should exist but not modify the immutable object
        assert hasattr(payment, 'mark_as_received')
        payment.mark_as_received(date(2025, 1, 16), "Test note")
        
        # Original object should remain unchanged
        assert payment.actual_date is None
        assert payment.status == PaymentStatus.NOT_DUE
