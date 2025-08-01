"""
Parser factory for creating appropriate parsers
"""

from typing import Dict, Type
from pathlib import Path
import logging

from .parser_interface import StatementParser, GarageRegistryParser
from ..file_parsers.excel_parser import ExcelGarageParser
from ..file_parsers.sberbank_parser import SberbankStatementParser
from ...core.exceptions import ConfigurationError


class ParserFactory:
    """
    Factory for creating appropriate parsers based on file type and content
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Registry of available parsers
        self._statement_parsers: Dict[str, Type[StatementParser]] = {
            "sberbank_excel": SberbankStatementParser,
        }
        
        self._garage_parsers: Dict[str, Type[GarageRegistryParser]] = {
            "excel": ExcelGarageParser,
        }
    
    def create_statement_parser(self, parser_type: str = None, source_file: Path = None) -> StatementParser:
        """
        Create statement parser
        
        Args:
            parser_type: Specific parser type to use
            source_file: Source file to determine parser type automatically
            
        Returns:
            Configured statement parser
            
        Raises:
            ConfigurationError: If parser type is not supported
        """
        if parser_type:
            if parser_type not in self._statement_parsers:
                raise ConfigurationError(f"Unknown statement parser type: {parser_type}")
            return self._statement_parsers[parser_type]()
        
        if source_file:
            # Auto-detect parser based on file
            return self._auto_detect_statement_parser(source_file)
        
        # Default to Sberbank parser
        return SberbankStatementParser()
    
    def create_garage_parser(self, parser_type: str = None, source_file: Path = None) -> GarageRegistryParser:
        """
        Create garage registry parser
        
        Args:
            parser_type: Specific parser type to use
            source_file: Source file to determine parser type automatically
            
        Returns:
            Configured garage parser
            
        Raises:
            ConfigurationError: If parser type is not supported
        """
        if parser_type:
            if parser_type not in self._garage_parsers:
                raise ConfigurationError(f"Unknown garage parser type: {parser_type}")
            return self._garage_parsers[parser_type]()
        
        if source_file:
            # Auto-detect parser based on file
            return self._auto_detect_garage_parser(source_file)
        
        # Default to Excel parser
        return ExcelGarageParser()
    
    def _auto_detect_statement_parser(self, source_file: Path) -> StatementParser:
        """Auto-detect appropriate statement parser for file"""
        
        # Check file extension
        if source_file.suffix.lower() in ['.xlsx', '.xls']:
            # Try Sberbank parser first (most specific)
            sberbank_parser = SberbankStatementParser()
            if sberbank_parser.validate_source(source_file):
                self.logger.info(f"Auto-detected Sberbank parser for {source_file}")
                return sberbank_parser
        
        # Default fallback
        self.logger.warning(f"Could not auto-detect parser for {source_file}, using default Sberbank parser")
        return SberbankStatementParser()
    
    def _auto_detect_garage_parser(self, source_file: Path) -> GarageRegistryParser:
        """Auto-detect appropriate garage parser for file"""
        
        # Check file extension
        if source_file.suffix.lower() in ['.xlsx', '.xls']:
            excel_parser = ExcelGarageParser()
            if excel_parser.validate_source(source_file):
                self.logger.info(f"Auto-detected Excel parser for {source_file}")
                return excel_parser
        
        # Default fallback
        self.logger.warning(f"Could not auto-detect parser for {source_file}, using default Excel parser")
        return ExcelGarageParser()
    
    def get_available_parsers(self) -> Dict[str, Dict[str, list]]:
        """Get information about available parsers"""
        return {
            "statement_parsers": list(self._statement_parsers.keys()),
            "garage_parsers": list(self._garage_parsers.keys())
        }
