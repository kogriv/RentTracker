"""
Payment matching service
"""

from typing import List, Optional, Tuple, Dict
from decimal import Decimal
from datetime import date, timedelta
import logging

from ..models.garage import Garage
from ..models.payment import Payment, PaymentStatus
from ..models.transaction import Transaction
from ...infrastructure.localization.i18n import LocalizationManager


class PaymentMatcher:
    """
    Service for matching bank transactions to garage rental payments
    """
    
    def __init__(self, search_window_days: int = 7, grace_period_days: int = 3, i18n: Optional[LocalizationManager] = None):
        """
        Initialize payment matcher
        
        Args:
            search_window_days: Days before expected date to search for payments
            grace_period_days: Days after expected date before marking overdue
            i18n: Localization manager for translated messages
        """
        self.search_window_days = search_window_days
        self.grace_period_days = grace_period_days
        self.i18n = i18n or LocalizationManager("en")
        self.logger = logging.getLogger(__name__)
    
    def match_payments(self, 
                      garages: List[Garage], 
                      transactions: List[Transaction],
                      analysis_date: date,
                      target_month: Optional[date] = None) -> List[Payment]:
        """
        Match transactions to garage payments
        
        Args:
            garages: List of garages to process
            transactions: List of bank transactions
            analysis_date: Date for status analysis
            target_month: Target month for expected payment calculation (default: analysis_date month)
            
        Returns:
            List of payments with matched transactions and statuses
        """
        payments = []
        used_transactions = set()
        amount_conflicts = self._find_amount_conflicts(garages)
        
        # Use target_month if provided, otherwise use analysis_date month
        if target_month is None:
            target_month = date(analysis_date.year, analysis_date.month, 1)
        
        for garage in garages:
            # Calculate expected payment date for target month
            from .date_calculator import DateCalculator
            date_calc = DateCalculator()
            expected_date = date_calc.calculate_expected_date(garage, target_month)
            
            # Find matching transaction with fallback to wider search
            transaction, conflict_info = self._find_best_match(
                garage.monthly_rent,
                expected_date,
                transactions,
                used_transactions,
                amount_conflicts.get(garage.monthly_rent, []),
                analysis_date
            )
            
            # If no transaction found in narrow window, try wider search within statement period
            if transaction is None:
                transaction, conflict_info = self._find_fallback_match(
                    garage.monthly_rent,
                    transactions,
                    used_transactions,
                    amount_conflicts.get(garage.monthly_rent, []),
                    analysis_date
                )
            
            # Create payment record
            payment = Payment(
                garage_id=garage.id,
                amount=garage.monthly_rent,
                expected_date=expected_date
            )
            
            if transaction:
                # Mark transaction as used
                used_transactions.add(id(transaction))
                payment = self._create_matched_payment(payment, transaction, conflict_info)
            else:
                # No matching transaction found
                payment = self._create_unmatched_payment(payment, analysis_date)
            
            payments.append(payment)
        
        return payments
    
    def _find_amount_conflicts(self, garages: List[Garage]) -> Dict[Decimal, List[str]]:
        """Identify garages with duplicate rental amounts"""
        amount_map = {}
        for garage in garages:
            if garage.monthly_rent not in amount_map:
                amount_map[garage.monthly_rent] = []
            amount_map[garage.monthly_rent].append(garage.id)
        
        # Return only amounts with conflicts (more than one garage)
        return {amount: garage_ids for amount, garage_ids in amount_map.items() if len(garage_ids) > 1}
    
    def _find_best_match(self, 
                        amount: Decimal, 
                        expected_date: date,
                        transactions: List[Transaction],
                        used_transactions: set,
                        conflicting_garages: List[str],
                        analysis_date: date) -> Tuple[Optional[Transaction], str]:
        """
        Find the best matching transaction for a payment
        
        Returns:
            Tuple of (transaction, conflict_info)
        """
        # Define search window
        start_date = expected_date - timedelta(days=self.search_window_days)
        end_date = expected_date + timedelta(days=self.grace_period_days)
        
        # Find all matching transactions
        candidates = []
        for transaction in transactions:
            if (id(transaction) not in used_transactions and
                transaction.matches_amount(amount) and
                start_date <= transaction.date <= end_date and
                transaction.date <= analysis_date):  # Only consider transactions up to analysis date
                candidates.append(transaction)
        
        if not candidates:
            return None, ""
        
        if len(candidates) == 1:
            conflict_info = ""
            if conflicting_garages:
                conflict_info = f"Amount conflict with garages: {', '.join(conflicting_garages)}"
            return candidates[0], conflict_info
        
        # Multiple candidates - choose closest to expected date
        best_transaction = min(candidates, 
                             key=lambda t: abs((t.date - expected_date).days))
        
        conflict_info = self.i18n.get("notes.multiple_matches", default="Multiple matches found") + ", " + self.i18n.get("notes.closest_match", default="selected closest to expected date")
        if conflicting_garages:
            conflict_info += ". " + self.i18n.get("notes.amount_shared", garages=", ".join(conflicting_garages), default="Amount conflict with garages: {garages}")
        
        return best_transaction, conflict_info
    
    def _create_matched_payment(self, payment: Payment, transaction: Transaction, conflict_info: str) -> Payment:
        """Create payment record for matched transaction"""
        from .status_determiner import StatusDeterminer
        status_determiner = StatusDeterminer(grace_period_days=self.grace_period_days)
        
        # For matched payments, status should be RECEIVED regardless of timing
        # If we found a matching payment by amount, it's received
        status = PaymentStatus.RECEIVED
        
        # Calculate days difference: positive if late, negative if early  
        days_overdue = (transaction.date - payment.expected_date).days
        
        return Payment(
            garage_id=payment.garage_id,
            amount=payment.amount,
            expected_date=payment.expected_date,
            actual_date=transaction.date,
            status=status,
            days_overdue=days_overdue,
            notes=conflict_info if conflict_info else self.i18n.get("notes.payment_matched", default="Payment matched")
        )
    
    def _create_unmatched_payment(self, payment: Payment, analysis_date: date) -> Payment:
        """Create payment record for unmatched payment"""
        from .status_determiner import StatusDeterminer
        status_determiner = StatusDeterminer(grace_period_days=self.grace_period_days)
        
        status, days_overdue = status_determiner.determine_status(
            expected_date=payment.expected_date,
            analysis_date=analysis_date,
            has_payment=False,
            actual_payment_date=None,
            has_multiple_payments=False
        )
        
        return Payment(
            garage_id=payment.garage_id,
            amount=payment.amount,
            expected_date=payment.expected_date,
            actual_date=None,
            status=status,
            days_overdue=days_overdue,
            notes=self.i18n.get("notes.no_payment", default="No matching payment found")
        )
    
    def _find_fallback_match(self, 
                           amount: Decimal, 
                           transactions: List[Transaction],
                           used_transactions: set,
                           conflicting_garages: List[str],
                           analysis_date: date) -> Tuple[Optional[Transaction], str]:
        """
        Fallback search for transactions anywhere in the statement period
        
        Used when narrow window search fails - searches by amount only
        
        Returns:
            Tuple of (transaction, conflict_info)
        """
        # Find all matching transactions by amount only (but still within analysis date limit)
        candidates = []
        for transaction in transactions:
            if (id(transaction) not in used_transactions and
                transaction.matches_amount(amount) and
                transaction.date <= analysis_date):  # Only consider transactions up to analysis date
                candidates.append(transaction)
        
        if not candidates:
            self.logger.debug(f"Fallback search: No transactions found for amount {amount}")
            return None, ""
        
        if len(candidates) == 1:
            if conflicting_garages:
                conflict_info = self.i18n.get("notes.wide_search_shared", garages=", ".join(conflicting_garages), default="Wide search match (amount shared with garages: {garages})")
            else:
                conflict_info = self.i18n.get("notes.wide_search", default="Wide search match")
            
            self.logger.info(f"Fallback match found for amount {amount}: {candidates[0].date}")
            return candidates[0], conflict_info
        
        # Multiple candidates - prefer the earliest transaction
        best_transaction = min(candidates, key=lambda t: t.date)
        conflict_info = self.i18n.get("notes.wide_search_earliest", count=len(candidates), default="Wide search - earliest of {count} matches")
        if conflicting_garages:
            conflict_info += " (" + self.i18n.get("notes.amount_shared", garages=", ".join(conflicting_garages), default="amount shared with garages: {garages}") + ")"
        
        self.logger.warning(f"Fallback search found {len(candidates)} candidates for amount {amount}, using earliest: {best_transaction.date}")
        return best_transaction, conflict_info
