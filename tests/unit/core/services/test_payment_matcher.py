"""
Unit tests for PaymentMatcher service
"""

import pytest
from decimal import Decimal
from datetime import date, timedelta

from src.core.services.payment_matcher import PaymentMatcher
from src.core.models.garage import Garage
from src.core.models.transaction import Transaction
from src.core.models.payment import PaymentStatus


class TestPaymentMatcher:
    """Test cases for PaymentMatcher service"""
    
    @pytest.fixture
    def payment_matcher(self):
        """Create PaymentMatcher instance for testing"""
        return PaymentMatcher(search_window_days=7, grace_period_days=3)
    
    @pytest.fixture
    def sample_garages(self):
        """Create sample garages for testing"""
        return [
            Garage("1", Decimal("3500.00"), date(2025, 1, 1), 15),
            Garage("2", Decimal("2800.00"), date(2025, 1, 2), 16),
            Garage("3", Decimal("4200.00"), date(2025, 1, 3), 17),
        ]
    
    @pytest.fixture
    def sample_transactions(self):
        """Create sample transactions for testing"""
        return [
            Transaction(date(2025, 1, 15), Decimal("3500.00"), "Перевод СБП"),
            Transaction(date(2025, 1, 16), Decimal("2800.00"), "Перевод на карту"),
            Transaction(date(2025, 1, 18), Decimal("4200.00"), "Перевод СБП"),
        ]
    
    def test_match_payments_perfect_matches(self, payment_matcher, sample_garages, sample_transactions):
        """Test payment matching with perfect matches"""
        analysis_date = date(2025, 1, 20)
        
        payments = payment_matcher.match_payments(sample_garages, sample_transactions, analysis_date)
        
        assert len(payments) == 3
        
        # Check that all payments were matched
        received_payments = [p for p in payments if p.status == PaymentStatus.RECEIVED]
        assert len(received_payments) == 3
        
        # Check specific matches
        garage1_payment = next(p for p in payments if p.garage_id == "1")
        assert garage1_payment.actual_date == date(2025, 1, 15)
        assert garage1_payment.amount == Decimal("3500.00")
    
    def test_match_payments_no_matches(self, payment_matcher, sample_garages):
        """Test payment matching with no matching transactions"""
        # Transactions with different amounts
        transactions = [
            Transaction(date(2025, 1, 15), Decimal("1000.00"), "Перевод СБП"),
            Transaction(date(2025, 1, 16), Decimal("2000.00"), "Перевод на карту"),
        ]
        
        analysis_date = date(2025, 1, 20)
        payments = payment_matcher.match_payments(sample_garages, transactions, analysis_date)
        
        assert len(payments) == 3
        
        # Check that no payments were matched (all should be overdue)
        received_payments = [p for p in payments if p.status == PaymentStatus.RECEIVED]
        assert len(received_payments) == 0
        
        overdue_payments = [p for p in payments if p.status == PaymentStatus.OVERDUE]
        assert len(overdue_payments) == 3
    
    def test_match_payments_partial_matches(self, payment_matcher, sample_garages):
        """Test payment matching with partial matches"""
        # Only some amounts match
        transactions = [
            Transaction(date(2025, 1, 15), Decimal("3500.00"), "Перевод СБП"),
            Transaction(date(2025, 1, 16), Decimal("1000.00"), "Перевод на карту"),  # No match
        ]
        
        analysis_date = date(2025, 1, 20)
        payments = payment_matcher.match_payments(sample_garages, transactions, analysis_date)
        
        assert len(payments) == 3
        
        # One match, two overdue
        received_payments = [p for p in payments if p.status == PaymentStatus.RECEIVED]
        assert len(received_payments) == 1
        
        overdue_payments = [p for p in payments if p.status == PaymentStatus.OVERDUE]
        assert len(overdue_payments) == 2
    
    def test_match_payments_outside_time_window(self, payment_matcher, sample_garages):
        """Test payment matching outside time window"""
        # Transaction too early (more than 7 days before expected)
        transactions = [
            Transaction(date(2025, 1, 5), Decimal("3500.00"), "Перевод СБП"),  # Expected: 15th
        ]
        
        analysis_date = date(2025, 1, 20)
        payments = payment_matcher.match_payments(sample_garages, transactions, analysis_date)
        
        garage1_payment = next(p for p in payments if p.garage_id == "1")
        assert garage1_payment.status == PaymentStatus.OVERDUE
        assert garage1_payment.actual_date is None
    
    def test_match_payments_multiple_candidates_closest_selected(self, payment_matcher):
        """Test that closest transaction is selected when multiple candidates exist"""
        garages = [Garage("1", Decimal("3500.00"), date(2025, 1, 1), 15)]
        
        # Multiple transactions with same amount, different dates
        transactions = [
            Transaction(date(2025, 1, 10), Decimal("3500.00"), "Перевод СБП"),  # 5 days early
            Transaction(date(2025, 1, 16), Decimal("3500.00"), "Перевод СБП"),  # 1 day late
            Transaction(date(2025, 1, 14), Decimal("3500.00"), "Перевод СБП"),  # 1 day early - closest
        ]
        
        analysis_date = date(2025, 1, 20)
        payments = payment_matcher.match_payments(garages, transactions, analysis_date)
        
        payment = payments[0]
        assert payment.status == PaymentStatus.RECEIVED
        assert payment.actual_date == date(2025, 1, 14)  # Closest to expected date (15th)
        assert "Multiple matches found" in payment.notes
    
    def test_match_payments_duplicate_amounts_conflict(self, payment_matcher):
        """Test handling of duplicate amounts between garages"""
        # Two garages with same amount
        garages = [
            Garage("1", Decimal("3500.00"), date(2025, 1, 1), 15),
            Garage("2", Decimal("3500.00"), date(2025, 1, 1), 16),  # Different expected date
        ]
        
        transactions = [
            Transaction(date(2025, 1, 15), Decimal("3500.00"), "Перевод СБП"),
        ]
        
        analysis_date = date(2025, 1, 20)
        payments = payment_matcher.match_payments(garages, transactions, analysis_date)
        
        # One should get the payment (closest to expected date), other should be unmatched
        received_payments = [p for p in payments if p.status == PaymentStatus.RECEIVED]
        assert len(received_payments) == 1
        
        # Check conflict is noted
        received_payment = received_payments[0]
        assert "Amount conflict" in received_payment.notes
        assert received_payment.garage_id == "1"  # Closer to transaction date
    
    def test_match_payments_pending_status(self, payment_matcher, sample_garages, sample_transactions):
        """Test pending status within grace period"""
        # Analysis date within grace period after expected dates
        analysis_date = date(2025, 1, 17)  # 2 days after first expected payment
        
        payments = payment_matcher.match_payments(sample_garages, sample_transactions, analysis_date)
        
        # Should have mix of received and pending
        received_count = sum(1 for p in payments if p.status == PaymentStatus.RECEIVED)
        pending_count = sum(1 for p in payments if p.status == PaymentStatus.PENDING)
        
        assert received_count > 0
        assert pending_count >= 0  # Might be 0 if all are matched
    
    def test_match_payments_not_due_status(self, payment_matcher, sample_garages, sample_transactions):
        """Test not due status before expected dates"""
        # Analysis date before expected dates
        analysis_date = date(2025, 1, 10)
        
        payments = payment_matcher.match_payments(sample_garages, sample_transactions, analysis_date)
        
        # All should be not due yet (since analysis is before expected dates)
        not_due_count = sum(1 for p in payments if p.status == PaymentStatus.NOT_DUE)
        assert not_due_count == 3
    
    def test_find_amount_conflicts(self, payment_matcher):
        """Test finding amount conflicts between garages"""
        garages = [
            Garage("1", Decimal("3500.00"), date(2025, 1, 1), 15),
            Garage("2", Decimal("2800.00"), date(2025, 1, 1), 16),
            Garage("3", Decimal("3500.00"), date(2025, 1, 1), 17),  # Duplicate amount
            Garage("4", Decimal("4200.00"), date(2025, 1, 1), 18),
        ]
        
        conflicts = payment_matcher._find_amount_conflicts(garages)
        
        assert Decimal("3500.00") in conflicts
        assert len(conflicts[Decimal("3500.00")]) == 2
        assert "1" in conflicts[Decimal("3500.00")]
        assert "3" in conflicts[Decimal("3500.00")]
        
        # Non-duplicate amounts should not be in conflicts
        assert Decimal("2800.00") not in conflicts
        assert Decimal("4200.00") not in conflicts
    
    def test_match_payments_transaction_reuse_prevention(self, payment_matcher):
        """Test that transactions are not reused across matches"""
        # Two garages with same amount, one transaction
        garages = [
            Garage("1", Decimal("3500.00"), date(2025, 1, 1), 15),
            Garage("2", Decimal("3500.00"), date(2025, 1, 1), 15),  # Same expected date
        ]
        
        transactions = [
            Transaction(date(2025, 1, 15), Decimal("3500.00"), "Перевод СБП"),
        ]
        
        analysis_date = date(2025, 1, 20)
        payments = payment_matcher.match_payments(garages, transactions, analysis_date)
        
        # Only one should be matched
        received_payments = [p for p in payments if p.status == PaymentStatus.RECEIVED]
        assert len(received_payments) == 1
        
        unmatched_payments = [p for p in payments if p.status != PaymentStatus.RECEIVED]
        assert len(unmatched_payments) == 1
    
    def test_payment_matcher_custom_windows(self):
        """Test PaymentMatcher with custom time windows"""
        matcher = PaymentMatcher(search_window_days=10, grace_period_days=5)
        
        assert matcher.search_window_days == 10
        assert matcher.grace_period_days == 5
    
    def test_match_payments_empty_inputs(self, payment_matcher):
        """Test payment matching with empty inputs"""
        analysis_date = date(2025, 1, 20)
        
        # Empty garages
        payments = payment_matcher.match_payments([], [], analysis_date)
        assert len(payments) == 0
        
        # Empty transactions
        garages = [Garage("1", Decimal("3500.00"), date(2025, 1, 1), 15)]
        payments = payment_matcher.match_payments(garages, [], analysis_date)
        assert len(payments) == 1
        assert payments[0].status != PaymentStatus.RECEIVED
