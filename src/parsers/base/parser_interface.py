"""
Abstract parser interface
"""

from abc import ABC, abstractmethod
from typing import List, Any
from pathlib import Path

from ...core.models.transaction import Transaction


class StatementParser(ABC):
    """
    Abstract base class for bank statement parsers
    """
    
    @abstractmethod
    def parse_transactions(self, source: Path) -> List[Transaction]:
        """
        Parse transactions from source file
        
        Args:
            source: Path to source file
            
        Returns:
            List of parsed transactions
            
        Raises:
            ParseError: If parsing fails
        """
        pass
    
    @abstractmethod
    def validate_source(self, source: Path) -> bool:
        """
        Validate if source file can be parsed by this parser
        
        Args:
            source: Path to source file
            
        Returns:
            True if file can be parsed
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats
        
        Returns:
            List of supported file extensions
        """
        pass


class GarageRegistryParser(ABC):
    """
    Abstract base class for garage registry parsers
    """
    
    @abstractmethod
    def parse_garages(self, source: Path) -> List[Any]:
        """
        Parse garage registry from source file
        
        Args:
            source: Path to source file
            
        Returns:
            List of garage data dictionaries
            
        Raises:
            ParseError: If parsing fails
        """
        pass
    
    @abstractmethod
    def validate_source(self, source: Path) -> bool:
        """
        Validate if source file can be parsed by this parser
        
        Args:
            source: Path to source file
            
        Returns:
            True if file can be parsed
        """
        pass
