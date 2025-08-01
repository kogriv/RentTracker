"""
Unit tests for Garage model
"""

import pytest
from decimal import Decimal
from datetime import date

from src.core.models.garage import Garage


class TestGarage:
    """Test cases for Garage model"""
    
    def test_garage_creation_valid(self):
        """Test creating garage with valid data"""
        garage = Garage(
            id="1",
            monthly_rent=Decimal("3500.00"),
            start_date=date(2025, 1, 1),
            payment_day=1
        )
        
        assert garage.id == "1"
        assert garage.monthly_rent == Decimal("3500.00")
        assert garage.start_date == date(2025, 1, 1)
        assert garage.payment_day == 1
    
    def test_garage_creation_string_id(self):
        """Test creating garage with string ID"""
        garage = Garage(
            id="garage_1",
            monthly_rent=Decimal("2500.50"),
            start_date=date(2025, 2, 15),
            payment_day=15
        )
        
        assert garage.id == "garage_1"
        assert garage.display_name == "Garage #garage_1"
    
    def test_garage_validation_empty_id(self):
        """Test validation with empty ID"""
        with pytest.raises(ValueError, match="Garage ID cannot be empty"):
            Garage(
                id="",
                monthly_rent=Decimal("3500.00"),
                start_date=date(2025, 1, 1),
                payment_day=1
            )
    
    def test_garage_validation_negative_rent(self):
        """Test validation with negative rent"""
        with pytest.raises(ValueError, match="Monthly rent must be positive"):
            Garage(
                id="1",
                monthly_rent=Decimal("-100.00"),
                start_date=date(2025, 1, 1),
                payment_day=1
            )
    
    def test_garage_validation_zero_rent(self):
        """Test validation with zero rent"""
        with pytest.raises(ValueError, match="Monthly rent must be positive"):
            Garage(
                id="1",
                monthly_rent=Decimal("0.00"),
                start_date=date(2025, 1, 1),
                payment_day=1
            )
    
    def test_garage_validation_invalid_payment_day_low(self):
        """Test validation with payment day too low"""
        with pytest.raises(ValueError, match="Payment day must be between 1 and 31"):
            Garage(
                id="1",
                monthly_rent=Decimal("3500.00"),
                start_date=date(2025, 1, 1),
                payment_day=0
            )
    
    def test_garage_validation_invalid_payment_day_high(self):
        """Test validation with payment day too high"""
        with pytest.raises(ValueError, match="Payment day must be between 1 and 31"):
            Garage(
                id="1",
                monthly_rent=Decimal("3500.00"),
                start_date=date(2025, 1, 1),
                payment_day=32
            )
    
    def test_garage_payment_day_boundary_values(self):
        """Test payment day boundary values"""
        # Valid boundary values
        garage1 = Garage("1", Decimal("3500"), date(2025, 1, 1), 1)
        garage31 = Garage("31", Decimal("3500"), date(2025, 1, 1), 31)
        
        assert garage1.payment_day == 1
        assert garage31.payment_day == 31
    
    def test_garage_display_name(self):
        """Test display name property"""
        garage = Garage("TEST_ID", Decimal("3500"), date(2025, 1, 1), 15)
        assert garage.display_name == "Garage #TEST_ID"
    
    def test_garage_string_representation(self):
        """Test string representation"""
        garage = Garage("1", Decimal("3500.00"), date(2025, 1, 1), 15)
        str_repr = str(garage)
        
        assert "Garage(" in str_repr
        assert "id=1" in str_repr
        assert "rent=3500.00" in str_repr
        assert "day=15" in str_repr
    
    def test_garage_immutability(self):
        """Test that garage is immutable (frozen dataclass)"""
        garage = Garage("1", Decimal("3500"), date(2025, 1, 1), 15)
        
        with pytest.raises(AttributeError):
            garage.id = "2"
        
        with pytest.raises(AttributeError):
            garage.monthly_rent = Decimal("4000")
    
    def test_garage_equality(self):
        """Test garage equality comparison"""
        garage1 = Garage("1", Decimal("3500"), date(2025, 1, 1), 15)
        garage2 = Garage("1", Decimal("3500"), date(2025, 1, 1), 15)
        garage3 = Garage("2", Decimal("3500"), date(2025, 1, 1), 15)
        
        assert garage1 == garage2
        assert garage1 != garage3
    
    def test_garage_hash(self):
        """Test garage hashing (for sets and dicts)"""
        garage1 = Garage("1", Decimal("3500"), date(2025, 1, 1), 15)
        garage2 = Garage("1", Decimal("3500"), date(2025, 1, 1), 15)
        
        # Should be hashable and equal garages should have same hash
        garage_set = {garage1, garage2}
        assert len(garage_set) == 1
    
    def test_garage_different_payment_days(self):
        """Test garages with different payment days"""
        garages = [
            Garage("1", Decimal("3500"), date(2025, 1, 1), 1),
            Garage("2", Decimal("3500"), date(2025, 1, 15), 15),
            Garage("3", Decimal("3500"), date(2025, 1, 31), 31)
        ]
        
        assert len(set(g.payment_day for g in garages)) == 3
    
    def test_garage_with_high_precision_amount(self):
        """Test garage with high precision decimal amount"""
        garage = Garage(
            id="precise",
            monthly_rent=Decimal("3599.99"),
            start_date=date(2025, 1, 1),
            payment_day=1
        )
        
        assert garage.monthly_rent == Decimal("3599.99")
