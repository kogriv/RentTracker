"""
Unit tests for DateCalculator service
"""

import pytest
from datetime import date
from unittest.mock import patch

from src.core.services.date_calculator import DateCalculator
from src.core.models.garage import Garage
from decimal import Decimal


class TestDateCalculator:
    """Test cases for DateCalculator service"""
    
    @pytest.fixture
    def date_calculator(self):
        """Create DateCalculator instance for testing"""
        return DateCalculator()
    
    def test_calculate_expected_date_normal_month(self, date_calculator):
        """Test expected date calculation for normal month"""
        garage = Garage("1", Decimal("3500"), date(2025, 1, 15), 15)
        target_month = date(2025, 2, 1)  # February 2025
        
        expected_date = date_calculator.calculate_expected_date(garage, target_month)
        
        assert expected_date == date(2025, 2, 15)
    
    def test_calculate_expected_date_february_leap_year(self, date_calculator):
        """Test expected date calculation for February in leap year"""
        garage = Garage("1", Decimal("3500"), date(2024, 1, 29), 29)
        target_month = date(2024, 2, 1)  # February 2024 (leap year)
        
        expected_date = date_calculator.calculate_expected_date(garage, target_month)
        
        assert expected_date == date(2024, 2, 29)  # February 29 exists in leap year
    
    def test_calculate_expected_date_february_non_leap_year(self, date_calculator):
        """Test expected date calculation for February in non-leap year"""
        garage = Garage("1", Decimal("3500"), date(2025, 1, 29), 29)
        target_month = date(2025, 2, 1)  # February 2025 (non-leap year)
        
        expected_date = date_calculator.calculate_expected_date(garage, target_month)
        
        assert expected_date == date(2025, 2, 28)  # February 29 doesn't exist, use 28
    
    def test_calculate_expected_date_short_month(self, date_calculator):
        """Test expected date calculation for short month (30 days)"""
        garage = Garage("1", Decimal("3500"), date(2025, 1, 31), 31)
        target_month = date(2025, 4, 1)  # April 2025 (30 days)
        
        expected_date = date_calculator.calculate_expected_date(garage, target_month)
        
        assert expected_date == date(2025, 4, 30)  # April 31 doesn't exist, use 30
    
    def test_calculate_expected_date_first_of_month(self, date_calculator):
        """Test expected date calculation for 1st of month"""
        garage = Garage("1", Decimal("3500"), date(2025, 1, 1), 1)
        target_month = date(2025, 3, 1)
        
        expected_date = date_calculator.calculate_expected_date(garage, target_month)
        
        assert expected_date == date(2025, 3, 1)
    
    def test_calculate_expected_date_end_of_month(self, date_calculator):
        """Test expected date calculation for end of month"""
        garage = Garage("1", Decimal("3500"), date(2025, 1, 31), 31)
        target_month = date(2025, 1, 1)  # Same month with 31 days
        
        expected_date = date_calculator.calculate_expected_date(garage, target_month)
        
        assert expected_date == date(2025, 1, 31)
    
    def test_get_next_payment_date_same_month_future(self, date_calculator):
        """Test next payment date when payment day hasn't passed this month"""
        garage = Garage("1", Decimal("3500"), date(2025, 1, 15), 15)
        
        with patch('src.core.services.date_calculator.date') as mock_date:
            mock_date.today.return_value = date(2025, 1, 10)  # Before payment day
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            
            next_date = date_calculator.get_next_payment_date(garage)
            
            assert next_date == date(2025, 1, 15)
    
    def test_get_next_payment_date_same_month_past(self, date_calculator):
        """Test next payment date when payment day has passed this month"""
        garage = Garage("1", Decimal("3500"), date(2025, 1, 15), 15)
        
        with patch('src.core.services.date_calculator.date') as mock_date:
            mock_date.today.return_value = date(2025, 1, 20)  # After payment day
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            
            next_date = date_calculator.get_next_payment_date(garage)
            
            assert next_date == date(2025, 2, 15)  # Next month
    
    def test_get_next_payment_date_december_rollover(self, date_calculator):
        """Test next payment date rollover from December to January"""
        garage = Garage("1", Decimal("3500"), date(2024, 12, 15), 15)
        
        with patch('src.core.services.date_calculator.date') as mock_date:
            mock_date.today.return_value = date(2024, 12, 20)  # After payment day in December
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            
            next_date = date_calculator.get_next_payment_date(garage)
            
            assert next_date == date(2025, 1, 15)  # Next year
    
    def test_get_next_payment_date_with_from_date(self, date_calculator):
        """Test next payment date with specific from_date"""
        garage = Garage("1", Decimal("3500"), date(2025, 1, 15), 15)
        from_date = date(2025, 3, 10)  # March 10
        
        next_date = date_calculator.get_next_payment_date(garage, from_date)
        
        assert next_date == date(2025, 3, 15)  # March 15
    
    def test_calculate_payment_day_from_start_date(self, date_calculator):
        """Test extracting payment day from start date"""
        test_cases = [
            (date(2025, 1, 1), 1),
            (date(2025, 1, 15), 15),
            (date(2025, 1, 31), 31),
            (date(2025, 2, 28), 28),
        ]
        
        for start_date, expected_day in test_cases:
            payment_day = date_calculator.calculate_payment_day_from_start_date(start_date)
            assert payment_day == expected_day
    
    def test_is_payment_overdue_not_overdue(self, date_calculator):
        """Test payment not overdue scenarios"""
        expected_date = date(2025, 1, 15)
        grace_period = 3
        
        # Same day - not overdue
        assert date_calculator.is_payment_overdue(expected_date, expected_date, grace_period) is False
        
        # Within grace period - not overdue
        assert date_calculator.is_payment_overdue(expected_date, date(2025, 1, 18), grace_period) is False
        
        # Last day of grace period - not overdue
        assert date_calculator.is_payment_overdue(expected_date, date(2025, 1, 18), grace_period) is False
    
    def test_is_payment_overdue_overdue(self, date_calculator):
        """Test payment overdue scenarios"""
        expected_date = date(2025, 1, 15)
        grace_period = 3
        
        # After grace period - overdue
        assert date_calculator.is_payment_overdue(expected_date, date(2025, 1, 19), grace_period) is True
        
        # Much later - overdue
        assert date_calculator.is_payment_overdue(expected_date, date(2025, 2, 1), grace_period) is True
    
    def test_calculate_days_overdue_not_overdue(self, date_calculator):
        """Test days overdue calculation when not overdue"""
        expected_date = date(2025, 1, 15)
        grace_period = 3
        
        # Same day
        assert date_calculator.calculate_days_overdue(expected_date, expected_date, grace_period) == 0
        
        # Within grace period
        assert date_calculator.calculate_days_overdue(expected_date, date(2025, 1, 17), grace_period) == 0
        
        # Last day of grace period
        assert date_calculator.calculate_days_overdue(expected_date, date(2025, 1, 18), grace_period) == 0
    
    def test_calculate_days_overdue_overdue(self, date_calculator):
        """Test days overdue calculation when overdue"""
        expected_date = date(2025, 1, 15)
        grace_period = 3
        
        # 1 day overdue
        assert date_calculator.calculate_days_overdue(expected_date, date(2025, 1, 19), grace_period) == 1
        
        # 5 days overdue
        assert date_calculator.calculate_days_overdue(expected_date, date(2025, 1, 23), grace_period) == 5
        
        # 17 days overdue
        assert date_calculator.calculate_days_overdue(expected_date, date(2025, 2, 5), grace_period) == 17
    
    def test_calculate_days_overdue_custom_grace_period(self, date_calculator):
        """Test days overdue calculation with custom grace period"""
        expected_date = date(2025, 1, 15)
        
        # 0 day grace period
        assert date_calculator.calculate_days_overdue(expected_date, date(2025, 1, 16), 0) == 1
        
        # 7 day grace period
        assert date_calculator.calculate_days_overdue(expected_date, date(2025, 1, 23), 7) == 1
        assert date_calculator.calculate_days_overdue(expected_date, date(2025, 1, 22), 7) == 0
    
    def test_edge_case_february_29_to_non_leap_year(self, date_calculator):
        """Test edge case: February 29 payment day in non-leap year"""
        # This is a theoretical case - normally payment_day would be <= 28 for Feb start dates
        garage = Garage("1", Decimal("3500"), date(2024, 2, 29), 29)  # Leap year start
        target_month = date(2025, 2, 1)  # Non-leap year target
        
        expected_date = date_calculator.calculate_expected_date(garage, target_month)
        
        assert expected_date == date(2025, 2, 28)  # Adjusted to last day of February
    
    def test_various_months_day_31(self, date_calculator):
        """Test payment day 31 across various months"""
        garage = Garage("1", Decimal("3500"), date(2025, 1, 31), 31)
        
        test_cases = [
            (date(2025, 1, 1), date(2025, 1, 31)),  # January - 31 days
            (date(2025, 2, 1), date(2025, 2, 28)),  # February - 28 days
            (date(2025, 3, 1), date(2025, 3, 31)),  # March - 31 days
            (date(2025, 4, 1), date(2025, 4, 30)),  # April - 30 days
            (date(2025, 5, 1), date(2025, 5, 31)),  # May - 31 days
            (date(2025, 6, 1), date(2025, 6, 30)),  # June - 30 days
        ]
        
        for target_month, expected_result in test_cases:
            result = date_calculator.calculate_expected_date(garage, target_month)
            assert result == expected_result
