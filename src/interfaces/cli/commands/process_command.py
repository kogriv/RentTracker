"""
Process payments CLI command
"""

import sys
from pathlib import Path
from datetime import date
from typing import Optional

import click

from ....application.dto.payment_request import PaymentProcessRequest
from ....core.exceptions import GarageTrackerException


class ProcessPaymentsCommand:
    """
    CLI command for processing garage payments
    """
    
    def __init__(self, app):
        """
        Initialize command
        
        Args:
            app: CLI application instance
        """
        self.app = app
    
    def execute(self, 
                garage_file: Path,
                statement_file: Path,
                output_path: Optional[Path] = None,
                analysis_date: Optional[date] = None) -> bool:
        """
        Execute payment processing command
        
        Args:
            garage_file: Path to garage registry file
            statement_file: Path to bank statement file
            output_path: Optional output path for report
            analysis_date: Optional analysis date (default: today)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use today if no analysis date provided
            if analysis_date is None:
                analysis_date = date.today()
            
            click.echo(self.app.i18n.get("cli.process.start"))
            
            # Create and execute request
            request = PaymentProcessRequest(
                garage_file=garage_file,
                statement_file=statement_file,
                analysis_date=analysis_date,
                output_path=output_path
            )
            
            response = self.app.process_payments_use_case.execute(request)
            
            if not response.success:
                click.echo(self.app.i18n.get("cli.process.failed"), err=True)
                for error in response.errors:
                    click.echo(f"Error: {error}", err=True)
                return False
            
            # Show warnings
            if response.warnings:
                for warning in response.warnings:
                    click.echo(f"Warning: {warning}", err=True)
            
            # Generate report
            report_response = self.app.generate_report_use_case.generate_excel_report(
                response.report, output_path
            )
            
            if report_response.success:
                click.echo(self.app.i18n.get("cli.process.complete"))
                click.echo(self.app.i18n.get("cli.report.generated", filename=str(report_response.output_path)))
                
                # Show summary
                summary_text = self.app.generate_report_use_case.generate_summary_text(response.report)
                click.echo("\n" + summary_text)
                return True
            else:
                click.echo(f"Report generation failed: {report_response.message}", err=True)
                return False
            
        except GarageTrackerException as e:
            click.echo(f"Error: {e}", err=True)
            return False
        except Exception as e:
            self.app.logger.exception("Unexpected error in process command")
            click.echo(f"Unexpected error: {e}", err=True)
            return False
