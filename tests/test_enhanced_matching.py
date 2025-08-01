"""
Tests for enhanced payment matching with fallback search
"""

import unittest
from datetime import date, timedelta
from decimal import Decimal

import sys
sys.path.insert(0, 'src')

from src.core.services.payment_matcher import PaymentMatcher
from src.core.models.garage import Garage
from src.core.models.transaction import Transaction


class TestEnhancedMatching(unittest.TestCase):
    """Test enhanced payment matching with fallback search"""
    
    def setUp(self):
        self.matcher = PaymentMatcher(search_window_days=7, grace_period_days=3)
        
        # Create test garage
        self.garage = Garage(
            id="1",
            monthly_rent=Decimal("4295.00"),
            start_date=date(2025, 1, 1),
            payment_day=1
        )
    
    def test_normal_window_match(self):
        """Test matching within normal search window"""
        analysis_date = date(2025, 5, 1)
        expected_date = date(2025, 5, 1)  # 1st of May
        
        # Transaction within search window (7 days before expected)
        transactions = [
            Transaction(
                date=date(2025, 4, 28),  # 3 days before expected
                amount=Decimal("4295.00"),
                category="Transfer",
                source="test"
            )
        ]
        
        payments = self.matcher.match_payments([self.garage], transactions, analysis_date)
        
        self.assertEqual(len(payments), 1)
        self.assertEqual(payments[0].status.value, "received")
        self.assertEqual(payments[0].actual_date, date(2025, 4, 28))
        self.assertNotIn("Wide search", payments[0].notes)
    
    def test_fallback_search_match(self):
        """Test fallback search when normal window fails"""
        analysis_date = date(2025, 5, 1)
        
        # Transaction outside normal window but within statement period
        transactions = [
            Transaction(
                date=date(2025, 5, 31),  # 30 days after expected (outside normal window)
                amount=Decimal("4295.00"),
                category="Transfer",
                source="test"
            )
        ]
        
        payments = self.matcher.match_payments([self.garage], transactions, analysis_date)
        
        self.assertEqual(len(payments), 1)
        self.assertEqual(payments[0].status.value, "received")
        self.assertEqual(payments[0].actual_date, date(2025, 5, 31))
        self.assertIn("Wide search match", payments[0].notes)
    
    def test_fallback_multiple_candidates(self):
        """Test fallback search with multiple candidates - should pick earliest"""
        analysis_date = date(2025, 5, 1)
        
        # Multiple transactions with same amount, outside normal window
        transactions = [
            Transaction(
                date=date(2025, 5, 31),  # Later transaction
                amount=Decimal("4295.00"),
                category="Transfer",
                source="test1"
            ),
            Transaction(
                date=date(2025, 5, 15),  # Earlier transaction (should be selected)
                amount=Decimal("4295.00"),
                category="Transfer",
                source="test2"
            ),
            Transaction(
                date=date(2025, 6, 1),   # Latest transaction
                amount=Decimal("4295.00"),
                category="Transfer",
                source="test3"
            )
        ]
        
        payments = self.matcher.match_payments([self.garage], transactions, analysis_date)
        
        self.assertEqual(len(payments), 1)
        self.assertEqual(payments[0].status.value, "received")
        self.assertEqual(payments[0].actual_date, date(2025, 5, 15))  # Earliest
        self.assertIn("earliest of 3 matches", payments[0].notes)
    
    def test_no_match_anywhere(self):
        """Test when no matching transaction exists anywhere"""
        analysis_date = date(2025, 5, 1)
        
        # No matching transactions
        transactions = [
            Transaction(
                date=date(2025, 5, 15),
                amount=Decimal("3500.00"),  # Different amount
                category="Transfer",
                source="test"
            )
        ]
        
        payments = self.matcher.match_payments([self.garage], transactions, analysis_date)
        
        self.assertEqual(len(payments), 1)
        self.assertNotEqual(payments[0].status.value, "received")
        self.assertIsNone(payments[0].actual_date)
        self.assertEqual(payments[0].notes, "No matching payment found")
    
    def test_normal_window_preferred_over_fallback(self):
        """Test that normal window match is preferred over fallback"""
        analysis_date = date(2025, 5, 1)
        
        # One transaction in normal window, one outside
        transactions = [
            Transaction(
                date=date(2025, 4, 28),  # Within normal window
                amount=Decimal("4295.00"),
                category="Transfer",
                source="normal"
            ),
            Transaction(
                date=date(2025, 5, 31),  # Outside normal window
                amount=Decimal("4295.00"),
                category="Transfer",
                source="fallback"
            )
        ]
        
        payments = self.matcher.match_payments([self.garage], transactions, analysis_date)
        
        self.assertEqual(len(payments), 1)
        self.assertEqual(payments[0].status.value, "received")
        self.assertEqual(payments[0].actual_date, date(2025, 4, 28))  # Normal window match
        self.assertNotIn("Wide search", payments[0].notes)


if __name__ == '__main__':
    unittest.main()