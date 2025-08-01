"""
Command Line Interface application
"""

import sys
import logging
from pathlib import Path
from datetime import date
from typing import Optional

import click

from ...application.use_cases.process_payments import ProcessPaymentsUseCase
from ...application.use_cases.generate_report import GenerateReportUseCase
from ...application.dto.payment_request import PaymentProcessRequest
from ...parsers.base.parser_factory import ParserFactory
from ...core.services.payment_matcher import PaymentMatcher
from ...infrastructure.file_handlers.excel_writer import ExcelReportWriter
from ...infrastructure.localization.i18n import LocalizationManager
from ...core.exceptions import GarageTrackerException


class CLIApp:
    """
    Command Line Interface application for garage payment tracker
    """
    
    def __init__(self, config: dict, localization_manager: LocalizationManager):
        """
        Initialize CLI application
        
        Args:
            config: Application configuration
            localization_manager: Localization manager
        """
        self.config = config
        self.i18n = localization_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        self._setup_services()
    
    def _setup_services(self):
        """Setup application services"""
        # Get configuration values
        search_window_days = self.config.get('parsing', {}).get('search_window_days', 7)
        grace_period_days = self.config.get('parsing', {}).get('grace_period_days', 3)
        
        # Create services
        self.parser_factory = ParserFactory()
        self.payment_matcher = PaymentMatcher(
            search_window_days=search_window_days,
            grace_period_days=grace_period_days,
            i18n=self.i18n
        )
        self.excel_writer = ExcelReportWriter()
        
        # Create use cases
        self.process_payments_use_case = ProcessPaymentsUseCase(
            parser_factory=self.parser_factory,
            payment_matcher=self.payment_matcher,
            search_window_days=search_window_days,
            grace_period_days=grace_period_days
        )
        
        self.generate_report_use_case = GenerateReportUseCase(
            excel_writer=self.excel_writer,
            localization_manager=self.i18n
        )
    
    def run(self):
        """Run the CLI application"""
        
        @click.group()
        @click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
        @click.option('--lang', '--language', type=click.Choice(['en', 'ru']), 
                     help='Interface language (en=English, ru=Russian)')
        @click.pass_context
        def cli(ctx, verbose, lang):
            """Garage Payment Tracker - Track rental payments and generate reports
            
            File Locations:
            • Input files: attached_assets/ folder
            • Output reports: output/ folder
            
            Example usage:
            python main.py process-payments --garage-file attached_assets/arenda.xlsx --statement-file attached_assets/print.xlsx
            """
            if verbose:
                logging.getLogger().setLevel(logging.DEBUG)
            
            # Switch language if specified
            if lang:
                self.i18n.switch_language(lang)
            
            # Store app instance in context
            ctx.ensure_object(dict)
            ctx.obj['app'] = self
        
        @cli.command('process-payments')
        @click.option('--garage-file', required=True, type=click.Path(exists=True, path_type=Path),
                     help='Path to garage registry Excel file (typically in attached_assets/ folder)')
        @click.option('--statement-file', required=True, type=click.Path(exists=True, path_type=Path),
                     help='Path to bank statement Excel file (typically in attached_assets/ folder)')
        @click.option('--output', '-o', type=click.Path(path_type=Path),
                     help='Output file path for report (saves to output/ folder if not specified)')
        @click.option('--analysis-date', type=click.DateTime(formats=['%Y-%m-%d']),
                     help='Analysis date (default: today)')
        @click.pass_context
        def process_payments(ctx, garage_file, statement_file, output, analysis_date):
            """Process garage payments and generate report
            
            This command parses garage registry and bank statement files, matches payments,
            and generates a comprehensive Excel report with payment analysis.
            
            Input files are typically located in the attached_assets/ folder.
            Output reports are saved to the output/ folder.
            
            Examples:
            python main.py process-payments --garage-file attached_assets/arenda.xlsx --statement-file attached_assets/print.xlsx
            python main.py process-payments --garage-file attached_assets/arenda.xlsx --statement-file attached_assets/print.xlsx --output my_report.xlsx
            """
            app = ctx.obj['app']
            
            try:
                # Use today if no analysis date provided
                if analysis_date is None:
                    analysis_date = date.today()
                else:
                    analysis_date = analysis_date.date()
                
                click.echo(app.i18n.get("cli.process.start"))
                
                # Create request
                request = PaymentProcessRequest(
                    garage_file=garage_file,
                    statement_file=statement_file,
                    analysis_date=analysis_date,
                    output_path=output
                )
                
                # Process payments
                response = app.process_payments_use_case.execute(request)
                
                if not response.success:
                    click.echo(app.i18n.get("cli.process.failed"), err=True)
                    for error in response.errors:
                        click.echo(f"Error: {error}", err=True)
                    sys.exit(1)
                
                # Show warnings
                if response.warnings:
                    for warning in response.warnings:
                        click.echo(f"Warning: {warning}", err=True)
                
                # Generate report
                report_response = app.generate_report_use_case.generate_excel_report(
                    response.report, output
                )
                
                if report_response.success:
                    click.echo(app.i18n.get("cli.process.complete"))
                    click.echo(app.i18n.get("cli.report.generated", filename=str(report_response.output_path)))
                    
                    # Show summary
                    summary_text = app.generate_report_use_case.generate_summary_text(response.report)
                    click.echo("\n" + summary_text)
                else:
                    click.echo(f"Report generation failed: {report_response.message}", err=True)
                    sys.exit(1)
                
            except GarageTrackerException as e:
                click.echo(f"Error: {e}", err=True)
                sys.exit(1)
            except Exception as e:
                app.logger.exception("Unexpected error in CLI")
                click.echo(f"Unexpected error: {e}", err=True)
                sys.exit(1)
        
        @cli.command('version')
        def version():
            """Show version information"""
            app_name = self.config.get('application', {}).get('name', 'Garage Payment Tracker')
            app_version = self.config.get('application', {}).get('version', '1.0.0')
            click.echo(f"{app_name} v{app_version}")
        
        # Run the CLI
        cli()
