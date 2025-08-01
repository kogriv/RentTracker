"""
Unit tests for ProcessPaymentsUseCase
"""

import pytest
from pathlib import Path
from decimal import Decimal
from datetime import date
from unittest.mock import Mock, patch, MagicMock

from src.application.use_cases.process_payments import ProcessPaymentsUseCase
from src.application.dto.payment_request import PaymentProcessRequest
from src.core.models.garage import Garage
from src.core.models.transaction import Transaction
from src.core.models.payment import Payment, PaymentStatus
from src.core.models.report import PaymentReport
from src.parsers.base.parser_factory import ParserFactory
from src.core.services.payment_matcher import PaymentMatcher
from src.core.exceptions import ParseError, ValidationError, DataIntegrityError


class TestProcessPaymentsUseCase:
    """Test cases for ProcessPaymentsUseCase"""
    
    @pytest.fixture
    def mock_parser_factory(self):
        """Create mock parser factory"""
        return Mock(spec=ParserFactory)
    
    @pytest.fixture
    def mock_payment_matcher(self):
        """Create mock payment matcher"""
        return Mock(spec=PaymentMatcher)
    
    @pytest.fixture
    def use_case(self, mock_parser_factory, mock_payment_matcher):
        """Create ProcessPaymentsUseCase instance for testing"""
        return ProcessPaymentsUseCase(
            parser_factory=mock_parser_factory,
            payment_matcher=mock_payment_matcher,
            search_window_days=7,
            grace_period_days=3
        )
    
    @pytest.fixture
    def sample_request(self):
        """Create sample payment process request"""
        return PaymentProcessRequest(
            garage_file=Path("test_garage.xlsx"),
            statement_file=Path("test_statement.xlsx"),
            analysis_date=date(2025, 1, 20)
        )
    
    @pytest.fixture
    def sample_garages(self):
        """Create sample garage data"""
        return [
            Garage("1", Decimal("3500.00"), date(2025, 1, 1), 15),
            Garage("2", Decimal("2800.00"), date(2025, 1, 2), 16),
            Garage("3", Decimal("4200.00"), date(2025, 1, 3), 17),
        ]
    
    @pytest.fixture
    def sample_transactions(self):
        """Create sample transaction data"""
        return [
            Transaction(date(2025, 1, 15), Decimal("3500.00"), "Перевод СБП"),
            Transaction(date(2025, 1, 16), Decimal("2800.00"), "Перевод на карту"),
            Transaction(date(2025, 1, 18), Decimal("4200.00"), "Перевод СБП"),
        ]
    
    @pytest.fixture
    def sample_payments(self, sample_garages):
        """Create sample payment data"""
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
                actual_date=date(2025, 1, 16),
                status=PaymentStatus.RECEIVED
            ),
            Payment(
                garage_id="3",
                amount=Decimal("4200.00"),
                expected_date=date(2025, 1, 17),
                actual_date=None,
                status=PaymentStatus.OVERDUE,
                days_overdue=3
            ),
        ]
    
    def test_execute_successful_processing(self, use_case, sample_request, sample_garages, 
                                         sample_transactions, sample_payments,
                                         mock_parser_factory, mock_payment_matcher):
        """Test successful payment processing"""
        # Setup mocks
        mock_garage_parser = Mock()
        mock_statement_parser = Mock()
        
        mock_parser_factory.create_garage_parser.return_value = mock_garage_parser
        mock_parser_factory.create_statement_parser.return_value = mock_statement_parser
        
        # Mock garage data (raw format from parser)
        garage_data = [
            {'id': '1', 'monthly_rent': Decimal('3500.00'), 'start_date': date(2025, 1, 1), 'payment_day': 15},
            {'id': '2', 'monthly_rent': Decimal('2800.00'), 'start_date': date(2025, 1, 2), 'payment_day': 16},
            {'id': '3', 'monthly_rent': Decimal('4200.00'), 'start_date': date(2025, 1, 3), 'payment_day': 17},
        ]
        
        mock_garage_parser.parse_garages.return_value = garage_data
        mock_statement_parser.parse_transactions.return_value = sample_transactions
        mock_payment_matcher.match_payments.return_value = sample_payments
        
        # Execute use case
        response = use_case.execute(sample_request)
        
        # Verify response
        assert response.success is True
        assert response.report is not None
        assert len(response.errors) == 0
        assert isinstance(response.report, PaymentReport)
        
        # Verify method calls
        mock_parser_factory.create_garage_parser.assert_called_once()
        mock_parser_factory.create_statement_parser.assert_called_once()
        mock_garage_parser.parse_garages.assert_called_once_with(sample_request.garage_file)
        mock_statement_parser.parse_transactions.assert_called_once_with(sample_request.statement_file)
        mock_payment_matcher.match_payments.assert_called_once()
    
    def test_execute_garage_parsing_error(self, use_case, sample_request, mock_parser_factory):
        """Test handling of garage parsing error"""
        # Setup mock to raise exception
        mock_garage_parser = Mock()
        mock_garage_parser.parse_garages.side_effect = Exception("Failed to parse garage file")
        mock_parser_factory.create_garage_parser.return_value = mock_garage_parser
        
        # Execute use case
        response = use_case.execute(sample_request)
        
        # Verify error handling
        assert response.success is False
        assert response.report is None
        assert len(response.errors) == 1
        assert "Failed to parse garage file" in response.errors[0]
    
    def test_execute_statement_parsing_error(self, use_case, sample_request, sample_garages,
                                           mock_parser_factory, mock_payment_matcher):
        """Test handling of statement parsing error"""
        # Setup mocks
        mock_garage_parser = Mock()
        mock_statement_parser = Mock()
        
        garage_data = [
            {'id': '1', 'monthly_rent': Decimal('3500.00'), 'start_date': date(2025, 1, 1), 'payment_day': 15}
        ]
        
        mock_garage_parser.parse_garages.return_value = garage_data
        mock_statement_parser.parse_transactions.side_effect = Exception("Failed to parse statement file")
        
        mock_parser_factory.create_garage_parser.return_value = mock_garage_parser
        mock_parser_factory.create_statement_parser.return_value = mock_statement_parser
        
        # Execute use case
        response = use_case.execute(sample_request)
        
        # Verify error handling
        assert response.success is False
        assert response.report is None
        assert len(response.errors) == 1
        assert "Failed to parse statement file" in response.errors[0]
    
    def test_parse_garage_registry_successful(self, use_case, mock_parser_factory):
        """Test successful garage registry parsing"""
        mock_parser = Mock()
        garage_data = [
            {'id': '1', 'monthly_rent': Decimal('3500.00'), 'start_date': date(2025, 1, 1), 'payment_day': 15},
            {'id': '2', 'monthly_rent': Decimal('2800.00'), 'start_date': date(2025, 1, 2), 'payment_day': 16},
        ]
        mock_parser.parse_garages.return_value = garage_data
        mock_parser_factory.create_garage_parser.return_value = mock_parser
        
        test_file = Path("test.xlsx")
        garages = use_case._parse_garage_registry(test_file)
        
        assert len(garages) == 2
        assert isinstance(garages[0], Garage)
        assert garages[0].id == "1"
        assert garages[0].monthly_rent == Decimal("3500.00")
        assert garages[1].id == "2"
        assert garages[1].monthly_rent == Decimal("2800.00")
    
    def test_parse_garage_registry_parse_error(self, use_case, mock_parser_factory):
        """Test garage registry parsing with parse error"""
        mock_parser = Mock()
        mock_parser.parse_garages.side_effect = Exception("Parse failed")
        mock_parser_factory.create_garage_parser.return_value = mock_parser
        
        test_file = Path("test.xlsx")
        
        with pytest.raises(ParseError, match="Failed to parse garage registry"):
            use_case._parse_garage_registry(test_file)
    
    def test_parse_bank_statement_successful(self, use_case, mock_parser_factory, sample_transactions):
        """Test successful bank statement parsing"""
        mock_parser = Mock()
        mock_parser.parse_transactions.return_value = sample_transactions
        mock_parser_factory.create_statement_parser.return_value = mock_parser
        
        test_file = Path("test.xlsx")
        transactions = use_case._parse_bank_statement(test_file)
        
        assert len(transactions) == 3
        assert transactions[0].amount == Decimal("3500.00")
        assert transactions[1].amount == Decimal("2800.00")
        assert transactions[2].amount == Decimal("4200.00")
    
    def test_parse_bank_statement_parse_error(self, use_case, mock_parser_factory):
        """Test bank statement parsing with parse error"""
        mock_parser = Mock()
        mock_parser.parse_transactions.side_effect = Exception("Parse failed")
        mock_parser_factory.create_statement_parser.return_value = mock_parser
        
        test_file = Path("test.xlsx")
        
        with pytest.raises(ParseError, match="Failed to parse bank statement"):
            use_case._parse_bank_statement(test_file)
    
    def test_validate_data_integrity_no_issues(self, use_case, sample_garages):
        """Test data integrity validation with no issues"""
        warnings = use_case._validate_data_integrity(sample_garages)
        
        assert len(warnings) == 0
    
    def test_validate_data_integrity_duplicate_amounts(self, use_case):
        """Test data integrity validation with duplicate amounts"""
        garages_with_duplicates = [
            Garage("1", Decimal("3500.00"), date(2025, 1, 1), 15),
            Garage("2", Decimal("2800.00"), date(2025, 1, 2), 16),
            Garage("3", Decimal("3500.00"), date(2025, 1, 3), 17),  # Duplicate amount
        ]
        
        warnings = use_case._validate_data_integrity(garages_with_duplicates)
        
        assert len(warnings) >= 1
        assert any("Duplicate rental amount" in warning for warning in warnings)
        assert any("3500" in warning for warning in warnings)
        assert any("1, 3" in warning for warning in warnings)
    
    def test_validate_data_integrity_unusual_payment_days(self, use_case):
        """Test data integrity validation with unusual payment days"""
        garages_with_unusual_days = [
            Garage("1", Decimal("3500.00"), date(2025, 1, 1), 15),
            Garage("2", Decimal("2800.00"), date(2025, 1, 2), 29),  # Unusual day
            Garage("3", Decimal("4200.00"), date(2025, 1, 3), 31),  # Unusual day
        ]
        
        warnings = use_case._validate_data_integrity(garages_with_unusual_days)
        
        assert len(warnings) >= 1
        assert any("payment days > 28" in warning for warning in warnings)
        assert any("2, 3" in warning for warning in warnings)
    
    def test_validate_data_integrity_multiple_issues(self, use_case):
        """Test data integrity validation with multiple issues"""
        problematic_garages = [
            Garage("1", Decimal("3500.00"), date(2025, 1, 1), 31),  # Unusual day
            Garage("2", Decimal("3500.00"), date(2025, 1, 2), 29),  # Duplicate amount + unusual day
            Garage("3", Decimal("4200.00"), date(2025, 1, 3), 30),  # Unusual day
        ]
        
        warnings = use_case._validate_data_integrity(problematic_garages)
        
        # Should have warnings for both duplicates and unusual days
        assert len(warnings) >= 2
        assert any("Duplicate rental amount" in warning for warning in warnings)
        assert any("payment days > 28" in warning for warning in warnings)
    
    def test_execute_with_warnings_but_success(self, use_case, sample_request, mock_parser_factory, 
                                             mock_payment_matcher):
        """Test successful execution with validation warnings"""
        # Setup mocks with problematic data
        mock_garage_parser = Mock()
        mock_statement_parser = Mock()
        
        garage_data = [
            {'id': '1', 'monthly_rent': Decimal('3500.00'), 'start_date': date(2025, 1, 1), 'payment_day': 15},
            {'id': '2', 'monthly_rent': Decimal('3500.00'), 'start_date': date(2025, 1, 2), 'payment_day': 31},  # Duplicate + unusual day
        ]
        
        mock_garage_parser.parse_garages.return_value = garage_data
        mock_statement_parser.parse_transactions.return_value = []
        
        mock_parser_factory.create_garage_parser.return_value = mock_garage_parser
        mock_parser_factory.create_statement_parser.return_value = mock_statement_parser
        
        # Mock payment matching
        payments = [
            Payment("1", Decimal("3500.00"), date(2025, 1, 15), status=PaymentStatus.OVERDUE),
            Payment("2", Decimal("3500.00"), date(2025, 1, 31), status=PaymentStatus.OVERDUE),
        ]
        mock_payment_matcher.match_payments.return_value = payments
        
        # Execute use case
        response = use_case.execute(sample_request)
        
        # Should succeed but have warnings
        assert response.success is True
        assert response.report is not None
        assert len(response.warnings) > 0
        assert any("Duplicate rental amount" in warning for warning in response.warnings)
    
    def test_execute_creates_proper_report(self, use_case, sample_request, sample_garages,
                                         sample_transactions, sample_payments,
                                         mock_parser_factory, mock_payment_matcher):
        """Test that execute creates a proper PaymentReport"""
        # Setup mocks
        mock_garage_parser = Mock()
        mock_statement_parser = Mock()
        
        garage_data = [
            {'id': '1', 'monthly_rent': Decimal('3500.00'), 'start_date': date(2025, 1, 1), 'payment_day': 15},
            {'id': '2', 'monthly_rent': Decimal('2800.00'), 'start_date': date(2025, 1, 2), 'payment_day': 16},
        ]
        
        mock_garage_parser.parse_garages.return_value = garage_data
        mock_statement_parser.parse_transactions.return_value = sample_transactions
        mock_payment_matcher.match_payments.return_value = sample_payments[:2]  # First two payments
        
        mock_parser_factory.create_garage_parser.return_value = mock_garage_parser
        mock_parser_factory.create_statement_parser.return_value = mock_statement_parser
        
        # Execute use case
        response = use_case.execute(sample_request)
        
        # Verify report structure
        report = response.report
        assert report.garage_file == str(sample_request.garage_file)
        assert report.statement_file == str(sample_request.statement_file)
        assert report.analysis_date == sample_request.analysis_date
        assert len(report.payments) == 2
        assert report.summary.total_garages == 2
        assert isinstance(report.generated_at, type(report.generated_at))  # datetime
    
    def test_execute_with_custom_configuration(self):
        """Test use case with custom configuration"""
        mock_parser_factory = Mock()
        mock_payment_matcher = Mock()
        
        # Create use case with custom settings
        use_case = ProcessPaymentsUseCase(
            parser_factory=mock_parser_factory,
            payment_matcher=mock_payment_matcher,
            search_window_days=14,  # Custom
            grace_period_days=5     # Custom
        )
        
        assert use_case.search_window_days == 14
        assert use_case.grace_period_days == 5
        assert use_case.parser_factory == mock_parser_factory
        assert use_case.payment_matcher == mock_payment_matcher
    
    def test_execute_empty_files(self, use_case, sample_request, mock_parser_factory, mock_payment_matcher):
        """Test execution with empty input files"""
        # Setup mocks for empty files
        mock_garage_parser = Mock()
        mock_statement_parser = Mock()
        
        mock_garage_parser.parse_garages.return_value = []  # Empty garage data
        mock_statement_parser.parse_transactions.return_value = []  # Empty transactions
        mock_payment_matcher.match_payments.return_value = []  # No payments
        
        mock_parser_factory.create_garage_parser.return_value = mock_garage_parser
        mock_parser_factory.create_statement_parser.return_value = mock_statement_parser
        
        # Execute use case
        response = use_case.execute(sample_request)
        
        # Should succeed with empty data
        assert response.success is True
        assert response.report is not None
        assert len(response.report.payments) == 0
        assert response.report.summary.total_garages == 0
