"""
Process payments use case
"""

import logging
from pathlib import Path
from typing import List, Optional
from datetime import date

from ..dto.payment_request import PaymentProcessRequest
from ..dto.report_response import PaymentProcessResponse
from ...core.models.garage import Garage
from ...core.models.payment import Payment
from ...core.models.report import PaymentReport
from ...core.models.payment_period import PaymentPeriod
from ...core.services.payment_matcher import PaymentMatcher
from ...parsers.base.parser_factory import ParserFactory
from ...core.exceptions import ParseError, ValidationError, DataIntegrityError


class ProcessPaymentsUseCase:
    """
    Main use case for processing garage rental payments
    """
    
    def __init__(self, 
                 parser_factory: ParserFactory,
                 payment_matcher: PaymentMatcher,
                 search_window_days: int = 7,
                 grace_period_days: int = 3):
        """
        Initialize use case
        
        Args:
            parser_factory: Factory for creating parsers
            payment_matcher: Service for matching payments
            search_window_days: Days to search for payments around expected date
            grace_period_days: Grace period before marking payments overdue
        """
        self.parser_factory = parser_factory
        self.payment_matcher = payment_matcher
        self.search_window_days = search_window_days
        self.grace_period_days = grace_period_days
        self.logger = logging.getLogger(__name__)
    
    def execute(self, request: PaymentProcessRequest) -> PaymentProcessResponse:
        """
        Execute payment processing
        
        Args:
            request: Payment processing request
            
        Returns:
            Payment processing response with results
            
        Raises:
            ParseError: If file parsing fails
            ValidationError: If data validation fails
            DataIntegrityError: If data integrity issues are found
        """
        self.logger.info(f"Starting payment processing for {request.garage_file} and {request.statement_file}")
        
        try:
            # Step 1: Parse garage registry
            garages = self._parse_garage_registry(request.garage_file)
            self.logger.info(f"Parsed {len(garages)} garages from registry")
            
            # Step 2: Parse bank statement and extract payment period
            transactions = self._parse_bank_statement(request.statement_file)
            self.logger.info(f"Parsed {len(transactions)} transactions from statement")
            
            # Step 2.1: Extract payment period from statement
            payment_period = self._extract_payment_period(request.statement_file)
            analysis_date = request.analysis_date
            
            # Determine target month for expected payment calculations
            if payment_period:
                target_month = payment_period.target_month
                self.logger.info(f"Found payment period: {payment_period}")
                self.logger.info(f"Using target month for expected dates: {target_month}")
            else:
                # Fallback to analysis date month if no period detected
                target_month = date(analysis_date.year, analysis_date.month, 1)
                self.logger.warning(f"No payment period detected, using analysis date month: {target_month}")
            
            self.logger.info(f"Using analysis date for status determination: {analysis_date}")
            
            # Step 3: Validate data integrity
            validation_notes = self._validate_data_integrity(garages)
            
            # Step 4: Match payments with proper target month for expected dates
            payments = self.payment_matcher.match_payments(
                garages, 
                transactions, 
                analysis_date,
                target_month
            )
            self.logger.info(f"Processed {len(payments)} payments")
            
            # Step 5: Create report
            report = PaymentReport.create(
                garage_file=str(request.garage_file),
                statement_file=str(request.statement_file),
                payments=payments,
                analysis_date=analysis_date,
                notes=validation_notes
            )
            
            self.logger.info("Payment processing completed successfully")
            
            return PaymentProcessResponse(
                success=True,
                report=report,
                errors=[],
                warnings=validation_notes
            )
            
        except Exception as e:
            self.logger.error(f"Payment processing failed: {e}")
            return PaymentProcessResponse(
                success=False,
                report=None,
                errors=[str(e)],
                warnings=[]
            )
    
    def _parse_garage_registry(self, garage_file: Path) -> List[Garage]:
        """Parse garage registry from file"""
        parser = self.parser_factory.create_garage_parser(source_file=garage_file)
        
        try:
            garage_data = parser.parse_garages(garage_file)
            
            # Convert to domain objects
            garages = []
            for data in garage_data:
                garage = Garage(
                    id=data['id'],
                    monthly_rent=data['monthly_rent'],
                    start_date=data['start_date'],
                    payment_day=data['payment_day']
                )
                garages.append(garage)
            
            return garages
            
        except Exception as e:
            raise ParseError(f"Failed to parse garage registry: {e}", str(garage_file))
    
    def _parse_bank_statement(self, statement_file: Path) -> List:
        """Parse bank statement from file"""
        parser = self.parser_factory.create_statement_parser(source_file=statement_file)
        
        try:
            return parser.parse_transactions(statement_file)
        except Exception as e:
            raise ParseError(f"Failed to parse bank statement: {e}", str(statement_file))
    
    def _validate_data_integrity(self, garages: List[Garage]) -> List[str]:
        """
        Validate data integrity and return warnings
        
        Args:
            garages: List of garages to validate
            
        Returns:
            List of validation warning messages
        """
        warnings = []
        
        # Check for duplicate amounts
        amount_map = {}
        for garage in garages:
            amount = garage.monthly_rent
            if amount not in amount_map:
                amount_map[amount] = []
            amount_map[amount].append(garage.id)
        
        # Report duplicates
        for amount, garage_ids in amount_map.items():
            if len(garage_ids) > 1:
                warning = f"Duplicate rental amount {amount}: garages {', '.join(garage_ids)}"
                warnings.append(warning)
                self.logger.warning(warning)
        
        # Check for unusual payment days
        unusual_days = [garage for garage in garages if garage.payment_day > 28]
        if unusual_days:
            garage_ids = [g.id for g in unusual_days]
            warning = f"Garages with payment days > 28: {', '.join(garage_ids)} (may cause issues in short months)"
            warnings.append(warning)
            self.logger.warning(warning)
        
        return warnings
    
    def _extract_payment_period(self, statement_file: Path) -> Optional[PaymentPeriod]:
        """Extract payment period from bank statement"""
        try:
            # Create statement parser and extract period
            statement_parser = self.parser_factory.create_statement_parser(source_file=statement_file)
            
            # Check if parser supports period extraction (currently only SberbankStatementParser does)
            from ...parsers.file_parsers.sberbank_parser import SberbankStatementParser
            if isinstance(statement_parser, SberbankStatementParser):
                return statement_parser.extract_payment_period(statement_file)
            else:
                self.logger.warning(f"Parser for {statement_file} does not support period extraction")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to extract payment period: {e}")
            return None
