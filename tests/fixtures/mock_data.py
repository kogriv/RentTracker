"""
Mock data and fixtures for testing
"""

from decimal import Decimal
from datetime import date, datetime
from typing import List, Dict, Any

from src.core.models.garage import Garage
from src.core.models.transaction import Transaction
from src.core.models.payment import Payment, PaymentStatus


class MockDataProvider:
    """Provider for mock test data"""
    
    @staticmethod
    def create_sample_garages() -> List[Garage]:
        """Create sample garage data for testing"""
        return [
            Garage("1", Decimal("3500.00"), date(2025, 1, 1), 15),
            Garage("2", Decimal("2800.00"), date(2025, 1, 2), 16),
            Garage("3", Decimal("4200.00"), date(2025, 1, 3), 17),
            Garage("4", Decimal("3100.00"), date(2025, 1, 4), 18),
            Garage("5", Decimal("2600.00"), date(2025, 1, 5), 19),
        ]
    
    @staticmethod
    def create_garages_with_duplicates() -> List[Garage]:
        """Create garage data with duplicate amounts for testing"""
        return [
            Garage("1", Decimal("3500.00"), date(2025, 1, 1), 15),
            Garage("2", Decimal("2800.00"), date(2025, 1, 2), 16),
            Garage("3", Decimal("3500.00"), date(2025, 1, 3), 17),  # Duplicate amount
            Garage("4", Decimal("4200.00"), date(2025, 1, 4), 18),
            Garage("5", Decimal("2800.00"), date(2025, 1, 5), 19),  # Another duplicate
        ]
    
    @staticmethod
    def create_garages_with_edge_cases() -> List[Garage]:
        """Create garage data with edge cases for testing"""
        return [
            Garage("feb29", Decimal("3500.00"), date(2024, 2, 29), 29),  # Leap year date
            Garage("jan31", Decimal("2800.00"), date(2025, 1, 31), 31),  # 31st day
            Garage("normal", Decimal("4200.00"), date(2025, 1, 15), 15),  # Normal case
        ]
    
    @staticmethod
    def create_sample_transactions() -> List[Transaction]:
        """Create sample transaction data for testing"""
        return [
            Transaction(date(2025, 1, 15), Decimal("3500.00"), "Перевод СБП", "sberbank_row_1"),
            Transaction(date(2025, 1, 16), Decimal("2800.00"), "Перевод на карту", "sberbank_row_2"),
            Transaction(date(2025, 1, 18), Decimal("4200.00"), "Перевод СБП", "sberbank_row_3"),
            Transaction(date(2025, 1, 19), Decimal("3100.00"), "Перевод СБП", "sberbank_row_4"),
        ]
    
    @staticmethod
    def create_transactions_with_gaps() -> List[Transaction]:
        """Create transaction data with missing amounts for testing"""
        return [
            Transaction(date(2025, 1, 15), Decimal("3500.00"), "Перевод СБП"),
            Transaction(date(2025, 1, 16), Decimal("2800.00"), "Перевод на карту"),
            # Missing: 4200.00 (garage 3 should be overdue)
            Transaction(date(2025, 1, 19), Decimal("1500.00"), "Перевод СБП"),  # Unknown amount
        ]
    
    @staticmethod
    def create_transactions_with_timing_variations() -> List[Transaction]:
        """Create transactions with various timing scenarios"""
        return [
            Transaction(date(2025, 1, 10), Decimal("3500.00"), "Перевод СБП"),  # Early payment
            Transaction(date(2025, 1, 16), Decimal("2800.00"), "Перевод на карту"),  # On time
            Transaction(date(2025, 1, 25), Decimal("4200.00"), "Перевод СБП"),  # Late payment
        ]
    
    @staticmethod
    def create_sample_payments() -> List[Payment]:
        """Create sample payment data for testing"""
        return [
            Payment(
                garage_id="1",
                amount=Decimal("3500.00"),
                expected_date=date(2025, 1, 15),
                actual_date=date(2025, 1, 15),
                status=PaymentStatus.RECEIVED,
                notes="Payment matched"
            ),
            Payment(
                garage_id="2",
                amount=Decimal("2800.00"),
                expected_date=date(2025, 1, 16),
                actual_date=date(2025, 1, 16),
                status=PaymentStatus.RECEIVED,
                notes="Payment matched"
            ),
            Payment(
                garage_id="3",
                amount=Decimal("4200.00"),
                expected_date=date(2025, 1, 17),
                actual_date=None,
                status=PaymentStatus.OVERDUE,
                days_overdue=5,
                notes="No matching payment found"
            ),
        ]
    
    @staticmethod
    def create_payments_with_all_statuses() -> List[Payment]:
        """Create payments covering all possible statuses"""
        return [
            Payment(
                garage_id="1",
                amount=Decimal("3500.00"),
                expected_date=date(2025, 1, 15),
                actual_date=date(2025, 1, 15),
                status=PaymentStatus.RECEIVED
            ),
            Payment(
                garage_id="2",
                amount=Decimal("2800.00"),
                expected_date=date(2025, 1, 16),
                actual_date=None,
                status=PaymentStatus.OVERDUE,
                days_overdue=5
            ),
            Payment(
                garage_id="3",
                amount=Decimal("4200.00"),
                expected_date=date(2025, 1, 17),
                actual_date=None,
                status=PaymentStatus.PENDING
            ),
            Payment(
                garage_id="4",
                amount=Decimal("3100.00"),
                expected_date=date(2025, 1, 25),
                actual_date=None,
                status=PaymentStatus.NOT_DUE
            ),
            Payment(
                garage_id="5",
                amount=Decimal("2600.00"),
                expected_date=date(2025, 1, 20),
                actual_date=None,
                status=PaymentStatus.UNCLEAR,
                notes="Multiple possible matches found"
            ),
        ]
    
    @staticmethod
    def create_garage_data_dict() -> List[Dict[str, Any]]:
        """Create garage data in dictionary format (as returned by parsers)"""
        return [
            {
                'id': '1',
                'monthly_rent': Decimal('3500.00'),
                'start_date': date(2025, 1, 1),
                'payment_day': 15
            },
            {
                'id': '2',
                'monthly_rent': Decimal('2800.00'),
                'start_date': date(2025, 1, 2),
                'payment_day': 16
            },
            {
                'id': '3',
                'monthly_rent': Decimal('4200.00'),
                'start_date': date(2025, 1, 3),
                'payment_day': 17
            },
        ]
    
    @staticmethod
    def create_invalid_garage_data() -> List[Dict[str, Any]]:
        """Create invalid garage data for testing error handling"""
        return [
            {
                'id': '',  # Invalid: empty ID
                'monthly_rent': Decimal('3500.00'),
                'start_date': date(2025, 1, 1),
                'payment_day': 15
            },
            {
                'id': '2',
                'monthly_rent': Decimal('-2800.00'),  # Invalid: negative amount
                'start_date': date(2025, 1, 2),
                'payment_day': 16
            },
            {
                'id': '3',
                'monthly_rent': Decimal('4200.00'),
                'start_date': date(2025, 1, 3),
                'payment_day': 35  # Invalid: payment day > 31
            },
        ]
    
    @staticmethod
    def create_excel_row_data() -> List[List[Any]]:
        """Create Excel row data for parser testing"""
        return [
            # Header row
            ["Гараж", "Сумма", "Первоначальная дата"],
            # Data rows
            ["1", 3500.00, datetime(2025, 1, 15)],
            ["2", "2,800.50", "16.01.2025"],  # String formats
            ["3", 4200, "17/01/2025"],  # Different date format
            [None, None, None],  # Empty row
            ["4", 3100.00, datetime(2025, 1, 18)],
        ]
    
    @staticmethod
    def create_sberbank_transaction_rows() -> List[List[Any]]:
        """Create Sberbank transaction row data for parser testing"""
        return [
            ["15.01.2025 14:30", "14:30", "", "Перевод СБП", "+3 500,00"],
            ["16.01.2025 15:00", "15:00", "", "Перевод на карту", "+2 800,50"],
            ["17.01.2025 16:00", "16:00", "", "Перевод СБП", "+4 200,00"],
            ["18.01.2025 17:00", "17:00", "", "Покупка", "-1 000,00"],  # Outgoing
            ["19.01.2025 18:00", "18:00", "", "Перевод СБП", "+1 500,00"],
            [None, None, None, None, None],  # Empty row
            ["Страница 1 из 5", "", "", "", ""],  # Service row
        ]
    
    @staticmethod
    def create_test_config() -> Dict[str, Any]:
        """Create test configuration"""
        return {
            "application": {
                "name": "Test Garage Payment Tracker",
                "version": "1.0.0",
                "default_language": "en"
            },
            "parsing": {
                "grace_period_days": 3,
                "search_window_days": 7,
                "amount_tolerance": 0.01
            },
            "parsers": {
                "default_statement": "sberbank_excel",
                "default_garage": "excel"
            },
            "output": {
                "format": "xlsx",
                "include_summary": True
            }
        }
    
    @staticmethod
    def create_date_scenarios() -> List[Dict[str, Any]]:
        """Create various date scenarios for testing"""
        return [
            {
                "name": "normal_month",
                "garage_start": date(2025, 1, 15),
                "target_month": date(2025, 2, 1),
                "expected_date": date(2025, 2, 15)
            },
            {
                "name": "february_leap_year",
                "garage_start": date(2024, 1, 29),
                "target_month": date(2024, 2, 1),
                "expected_date": date(2024, 2, 29)
            },
            {
                "name": "february_non_leap_year",
                "garage_start": date(2025, 1, 29),
                "target_month": date(2025, 2, 1),
                "expected_date": date(2025, 2, 28)
            },
            {
                "name": "short_month",
                "garage_start": date(2025, 1, 31),
                "target_month": date(2025, 4, 1),
                "expected_date": date(2025, 4, 30)
            },
        ]
    
    @staticmethod
    def create_amount_matching_scenarios() -> List[Dict[str, Any]]:
        """Create amount matching test scenarios"""
        return [
            {
                "name": "exact_match",
                "garage_amount": Decimal("3500.00"),
                "transaction_amount": Decimal("3500.00"),
                "tolerance": Decimal("0.01"),
                "should_match": True
            },
            {
                "name": "within_tolerance",
                "garage_amount": Decimal("3500.00"),
                "transaction_amount": Decimal("3500.01"),
                "tolerance": Decimal("0.01"),
                "should_match": True
            },
            {
                "name": "outside_tolerance",
                "garage_amount": Decimal("3500.00"),
                "transaction_amount": Decimal("3500.05"),
                "tolerance": Decimal("0.01"),
                "should_match": False
            },
            {
                "name": "large_difference",
                "garage_amount": Decimal("3500.00"),
                "transaction_amount": Decimal("3600.00"),
                "tolerance": Decimal("0.01"),
                "should_match": False
            },
        ]


class MockExcelData:
    """Mock Excel data structures for testing parsers"""
    
    @staticmethod
    def create_mock_cell(value: Any):
        """Create mock Excel cell"""
        class MockCell:
            def __init__(self, value):
                self.value = value
        
        return MockCell(value)
    
    @staticmethod
    def create_mock_row(values: List[Any]):
        """Create mock Excel row"""
        return [MockExcelData.create_mock_cell(value) for value in values]
    
    @staticmethod
    def create_mock_worksheet(rows_data: List[List[Any]]):
        """Create mock Excel worksheet"""
        class MockWorksheet:
            def __init__(self, rows_data):
                self.rows_data = rows_data
            
            def iter_rows(self, min_row=1, max_row=None, **kwargs):
                start_idx = min_row - 1
                end_idx = max_row if max_row else len(self.rows_data)
                
                for row_data in self.rows_data[start_idx:end_idx]:
                    yield MockExcelData.create_mock_row(row_data)
        
        return MockWorksheet(rows_data)
    
    @staticmethod
    def create_mock_workbook(rows_data: List[List[Any]]):
        """Create mock Excel workbook"""
        class MockWorkbook:
            def __init__(self, rows_data):
                self.active = MockExcelData.create_mock_worksheet(rows_data)
                self.closed = False
            
            def close(self):
                self.closed = True
        
        return MockWorkbook(rows_data)


# Commonly used test fixtures as module-level variables
SAMPLE_GARAGES = MockDataProvider.create_sample_garages()
SAMPLE_TRANSACTIONS = MockDataProvider.create_sample_transactions()
SAMPLE_PAYMENTS = MockDataProvider.create_sample_payments()
GARAGES_WITH_DUPLICATES = MockDataProvider.create_garages_with_duplicates()
PAYMENTS_ALL_STATUSES = MockDataProvider.create_payments_with_all_statuses()
