"""
Internationalization and localization manager
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional


class LocalizationManager:
    """
    Manager for application localization and internationalization
    """
    
    def __init__(self, language: str = "en"):
        """
        Initialize localization manager
        
        Args:
            language: Language code (e.g., 'en', 'ru')
        """
        self.language = language
        self.logger = logging.getLogger(__name__)
        self.messages: Dict[str, str] = {}
        self._load_messages()
    
    def _load_messages(self):
        """Load messages for current language"""
        try:
            # Try to load language-specific messages
            messages_file = Path(__file__).parent / f"messages_{self.language}.json"
            
            if messages_file.exists():
                with open(messages_file, 'r', encoding='utf-8') as f:
                    self.messages = json.load(f)
                self.logger.info(f"Loaded messages for language: {self.language}")
            else:
                # Fallback to English
                if self.language != "en":
                    self.logger.warning(f"Messages not found for {self.language}, falling back to English")
                    self.language = "en"
                    self._load_messages()
                else:
                    # Create minimal English messages if file doesn't exist
                    self.messages = self._get_default_messages()
                    self.logger.warning("No message files found, using defaults")
                    
        except Exception as e:
            self.logger.error(f"Failed to load messages: {e}")
            self.messages = self._get_default_messages()
    
    def get(self, key: str, default: str = None, **kwargs) -> str:
        """
        Get localized message
        
        Args:
            key: Message key
            default: Default value if key not found
            **kwargs: Format parameters for message
            
        Returns:
            Localized message string
        """
        message = self.messages.get(key, default or key)
        
        # Format message with provided parameters
        if kwargs:
            try:
                return message.format(**kwargs)
            except (KeyError, ValueError) as e:
                self.logger.warning(f"Failed to format message '{key}': {e}")
                return message
        
        return message
    
    def set_language(self, language: str):
        """
        Change current language
        
        Args:
            language: New language code
        """
        if language != self.language:
            self.language = language
            self._load_messages()
            self.logger.info(f"Language changed to: {language}")
    
    def switch_language(self, language: str):
        """
        Switch to specified language (alias for set_language)
        
        Args:
            language: Language code to switch to
        """
        self.set_language(language)
    
    def get_available_languages(self) -> list:
        """Get list of available languages"""
        localization_dir = Path(__file__).parent
        languages = []
        
        for file_path in localization_dir.glob("messages_*.json"):
            # Extract language code from filename
            lang_code = file_path.stem.replace("messages_", "")
            languages.append(lang_code)
        
        return sorted(languages)
    
    def _get_default_messages(self) -> Dict[str, str]:
        """Get default English messages"""
        return {
            # Status messages
            "status.received": "Received",
            "status.overdue": "Overdue",
            "status.pending": "Pending",
            "status.not_due": "Not Due",
            "status.unclear": "Unclear",
            
            # Report headers
            "report.header.garage": "Garage",
            "report.header.amount": "Amount (RUB)",
            "report.header.expected_date": "Expected Date",
            "report.header.actual_date": "Actual Date",
            "report.header.status": "Status",
            "report.header.days_overdue": "Days Overdue",
            "report.header.notes": "Notes",
            
            # Worksheet names
            "report.worksheet.payments": "Payments",
            "report.worksheet.summary": "Summary",
            
            # CLI messages
            "cli.process.start": "Processing payments...",
            "cli.process.complete": "Processing completed successfully",
            "cli.process.failed": "Processing failed",
            "cli.report.generated": "Report generated: {filename}",
            
            # Summary messages
            "summary.title": "Payment Summary",
            "summary.total_garages": "Total Garages",
            "summary.received": "Received",
            "summary.overdue": "Overdue",
            "summary.pending": "Pending", 
            "summary.not_due": "Not Due",
            "summary.unclear": "Unclear",
            "summary.collection_rate": "Collection Rate",
            "summary.expected_amount": "Expected Amount",
            "summary.received_amount": "Received Amount",
            "summary.notes_header": "Notes",
            
            # Error messages
            "error.file_not_found": "File not found: {filename}",
            "error.invalid_format": "Invalid file format: {filename}",
            "error.duplicate_amounts": "Duplicate amounts found: {amounts}",
            "error.parsing_failed": "Failed to parse file: {filename}",
            "error.unsupported_language": "Unsupported language: {language}",
            
            # Report messages
            "report.generated": "Report generated successfully"
        }
