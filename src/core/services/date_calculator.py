"""
Date calculation service
"""

from datetime import date, timedelta
from calendar import monthrange
from typing import Optional
import logging

from ..models.garage import Garage


class DateCalculator:
    """
    Service for calculating expected payment dates
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_expected_date(self, garage: Garage, target_month: date) -> date:
        """
        Calculate expected payment date for a garage in a specific month
        
        Args:
            garage: Garage with payment details
            target_month: Month to calculate payment date for
            
        Returns:
            Expected payment date
        """
        target_year = target_month.year
        target_month_num = target_month.month
        payment_day = garage.payment_day
        
        # Handle cases where payment day doesn't exist in target month
        days_in_month = monthrange(target_year, target_month_num)[1]
        
        if payment_day <= days_in_month:
            return date(target_year, target_month_num, payment_day)
        else:
            # Use last day of month if payment day is too high
            self.logger.warning(
                f"Payment day {payment_day} doesn't exist in {target_year}-{target_month_num:02d}, "
                f"using last day ({days_in_month})"
            )
            return date(target_year, target_month_num, days_in_month)
    
    def get_next_payment_date(self, garage: Garage, from_date: date = None) -> date:
        """
        Get the next expected payment date for a garage
        
        Args:
            garage: Garage with payment details
            from_date: Calculate from this date (default: today)
            
        Returns:
            Next expected payment date
        """
        if from_date is None:
            from_date = date.today()
        
        # Start with current month
        current_month = date(from_date.year, from_date.month, 1)
        expected_date = self.calculate_expected_date(garage, current_month)
        
        # If payment date has passed this month, move to next month
        if expected_date < from_date:
            if current_month.month == 12:
                next_month = date(current_month.year + 1, 1, 1)
            else:
                next_month = date(current_month.year, current_month.month + 1, 1)
            expected_date = self.calculate_expected_date(garage, next_month)
        
        return expected_date
    
    def calculate_payment_day_from_start_date(self, start_date: date) -> int:
        """
        Extract payment day from garage start date
        
        Args:
            start_date: Initial rental start date
            
        Returns:
            Day of month for recurring payments
        """
        return start_date.day
    
    def is_payment_overdue(self, expected_date: date, current_date: date, grace_period_days: int = 3) -> bool:
        """
        Check if a payment is overdue
        
        Args:
            expected_date: Expected payment date
            current_date: Current date for comparison
            grace_period_days: Number of grace days after expected date
            
        Returns:
            True if payment is overdue
        """
        grace_end = expected_date + timedelta(days=grace_period_days)
        return current_date > grace_end
    
    def calculate_days_overdue(self, expected_date: date, current_date: date, grace_period_days: int = 3) -> int:
        """
        Calculate number of days a payment is overdue
        
        Args:
            expected_date: Expected payment date
            current_date: Current date for comparison
            grace_period_days: Number of grace days after expected date
            
        Returns:
            Number of days overdue (0 if not overdue)
        """
        grace_end = expected_date + timedelta(days=grace_period_days)
        if current_date > grace_end:
            return (current_date - grace_end).days
        return 0
