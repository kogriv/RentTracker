"""
Unit tests for Transaction model
"""

import pytest
from decimal import Decimal
from datetime import date

from src.core.models.transaction import Transaction


class TestTransaction:
    """Test cases for Transaction model"""
    
    def test_transaction_creation_minimal(self):
        """Test creating transaction with minimal required data"""
        transaction = Transaction(
            date=date(2025, 1, 15),
            amount=Decimal("3500.00"),
            category="Transfer"
        )
        
        assert transaction.date == date(2025, 1, 15)
        assert transaction.amount == Decimal("3500.00")
        assert transaction.category == "Transfer"
        assert transaction.source == "bank_statement"
        assert transaction.description is None
    
    def test_transaction_creation_complete(self):
        """Test creating transaction with all data"""
        transaction = Transaction(
            date=date(2025, 1, 15),
            amount=Decimal("3500.00"),
            category="Перевод СБП",
            source="sberbank_statement_row_45",
            description="Payment from mobile app"
        )
        
        assert transaction.date == date(2025, 1, 15)
        assert transaction.amount == Decimal("3500.00")
        assert transaction.category == "Перевод СБП"
        assert transaction.source == "sberbank_statement_row_45"
        assert transaction.description == "Payment from mobile app"
    
    def test_transaction_validation_negative_amount(self):
        """Test validation with negative amount"""
        with pytest.raises(ValueError, match="Transaction amount must be positive"):
            Transaction(
                date=date(2025, 1, 15),
                amount=Decimal("-100.00"),
                category="Transfer"
            )
    
    def test_transaction_validation_zero_amount(self):
        """Test validation with zero amount"""
        with pytest.raises(ValueError, match="Transaction amount must be positive"):
            Transaction(
                date=date(2025, 1, 15),
                amount=Decimal("0.00"),
                category="Transfer"
            )
    
    def test_transaction_validation_empty_category(self):
        """Test validation with empty category"""
        with pytest.raises(ValueError, match="Transaction category cannot be empty"):
            Transaction(
                date=date(2025, 1, 15),
                amount=Decimal("3500.00"),
                category=""
            )
    
    def test_transaction_is_incoming_property(self):
        """Test is_incoming property"""
        transaction = Transaction(
            date=date(2025, 1, 15),
            amount=Decimal("3500.00"),
            category="Transfer"
        )
        
        # All valid transactions should be incoming (positive amounts)
        assert transaction.is_incoming is True
    
    def test_transaction_matches_amount_exact(self):
        """Test exact amount matching"""
        transaction = Transaction(
            date=date(2025, 1, 15),
            amount=Decimal("3500.00"),
            category="Transfer"
        )
        
        # Exact match
        assert transaction.matches_amount(Decimal("3500.00")) is True
        
        # No match
        assert transaction.matches_amount(Decimal("3600.00")) is False
    
    def test_transaction_matches_amount_with_tolerance(self):
        """Test amount matching with tolerance"""
        transaction = Transaction(
            date=date(2025, 1, 15),
            amount=Decimal("3500.00"),
            category="Transfer"
        )
        
        tolerance = Decimal("0.10")
        
        # Within tolerance
        assert transaction.matches_amount(Decimal("3500.05"), tolerance) is True
        assert transaction.matches_amount(Decimal("3499.95"), tolerance) is True
        
        # Outside tolerance
        assert transaction.matches_amount(Decimal("3500.15"), tolerance) is False
        assert transaction.matches_amount(Decimal("3499.85"), tolerance) is False
    
    def test_transaction_matches_amount_default_tolerance(self):
        """Test amount matching with default tolerance"""
        transaction = Transaction(
            date=date(2025, 1, 15),
            amount=Decimal("3500.00"),
            category="Transfer"
        )
        
        # Default tolerance is 0.01
        assert transaction.matches_amount(Decimal("3500.01")) is True
        assert transaction.matches_amount(Decimal("3499.99")) is True
        assert transaction.matches_amount(Decimal("3500.02")) is False
        assert transaction.matches_amount(Decimal("3499.98")) is False
    
    def test_transaction_string_representation(self):
        """Test string representation"""
        transaction = Transaction(
            date=date(2025, 1, 15),
            amount=Decimal("3500.00"),
            category="Transfer"
        )
        
        str_repr = str(transaction)
        assert "Transaction(" in str_repr
        assert "date=2025-01-15" in str_repr
        assert "amount=3500.00" in str_repr
        assert "category=Transfer" in str_repr
    
    def test_transaction_immutability(self):
        """Test that transaction is immutable (frozen dataclass)"""
        transaction = Transaction(
            date=date(2025, 1, 15),
            amount=Decimal("3500.00"),
            category="Transfer"
        )
        
        with pytest.raises(AttributeError):
            transaction.amount = Decimal("4000")
        
        with pytest.raises(AttributeError):
            transaction.category = "New Category"
    
    def test_transaction_equality(self):
        """Test transaction equality comparison"""
        transaction1 = Transaction(
            date=date(2025, 1, 15),
            amount=Decimal("3500.00"),
            category="Transfer"
        )
        
        transaction2 = Transaction(
            date=date(2025, 1, 15),
            amount=Decimal("3500.00"),
            category="Transfer"
        )
        
        transaction3 = Transaction(
            date=date(2025, 1, 16),
            amount=Decimal("3500.00"),
            category="Transfer"
        )
        
        assert transaction1 == transaction2
        assert transaction1 != transaction3
    
    def test_transaction_different_categories(self):
        """Test transactions with different categories"""
        categories = [
            "Перевод на карту",
            "Перевод СБП",
            "Transfer",
            "Mobile payment",
            "Online transfer"
        ]
        
        for category in categories:
            transaction = Transaction(
                date=date(2025, 1, 15),
                amount=Decimal("3500.00"),
                category=category
            )
            assert transaction.category == category
    
    def test_transaction_different_sources(self):
        """Test transactions with different sources"""
        sources = [
            "bank_statement",
            "sberbank_statement_row_1",
            "manual_entry",
            "api_import",
            "csv_import"
        ]
        
        for source in sources:
            transaction = Transaction(
                date=date(2025, 1, 15),
                amount=Decimal("3500.00"),
                category="Transfer",
                source=source
            )
            assert transaction.source == source
    
    def test_transaction_high_precision_amount(self):
        """Test transaction with high precision amount"""
        transaction = Transaction(
            date=date(2025, 1, 15),
            amount=Decimal("3599.99"),
            category="Transfer"
        )
        
        assert transaction.amount == Decimal("3599.99")
        assert transaction.matches_amount(Decimal("3599.99")) is True
    
    def test_transaction_with_description_variations(self):
        """Test transaction with various descriptions"""
        descriptions = [
            None,
            "",
            "Simple payment",
            "Платеж за аренду гаража №5",
            "Payment with special characters: №1, 50% fee"
        ]
        
        for desc in descriptions:
            transaction = Transaction(
                date=date(2025, 1, 15),
                amount=Decimal("3500.00"),
                category="Transfer",
                description=desc
            )
            assert transaction.description == desc
