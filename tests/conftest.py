"""
Pytest configuration and shared fixtures
"""

import pytest
import tempfile
import logging
from pathlib import Path
from decimal import Decimal
from datetime import date
from unittest.mock import Mock
from typing import List

from src.core.models.garage import Garage
from src.core.models.transaction import Transaction
from src.core.models.payment import Payment, PaymentStatus
from src.parsers.base.parser_factory import ParserFactory
from src.core.services.payment_matcher import PaymentMatcher
from src.core.services.date_calculator import DateCalculator
from src.core.services.status_determiner import StatusDeterminer
from src.infrastructure.localization.i18n import LocalizationManager
from tests.fixtures.mock_data import MockDataProvider


# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)


@pytest.fixture(scope="session")
def temp_dir():
    """Create temporary directory for test session"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_garages():
    """Fixture providing sample garage data"""
    return MockDataProvider.create_sample_garages()


@pytest.fixture
def garages_with_duplicates():
    """Fixture providing garage data with duplicate amounts"""
    return MockDataProvider.create_garages_with_duplicates()


@pytest.fixture
def garages_with_edge_cases():
    """Fixture providing garage data with edge cases"""
    return MockDataProvider.create_garages_with_edge_cases()


@pytest.fixture
def sample_transactions():
    """Fixture providing sample transaction data"""
    return MockDataProvider.create_sample_transactions()


@pytest.fixture
def transactions_with_gaps():
    """Fixture providing transaction data with missing amounts"""
    return MockDataProvider.create_transactions_with_gaps()


@pytest.fixture
def transactions_with_timing_variations():
    """Fixture providing transactions with various timing scenarios"""
    return MockDataProvider.create_transactions_with_timing_variations()


@pytest.fixture
def sample_payments():
    """Fixture providing sample payment data"""
    return MockDataProvider.create_sample_payments()


@pytest.fixture
def payments_all_statuses():
    """Fixture providing payments with all possible statuses"""
    return MockDataProvider.create_payments_with_all_statuses()


@pytest.fixture
def garage_data_dict():
    """Fixture providing garage data in dictionary format"""
    return MockDataProvider.create_garage_data_dict()


@pytest.fixture
def invalid_garage_data():
    """Fixture providing invalid garage data for error testing"""
    return MockDataProvider.create_invalid_garage_data()


@pytest.fixture
def excel_row_data():
    """Fixture providing Excel row data for parser testing"""
    return MockDataProvider.create_excel_row_data()


@pytest.fixture
def sberbank_transaction_rows():
    """Fixture providing Sberbank transaction row data"""
    return MockDataProvider.create_sberbank_transaction_rows()


@pytest.fixture
def test_config():
    """Fixture providing test configuration"""
    return MockDataProvider.create_test_config()


@pytest.fixture
def date_scenarios():
    """Fixture providing various date scenarios"""
    return MockDataProvider.create_date_scenarios()


@pytest.fixture
def amount_matching_scenarios():
    """Fixture providing amount matching test scenarios"""
    return MockDataProvider.create_amount_matching_scenarios()


@pytest.fixture
def parser_factory():
    """Fixture providing ParserFactory instance"""
    return ParserFactory()


@pytest.fixture
def payment_matcher():
    """Fixture providing PaymentMatcher instance"""
    return PaymentMatcher(search_window_days=7, grace_period_days=3)


@pytest.fixture
def date_calculator():
    """Fixture providing DateCalculator instance"""
    return DateCalculator()


@pytest.fixture
def status_determiner():
    """Fixture providing StatusDeterminer instance"""
    return StatusDeterminer(grace_period_days=3)


@pytest.fixture
def localization_manager():
    """Fixture providing LocalizationManager instance"""
    return LocalizationManager("en")


@pytest.fixture
def mock_parser_factory():
    """Fixture providing mock ParserFactory"""
    return Mock(spec=ParserFactory)


@pytest.fixture
def mock_payment_matcher():
    """Fixture providing mock PaymentMatcher"""
    return Mock(spec=PaymentMatcher)


# Analysis date fixtures
@pytest.fixture
def analysis_date_current():
    """Fixture providing current analysis date"""
    return date(2025, 1, 20)


@pytest.fixture
def analysis_date_early():
    """Fixture providing early analysis date (before expected payments)"""
    return date(2024, 12, 15)


@pytest.fixture
def analysis_date_late():
    """Fixture providing late analysis date (well after expected payments)"""
    return date(2025, 2, 15)


# Common test scenarios
@pytest.fixture
def perfect_match_scenario(sample_garages, sample_transactions):
    """Fixture providing perfect matching scenario"""
    return {
        'garages': sample_garages,
        'transactions': sample_transactions,
        'analysis_date': date(2025, 1, 20)
    }


@pytest.fixture
def no_match_scenario(sample_garages):
    """Fixture providing no matching transactions scenario"""
    # Transactions with different amounts that don't match garages
    no_match_transactions = [
        Transaction(date(2025, 1, 15), Decimal("1000.00"), "Перевод СБП"),
        Transaction(date(2025, 1, 16), Decimal("2000.00"), "Перевод на карту"),
    ]
    
    return {
        'garages': sample_garages,
        'transactions': no_match_transactions,
        'analysis_date': date(2025, 1, 20)
    }


@pytest.fixture
def duplicate_amounts_scenario(garages_with_duplicates):
    """Fixture providing duplicate amounts scenario"""
    # Transactions that match duplicate amounts
    duplicate_transactions = [
        Transaction(date(2025, 1, 15), Decimal("3500.00"), "Перевод СБП"),  # Matches garages 1 and 3
        Transaction(date(2025, 1, 16), Decimal("2800.00"), "Перевод на карту"),  # Matches garages 2 and 5
        Transaction(date(2025, 1, 18), Decimal("4200.00"), "Перевод СБП"),  # Matches garage 4
    ]
    
    return {
        'garages': garages_with_duplicates,
        'transactions': duplicate_transactions,
        'analysis_date': date(2025, 1, 20)
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "parser: mark test as parser-related"
    )
    config.addinivalue_line(
        "markers", "service: mark test as service-related"
    )
    config.addinivalue_line(
        "markers", "cli: mark test as CLI-related"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add markers based on test file name
        if "parser" in str(item.fspath):
            item.add_marker(pytest.mark.parser)
        elif "service" in str(item.fspath):
            item.add_marker(pytest.mark.service)
        elif "cli" in str(item.fspath):
            item.add_marker(pytest.mark.cli)


# Helper functions for tests
def create_test_garage(garage_id: str, amount: float, day: int) -> Garage:
    """Helper function to create test garage"""
    return Garage(
        id=garage_id,
        monthly_rent=Decimal(str(amount)),
        start_date=date(2025, 1, day),
        payment_day=day
    )


def create_test_transaction(day: int, amount: float, category: str = "Перевод СБП") -> Transaction:
    """Helper function to create test transaction"""
    return Transaction(
        date=date(2025, 1, day),
        amount=Decimal(str(amount)),
        category=category
    )


def create_test_payment(garage_id: str, amount: float, expected_day: int, 
                       status: PaymentStatus = PaymentStatus.NOT_DUE,
                       actual_day: int = None) -> Payment:
    """Helper function to create test payment"""
    actual_date = date(2025, 1, actual_day) if actual_day else None
    
    return Payment(
        garage_id=garage_id,
        amount=Decimal(str(amount)),
        expected_date=date(2025, 1, expected_day),
        actual_date=actual_date,
        status=status
    )


# Assertion helpers
def assert_payment_status_counts(payments: List[Payment], expected_counts: dict):
    """Assert payment status counts match expected values"""
    actual_counts = {}
    for payment in payments:
        status = payment.status
        actual_counts[status] = actual_counts.get(status, 0) + 1
    
    for status, expected_count in expected_counts.items():
        actual_count = actual_counts.get(status, 0)
        assert actual_count == expected_count, \
            f"Expected {expected_count} payments with status {status.value}, got {actual_count}"


def assert_garage_payment_exists(payments: List[Payment], garage_id: str) -> Payment:
    """Assert that a payment exists for a specific garage and return it"""
    payment = next((p for p in payments if p.garage_id == garage_id), None)
    assert payment is not None, f"No payment found for garage {garage_id}"
    return payment


def assert_amount_matches(actual: Decimal, expected: Decimal, tolerance: Decimal = Decimal("0.01")):
    """Assert that two amounts match within tolerance"""
    diff = abs(actual - expected)
    assert diff <= tolerance, f"Amount difference {diff} exceeds tolerance {tolerance}"


# Custom pytest fixtures for specific test scenarios
@pytest.fixture
def february_edge_case():
    """Fixture for February date edge cases"""
    return {
        'leap_year_garage': create_test_garage("leap", 3500.00, 29),
        'non_leap_target': date(2025, 2, 1),  # 2025 is not a leap year
        'expected_adjusted_date': date(2025, 2, 28)
    }


@pytest.fixture
def month_end_edge_case():
    """Fixture for month-end date edge cases"""
    return {
        'garage_31st': create_test_garage("31st", 3500.00, 31),
        'april_target': date(2025, 4, 1),  # April has 30 days
        'expected_adjusted_date': date(2025, 4, 30)
    }


# Performance testing fixtures
@pytest.fixture
def large_dataset():
    """Fixture providing large dataset for performance testing"""
    garages = []
    transactions = []
    
    # Create 100 garages
    for i in range(1, 101):
        garages.append(create_test_garage(str(i), 3000 + i * 10, 15))
    
    # Create 80 matching transactions (some gaps for realism)
    for i in range(1, 81):
        transactions.append(create_test_transaction(15, 3000 + i * 10))
    
    return {
        'garages': garages,
        'transactions': transactions,
        'analysis_date': date(2025, 1, 20)
    }


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_logging():
    """Automatically cleanup logging after each test"""
    yield
    # Reset logging level after test
    logging.getLogger().setLevel(logging.WARNING)


@pytest.fixture(autouse=True)
def reset_mocks():
    """Automatically reset all mocks after each test"""
    yield
    # Any cleanup code would go here if needed
    pass
