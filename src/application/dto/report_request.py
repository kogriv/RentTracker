"""
Report generation request DTO
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ...core.models.report import PaymentReport
from ...infrastructure.localization.i18n import LocalizationManager


@dataclass
class ReportGenerationRequest:
    """Request for generating payment report"""
    report: PaymentReport
    output_file: Path
    localization_manager: Optional[LocalizationManager] = None


@dataclass 
class ReportGenerationResponse:
    """Response from report generation"""
    output_file: Path
    generation_time: float
    file_size: int