"""
Date utility functions
"""

from datetime import date, datetime, timedelta
from typing import Optional, List
from calendar import monthrange
import re


class DateUtils:
    """
    Utility functions for date operations
    """
    
    # Common date format patterns
    DATE_PATTERNS = [
        (r'(\d{2})\.(\d{2})\.(\d{4})', '%d.%m.%Y'),  # DD.MM.YYYY
        (r'(\d{2})/(\d{2})/(\d{4})', '%d/%m/%Y'),   # DD/MM/YYYY
        (r'(\d{4})-(\d{2})-(\d{2})', '%Y-%m-%d'),   # YYYY-MM-DD
        (r'(\d{2})-(\d{2})-(\d{4})', '%d-%m-%Y'),   # DD-MM-YYYY
    ]
    
    @staticmethod
    def parse_date(date_string: str) -> Optional[date]:
        """
        Parse date string using various formats
        
        Args:
            date_string: Date string to parse
            
        Returns:
            Parsed date or None if parsing fails
        """
        if not date_string:
            return None
        
        date_string = str(date_string).strip()
        
        # Try each pattern
        for pattern, format_str in DateUtils.DATE_PATTERNS:
            match = re.match(pattern, date_string)
            if match:
                try:
                    return datetime.strptime(date_string, format_str).date()
                except ValueError:
                    continue
        
        return None
    
    @staticmethod
    def get_last_day_of_month(year: int, month: int) -> int:
        """
        Get the last day of a specific month
        
        Args:
            year: Year
            month: Month (1-12)
            
        Returns:
            Last day of the month
        """
        return monthrange(year, month)[1]
    
    @staticmethod
    def adjust_payment_day(payment_day: int, target_year: int, target_month: int) -> int:
        """
        Adjust payment day for months that don't have enough days
        
        Args:
            payment_day: Desired payment day
            target_year: Target year
            target_month: Target month
            
        Returns:
            Adjusted payment day (uses last day of month if needed)
        """
        last_day = DateUtils.get_last_day_of_month(target_year, target_month)
        return min(payment_day, last_day)
    
    @staticmethod
    def calculate_expected_payment_date(base_date: date, target_month: date) -> date:
        """
        Calculate expected payment date based on base date and target month
        
        Args:
            base_date: Base date containing the payment day
            target_month: Target month for payment
            
        Returns:
            Expected payment date
        """
        payment_day = base_date.day
        adjusted_day = DateUtils.adjust_payment_day(
            payment_day, 
            target_month.year, 
            target_month.month
        )
        
        return date(target_month.year, target_month.month, adjusted_day)
    
    @staticmethod
    def is_date_in_range(check_date: date, 
                        center_date: date, 
                        days_before: int = 7, 
                        days_after: int = 3) -> bool:
        """
        Check if date is within range of center date
        
        Args:
            check_date: Date to check
            center_date: Center date for range
            days_before: Days before center date
            days_after: Days after center date
            
        Returns:
            True if date is in range
        """
        start_date = center_date - timedelta(days=days_before)
        end_date = center_date + timedelta(days=days_after)
        
        return start_date <= check_date <= end_date
    
    @staticmethod
    def get_months_between(start_date: date, end_date: date) -> List[date]:
        """
        Get list of first days of months between two dates
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of first days of months in range
        """
        months = []
        current = date(start_date.year, start_date.month, 1)
        end_month = date(end_date.year, end_date.month, 1)
        
        while current <= end_month:
            months.append(current)
            
            # Move to next month
            if current.month == 12:
                current = date(current.year + 1, 1, 1)
            else:
                current = date(current.year, current.month + 1, 1)
        
        return months
    
    @staticmethod
    def format_date(date_obj: date, format_str: str = "%Y-%m-%d") -> str:
        """
        Format date object as string
        
        Args:
            date_obj: Date to format
            format_str: Format string
            
        Returns:
            Formatted date string
        """
        if date_obj is None:
            return ""
        return date_obj.strftime(format_str)
    
    @staticmethod
    def days_difference(date1: date, date2: date) -> int:
        """
        Calculate days difference between two dates
        
        Args:
            date1: First date
            date2: Second date
            
        Returns:
            Number of days (positive if date2 > date1)
        """
        return (date2 - date1).days
    
    @staticmethod
    def is_weekend(check_date: date) -> bool:
        """
        Check if date falls on weekend
        
        Args:
            check_date: Date to check
            
        Returns:
            True if date is Saturday or Sunday
        """
        return check_date.weekday() >= 5
    
    @staticmethod
    def get_next_business_day(start_date: date) -> date:
        """
        Get next business day (skip weekends)
        
        Args:
            start_date: Starting date
            
        Returns:
            Next business day
        """
        next_day = start_date + timedelta(days=1)
        
        while DateUtils.is_weekend(next_day):
            next_day += timedelta(days=1)
        
        return next_day
