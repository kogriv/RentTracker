"""
Data validation utilities
"""

import re
from decimal import Decimal, InvalidOperation
from datetime import date
from typing import Any, List, Dict, Optional, Tuple
from pathlib import Path


class ValidationError(Exception):
    """Validation error exception"""
    pass


class DataValidator:
    """
    Utility class for data validation
    """
    
    # Regex patterns for validation
    GARAGE_ID_PATTERN = re.compile(r'^[A-Za-z0-9\-_]+$')
    AMOUNT_PATTERN = re.compile(r'^\d+([.,]\d{1,2})?$')
    DATE_PATTERN = re.compile(r'^\d{2}[./\-]\d{2}[./\-]\d{4}$')
    
    @staticmethod
    def validate_garage_id(garage_id: str) -> bool:
        """
        Validate garage ID format
        
        Args:
            garage_id: Garage ID to validate
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If validation fails
        """
        if not garage_id or not isinstance(garage_id, str):
            raise ValidationError("Garage ID must be a non-empty string")
        
        garage_id = garage_id.strip()
        
        if not garage_id:
            raise ValidationError("Garage ID cannot be empty or whitespace only")
        
        if len(garage_id) > 20:
            raise ValidationError("Garage ID too long (max 20 characters)")
        
        if not DataValidator.GARAGE_ID_PATTERN.match(garage_id):
            raise ValidationError("Garage ID contains invalid characters (only letters, numbers, hyphens, underscores allowed)")
        
        return True
    
    @staticmethod
    def validate_amount(amount: Any) -> Decimal:
        """
        Validate and convert amount to Decimal
        
        Args:
            amount: Amount to validate
            
        Returns:
            Validated amount as Decimal
            
        Raises:
            ValidationError: If validation fails
        """
        if amount is None:
            raise ValidationError("Amount cannot be None")
        
        try:
            # Handle different input types
            if isinstance(amount, Decimal):
                decimal_amount = amount
            elif isinstance(amount, (int, float)):
                decimal_amount = Decimal(str(amount))
            elif isinstance(amount, str):
                # Clean string amount
                clean_amount = amount.strip().replace(',', '.').replace(' ', '')
                if not clean_amount:
                    raise ValidationError("Amount cannot be empty")
                decimal_amount = Decimal(clean_amount)
            else:
                raise ValidationError(f"Unsupported amount type: {type(amount)}")
            
            # Validate amount value
            if decimal_amount <= 0:
                raise ValidationError("Amount must be positive")
            
            if decimal_amount > Decimal('1000000'):
                raise ValidationError("Amount too large (max 1,000,000)")
            
            # Round to 2 decimal places
            return decimal_amount.quantize(Decimal('0.01'))
            
        except InvalidOperation as e:
            raise ValidationError(f"Invalid amount format: {amount}")
    
    @staticmethod
    def validate_date(date_value: Any) -> date:
        """
        Validate date value
        
        Args:
            date_value: Date to validate
            
        Returns:
            Validated date
            
        Raises:
            ValidationError: If validation fails
        """
        if date_value is None:
            raise ValidationError("Date cannot be None")
        
        if isinstance(date_value, date):
            return date_value
        
        # Try to parse string date
        from .date_utils import DateUtils
        
        if isinstance(date_value, str):
            parsed_date = DateUtils.parse_date(date_value)
            if parsed_date is None:
                raise ValidationError(f"Invalid date format: {date_value}")
            return parsed_date
        
        raise ValidationError(f"Unsupported date type: {type(date_value)}")
    
    @staticmethod
    def validate_payment_day(payment_day: Any) -> int:
        """
        Validate payment day
        
        Args:
            payment_day: Payment day to validate
            
        Returns:
            Validated payment day
            
        Raises:
            ValidationError: If validation fails
        """
        if payment_day is None:
            raise ValidationError("Payment day cannot be None")
        
        try:
            day = int(payment_day)
        except (ValueError, TypeError):
            raise ValidationError(f"Payment day must be a number: {payment_day}")
        
        if not (1 <= day <= 31):
            raise ValidationError(f"Payment day must be between 1 and 31: {day}")
        
        return day
    
    @staticmethod
    def validate_file_path(file_path: Any, must_exist: bool = True) -> Path:
        """
        Validate file path
        
        Args:
            file_path: File path to validate
            must_exist: Whether file must exist
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationError: If validation fails
        """
        if file_path is None:
            raise ValidationError("File path cannot be None")
        
        if isinstance(file_path, str):
            path = Path(file_path)
        elif isinstance(file_path, Path):
            path = file_path
        else:
            raise ValidationError(f"Unsupported file path type: {type(file_path)}")
        
        if must_exist and not path.exists():
            raise ValidationError(f"File does not exist: {path}")
        
        return path
    
    @staticmethod
    def validate_excel_file(file_path: Path) -> bool:
        """
        Validate Excel file
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If validation fails
        """
        if not file_path.exists():
            raise ValidationError(f"Excel file does not exist: {file_path}")
        
        if file_path.suffix.lower() not in ['.xlsx', '.xls']:
            raise ValidationError(f"File is not an Excel file: {file_path}")
        
        if file_path.stat().st_size == 0:
            raise ValidationError(f"Excel file is empty: {file_path}")
        
        return True
    
    @staticmethod
    def validate_garage_data(garage_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete garage data dictionary
        
        Args:
            garage_data: Garage data to validate
            
        Returns:
            Validated garage data
            
        Raises:
            ValidationError: If validation fails
        """
        required_fields = ['id', 'monthly_rent', 'start_date', 'payment_day']
        
        for field in required_fields:
            if field not in garage_data:
                raise ValidationError(f"Missing required field: {field}")
        
        validated_data = {}
        
        # Validate each field
        validated_data['id'] = garage_data['id']
        DataValidator.validate_garage_id(validated_data['id'])
        
        validated_data['monthly_rent'] = DataValidator.validate_amount(garage_data['monthly_rent'])
        validated_data['start_date'] = DataValidator.validate_date(garage_data['start_date'])
        validated_data['payment_day'] = DataValidator.validate_payment_day(garage_data['payment_day'])
        
        return validated_data
    
    @staticmethod
    def find_duplicate_amounts(garage_list: List[Dict[str, Any]]) -> Dict[Decimal, List[str]]:
        """
        Find duplicate amounts in garage list
        
        Args:
            garage_list: List of garage data dictionaries
            
        Returns:
            Dictionary mapping amounts to list of garage IDs with that amount
        """
        amount_map = {}
        
        for garage in garage_list:
            amount = garage.get('monthly_rent')
            garage_id = garage.get('id')
            
            if amount is not None and garage_id is not None:
                if amount not in amount_map:
                    amount_map[amount] = []
                amount_map[amount].append(str(garage_id))
        
        # Return only duplicates
        return {amount: ids for amount, ids in amount_map.items() if len(ids) > 1}
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date) -> bool:
        """
        Validate date range
        
        Args:
            start_date: Range start date
            end_date: Range end date
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If validation fails
        """
        if start_date > end_date:
            raise ValidationError("Start date must be before or equal to end date")
        
        # Check if range is reasonable (not more than 10 years)
        max_days = 10 * 365
        if (end_date - start_date).days > max_days:
            raise ValidationError("Date range too large (max 10 years)")
        
        return True
