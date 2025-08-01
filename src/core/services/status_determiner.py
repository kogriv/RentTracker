"""
Payment status determination service
"""

from datetime import date, timedelta
from typing import Tuple, Optional
import logging

from ..models.payment import PaymentStatus


class StatusDeterminer:
    """
    Service for determining payment statuses based on dates and conditions
    """
    
    def __init__(self, grace_period_days: int = 3):
        """
        Initialize status determiner
        
        Args:
            grace_period_days: Number of days after expected date before marking overdue
        """
        self.grace_period_days = grace_period_days
        self.logger = logging.getLogger(__name__)
    
    def determine_status(self, 
                        expected_date: date, 
                        analysis_date: date, 
                        has_payment: bool = False,
                        actual_payment_date: Optional[date] = None,
                        has_multiple_payments: bool = False) -> Tuple[PaymentStatus, int]:
        """
        Determine payment status based on dates and payment existence
        
        Статусы определяются согласно таблице:
        - "Получен": Найден точный платеж в окне [расчетная_дата - 7 дней; расчетная_дата + 3 дня]
        - "Просрочен": Текущая дата > расчетная_дата + 3 дня И платеж не найден
        - "Срок не наступил": Текущая дата < расчетная_дата
        - "Ожидается оплата": Расчетная_дата ≤ текущая дата ≤ расчетная_дата + 3 дня И платеж не найден
        - "Неопределенно": Найдено несколько подходящих платежей
        
        Args:
            expected_date: Expected payment date (расчетная_дата)
            analysis_date: Date of analysis (текущая дата)
            has_payment: Whether a matching payment was found
            actual_payment_date: Date when payment was actually made
            has_multiple_payments: Whether multiple matching payments were found
            
        Returns:
            Tuple of (status, days_overdue)
        """
        
        # Если найдено несколько подходящих платежей - неопределенно
        if has_multiple_payments:
            return PaymentStatus.UNCLEAR, 0
        
        # Если найден точный платеж в окне [расчетная_дата - 7 дней; расчетная_дата + 3 дня] - получен
        if has_payment:
            if actual_payment_date:
                # Проверяем, что платеж в допустимом окне
                earliest_acceptable = expected_date - timedelta(days=7)
                latest_acceptable = expected_date + timedelta(days=self.grace_period_days)
                if earliest_acceptable <= actual_payment_date <= latest_acceptable:
                    # Рассчитываем разность дат: положительные = опоздание, отрицательные = досрочно
                    days_difference = (actual_payment_date - expected_date).days
                    return PaymentStatus.RECEIVED, days_difference
                else:
                    # Платеж найден, но вне допустимого окна - может быть неопределенно
                    return PaymentStatus.UNCLEAR, 0
            else:
                return PaymentStatus.RECEIVED, 0
        
        # Если платеж не найден, определяем статус по датам
        grace_end = expected_date + timedelta(days=self.grace_period_days)
        
        # Срок не наступил: текущая дата < расчетная_дата
        if analysis_date < expected_date:
            return PaymentStatus.NOT_DUE, 0
        
        # Ожидается оплата: расчетная_дата ≤ текущая дата ≤ расчетная_дата + 3 дня
        elif expected_date <= analysis_date <= grace_end:
            days_pending = (analysis_date - expected_date).days
            return PaymentStatus.PENDING, days_pending
        
        # Просрочен: текущая дата > расчетная_дата + 3 дня
        else:
            # Для неполученных платежей: разница между датой анализа и ожидаемой датой
            days_overdue = (analysis_date - expected_date).days
            return PaymentStatus.OVERDUE, days_overdue
    
    def is_payment_timely(self, expected_date: date, actual_date: date, early_days: int = 7) -> bool:
        """
        Check if payment was made within acceptable timeframe
        
        Args:
            expected_date: Expected payment date
            actual_date: Actual payment date
            early_days: Maximum days early that's acceptable
            
        Returns:
            True if payment is timely
        """
        earliest_acceptable = expected_date - timedelta(days=early_days)
        latest_acceptable = expected_date + timedelta(days=self.grace_period_days)
        
        return earliest_acceptable <= actual_date <= latest_acceptable
    
    def calculate_payment_delay(self, expected_date: date, actual_date: date) -> int:
        """
        Calculate number of days between expected and actual payment
        
        Args:
            expected_date: Expected payment date
            actual_date: Actual payment date
            
        Returns:
            Number of days (positive = late, negative = early)
        """
        return (actual_date - expected_date).days
