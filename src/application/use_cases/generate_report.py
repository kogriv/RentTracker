"""
Generate report use case
"""

import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from ..dto.report_response import ReportGenerationResponse
from ...core.models.report import PaymentReport
from ...infrastructure.file_handlers.excel_writer import ExcelReportWriter
from ...infrastructure.localization.i18n import LocalizationManager
from ...core.exceptions import FileProcessingError


class GenerateReportUseCase:
    """
    Use case for generating payment reports in various formats
    """
    
    def __init__(self, 
                 excel_writer: ExcelReportWriter,
                 localization_manager: LocalizationManager):
        """
        Initialize report generation use case
        
        Args:
            excel_writer: Excel report writer
            localization_manager: Localization manager for translations
        """
        self.excel_writer = excel_writer
        self.i18n = localization_manager
        self.logger = logging.getLogger(__name__)
    
    def generate_excel_report(self, 
                            report: PaymentReport, 
                            output_path: Optional[Path] = None) -> ReportGenerationResponse:
        """
        Generate Excel report from payment data
        
        Args:
            report: Payment report data
            output_path: Output file path (auto-generated if None)
            
        Returns:
            Report generation response
        """
        try:
            # Generate output path if not provided
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                # Ensure output directory exists
                output_dir = Path("output")
                output_dir.mkdir(exist_ok=True)
                output_path = output_dir / f"payment_report_{timestamp}.xlsx"
            
            self.logger.info(f"Generating Excel report: {output_path}")
            
            # Write Excel report
            self.excel_writer.write_report(report, output_path, self.i18n)
            
            self.logger.info(f"Excel report generated successfully: {output_path}")
            
            return ReportGenerationResponse(
                success=True,
                output_path=output_path,
                format="xlsx",
                message=self.i18n.get("report.generated", filename=str(output_path))
            )
            
        except Exception as e:
            error_msg = f"Failed to generate Excel report: {e}"
            self.logger.error(error_msg)
            
            return ReportGenerationResponse(
                success=False,
                output_path=None,
                format="xlsx",
                message=error_msg
            )
    
    def generate_summary_text(self, report: PaymentReport) -> str:
        """
        Generate text summary of payment report
        
        Args:
            report: Payment report data
            
        Returns:
            Formatted text summary
        """
        summary = report.summary
        
        lines = [
            self.i18n.get("summary.title", date=report.analysis_date.strftime("%Y-%m-%d")),
            "=" * 50,
            "",
            self.i18n.get("summary.total_garages", count=summary.total_garages),
            self.i18n.get("summary.received", count=summary.received_count),
            self.i18n.get("summary.overdue", count=summary.overdue_count),
            self.i18n.get("summary.pending", count=summary.pending_count),
            self.i18n.get("summary.not_due", count=summary.not_due_count),
            "",
            self.i18n.get("summary.collection_rate", rate=f"{summary.collection_rate:.1f}%"),
            self.i18n.get("summary.expected_amount", amount=f"{summary.total_expected:.2f}"),
            self.i18n.get("summary.received_amount", amount=f"{summary.total_received:.2f}")
        ]
        
        # Add notes if any
        if report.notes:
            lines.extend([
                "",
                self.i18n.get("summary.notes_header"),
                "-" * 20
            ])
            lines.extend(f"• {note}" for note in report.notes)
        
        return "\n".join(lines)
