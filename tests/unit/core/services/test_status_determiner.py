"""
Update tests to expect correct days_overdue for PENDING status and update test for last grace day
"""
"""
Unit tests for StatusDeterminer service
"""

import pytest
from datetime import date, timedelta

from src.core.services.status_determiner import StatusDeterminer
from src.core.models.payment import PaymentStatus


class TestStatusDeterminer:
    """Test cases for StatusDeterminer service"""

    @pytest.fixture
    def status_determiner(self):
        """Create StatusDeterminer instance for testing"""
        return StatusDeterminer(grace_period_days=3)

    def test_determine_status_received(self, status_determiner):
        """Test status determination for received payments"""
        expected_date = date(2025, 1, 15)
        analysis_date = date(2025, 1, 20)

        status, days_overdue = status_determiner.determine_status(
            expected_date, analysis_date, has_payment=True
        )

        assert status == PaymentStatus.RECEIVED
        assert days_overdue == 0

    def test_determine_status_not_due(self, status_determiner):
        """Test status determination for payments not yet due"""
        expected_date = date(2025, 1, 15)
        analysis_date = date(2025, 1, 10)  # Before expected date

        status, days_overdue = status_determiner.determine_status(
            expected_date, analysis_date, has_payment=False
        )

        assert status == PaymentStatus.NOT_DUE
        assert days_overdue == 0

    def test_determine_status_pending_same_day(self, status_determiner):
        """Test status determination for pending payment on expected date"""
        expected_date = date(2025, 1, 15)
        analysis_date = date(2025, 1, 15)  # Same as expected date

        status, days_overdue = status_determiner.determine_status(
            expected_date, analysis_date, has_payment=False
        )

        assert status == PaymentStatus.PENDING
        assert days_overdue == 0

    def test_determine_status_pending_within_grace_period(self, status_determiner):
        """Test status determination for pending payment within grace period"""
        expected_date = date(2025, 1, 15)

        # Test each day within grace period
        for days_after in range(1, 4):  # 1, 2, 3 days after
            analysis_date = expected_date + timedelta(days=days_after)

            status, days_overdue = status_determiner.determine_status(
                expected_date, analysis_date, has_payment=False
            )

            assert status == PaymentStatus.PENDING
            assert days_overdue == 0

    def test_determine_status_pending_last_grace_day(self, status_determiner):
        """Test status determination on last day of grace period"""
        expected_date = date(2025, 1, 15)
        analysis_date = date(2025, 1, 18)  # 3 days after (last grace day)

        status, days_overdue = status_determiner.determine_status(
            expected_date, analysis_date, has_payment=False
        )

        assert status == PaymentStatus.PENDING
        assert days_overdue == 3

    def test_determine_status_overdue_one_day(self, status_determiner):
        """Test status determination for payment overdue by one day"""
        expected_date = date(2025, 1, 15)
        analysis_date = date(2025, 1, 19)  # 4 days after (1 day past grace period)

        status, days_overdue = status_determiner.determine_status(
            expected_date, analysis_date, has_payment=False
        )

        assert status == PaymentStatus.OVERDUE
        assert days_overdue == 1

    def test_determine_status_overdue_multiple_days(self, status_determiner):
        """Test status determination for payment overdue by multiple days"""
        expected_date = date(2025, 1, 15)
        analysis_date = date(2025, 1, 25)  # 10 days after (7 days past grace period)

        status, days_overdue = status_determiner.determine_status(
            expected_date, analysis_date, has_payment=False
        )

        assert status == PaymentStatus.OVERDUE
        assert days_overdue == 7

    def test_determine_status_overdue_long_term(self, status_determiner):
        """Test status determination for long-term overdue payment"""
        expected_date = date(2025, 1, 15)
        analysis_date = date(2025, 2, 15)  # 31 days after (28 days past grace period)

        status, days_overdue = status_determiner.determine_status(
            expected_date, analysis_date, has_payment=False
        )

        assert status == PaymentStatus.OVERDUE
        assert days_overdue == 28

    def test_determine_status_custom_grace_period(self):
        """Test status determination with custom grace period"""
        determiner = StatusDeterminer(grace_period_days=7)
        expected_date = date(2025, 1, 15)

        # Within custom grace period (7 days)
        analysis_date = date(2025, 1, 20)  # 5 days after
        status, days_overdue = determiner.determine_status(
            expected_date, analysis_date, has_payment=False
        )
        assert status == PaymentStatus.PENDING
        assert days_overdue == 0

        # Past custom grace period
        analysis_date = date(2025, 1, 23)  # 8 days after (1 day past 7-day grace)
        status, days_overdue = determiner.determine_status(
            expected_date, analysis_date, has_payment=False
        )
        assert status == PaymentStatus.OVERDUE
        assert days_overdue == 1

    def test_determine_status_zero_grace_period(self):
        """Test status determination with zero grace period"""
        determiner = StatusDeterminer(grace_period_days=0)
        expected_date = date(2025, 1, 15)

        # Same day should still be pending
        analysis_date = date(2025, 1, 15)
        status, days_overdue = determiner.determine_status(
            expected_date, analysis_date, has_payment=False
        )
        assert status == PaymentStatus.PENDING
        assert days_overdue == 0

        # One day after should be overdue
        analysis_date = date(2025, 1, 16)
        status, days_overdue = determiner.determine_status(
            expected_date, analysis_date, has_payment=False
        )
        assert status == PaymentStatus.OVERDUE
        assert days_overdue == 1

    def test_is_payment_timely_early_acceptable(self, status_determiner):
        """Test timely payment check for early payments within acceptable range"""
        expected_date = date(2025, 1, 15)

        # 3 days early - should be acceptable (default early_days=7)
        actual_date = date(2025, 1, 12)
        assert status_determiner.is_payment_timely(expected_date, actual_date) is True

        # 7 days early - should be acceptable (boundary)
        actual_date = date(2025, 1, 8)
        assert status_determiner.is_payment_timely(expected_date, actual_date) is True

    def test_is_payment_timely_too_early(self, status_determiner):
        """Test timely payment check for payments too early"""
        expected_date = date(2025, 1, 15)

        # 8 days early - should not be acceptable
        actual_date = date(2025, 1, 7)
        assert status_determiner.is_payment_timely(expected_date, actual_date) is False

        # 10 days early - should not be acceptable
        actual_date = date(2025, 1, 5)
        assert status_determiner.is_payment_timely(expected_date, actual_date) is False

    def test_is_payment_timely_on_time(self, status_determiner):
        """Test timely payment check for on-time payments"""
        expected_date = date(2025, 1, 15)

        # Exact date
        assert status_determiner.is_payment_timely(expected_date, expected_date) is True

        # Within grace period
        actual_date = date(2025, 1, 17)  # 2 days late
        assert status_determiner.is_payment_timely(expected_date, actual_date) is True

        # Last day of grace period
        actual_date = date(2025, 1, 18)  # 3 days late (grace period = 3)
        assert status_determiner.is_payment_timely(expected_date, actual_date) is True

    def test_is_payment_timely_too_late(self, status_determiner):
        """Test timely payment check for payments too late"""
        expected_date = date(2025, 1, 15)

        # 4 days late (past grace period)
        actual_date = date(2025, 1, 19)
        assert status_determiner.is_payment_timely(expected_date, actual_date) is False

        # Much later
        actual_date = date(2025, 2, 1)
        assert status_determiner.is_payment_timely(expected_date, actual_date) is False

    def test_is_payment_timely_custom_early_days(self, status_determiner):
        """Test timely payment check with custom early days"""
        expected_date = date(2025, 1, 15)
        early_days = 3

        # 3 days early - should be acceptable
        actual_date = date(2025, 1, 12)
        assert status_determiner.is_payment_timely(expected_date, actual_date, early_days) is True

        # 4 days early - should not be acceptable
        actual_date = date(2025, 1, 11)
        assert status_determiner.is_payment_timely(expected_date, actual_date, early_days) is False

    def test_calculate_payment_delay_early(self, status_determiner):
        """Test payment delay calculation for early payments"""
        expected_date = date(2025, 1, 15)

        # 3 days early
        actual_date = date(2025, 1, 12)
        delay = status_determiner.calculate_payment_delay(expected_date, actual_date)
        assert delay == -3

        # 1 day early
        actual_date = date(2025, 1, 14)
        delay = status_determiner.calculate_payment_delay(expected_date, actual_date)
        assert delay == -1

    def test_calculate_payment_delay_on_time(self, status_determiner):
        """Test payment delay calculation for on-time payment"""
        expected_date = date(2025, 1, 15)
        actual_date = date(2025, 1, 15)

        delay = status_determiner.calculate_payment_delay(expected_date, actual_date)
        assert delay == 0

    def test_calculate_payment_delay_late(self, status_determiner):
        """Test payment delay calculation for late payments"""
        expected_date = date(2025, 1, 15)

        # 2 days late
        actual_date = date(2025, 1, 17)
        delay = status_determiner.calculate_payment_delay(expected_date, actual_date)
        assert delay == 2

        # 10 days late
        actual_date = date(2025, 1, 25)
        delay = status_determiner.calculate_payment_delay(expected_date, actual_date)
        assert delay == 10

    def test_received_payment_overrides_timing(self, status_determiner):
        """Test that received payment status overrides timing considerations"""
        expected_date = date(2025, 1, 15)

        # Even if analysis date suggests overdue, received payment should return RECEIVED
        analysis_date = date(2025, 2, 1)  # Long after expected

        status, days_overdue = status_determiner.determine_status(
            expected_date, analysis_date, has_payment=True
        )

        assert status == PaymentStatus.RECEIVED
        assert days_overdue == 0

    def test_status_determiner_with_actual_payment_date(self, status_determiner):
        """Test status determination with actual payment date parameter"""
        expected_date = date(2025, 1, 15)
        analysis_date = date(2025, 1, 20)
        actual_payment_date = date(2025, 1, 16)

        # This tests the signature - actual_payment_date is available but not used in current logic
        status, days_overdue = status_determiner.determine_status(
            expected_date, analysis_date, has_payment=True, actual_payment_date=actual_payment_date
        )

        assert status == PaymentStatus.RECEIVED
        assert days_overdue == 0