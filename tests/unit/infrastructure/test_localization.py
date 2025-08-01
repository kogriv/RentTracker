"""
Tests for localization system
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

from src.infrastructure.localization.i18n import LocalizationManager


class TestLocalizationManager:
    """Test cases for LocalizationManager"""
    
    def test_init_with_english(self):
        """Test initialization with English language"""
        manager = LocalizationManager("en")
        assert manager.language == "en"
        assert len(manager.messages) > 0
    
    def test_init_with_russian(self):
        """Test initialization with Russian language"""
        manager = LocalizationManager("ru")
        assert manager.language == "ru"
        assert len(manager.messages) > 0
        # Check some Russian messages
        assert manager.get("status.received") == "Получен"
        assert manager.get("status.overdue") == "Просрочен"
    
    def test_get_message_with_formatting(self):
        """Test getting message with format parameters"""
        manager = LocalizationManager("ru")
        
        # Test with parameters
        result = manager.get("summary.total_garages", count=15)
        assert result == "Всего гаражей: 15"
        
        result = manager.get("cli.report.generated", filename="test.xlsx")
        assert result == "Отчет создан: test.xlsx"
    
    def test_get_message_fallback(self):
        """Test fallback behavior for missing keys"""
        manager = LocalizationManager("en")
        
        # Non-existent key should return the key itself
        result = manager.get("non.existent.key")
        assert result == "non.existent.key"
        
        # With default value
        result = manager.get("non.existent.key", default="Default Value")
        assert result == "Default Value"
    
    def test_switch_language(self):
        """Test language switching"""
        manager = LocalizationManager("en")
        assert manager.get("status.received") == "Received"
        
        # Switch to Russian
        manager.switch_language("ru")
        assert manager.language == "ru"
        assert manager.get("status.received") == "Получен"
        
        # Switch back to English
        manager.switch_language("en")
        assert manager.language == "en"
        assert manager.get("status.received") == "Received"
    
    def test_get_available_languages(self):
        """Test getting available languages"""
        manager = LocalizationManager("en")
        languages = manager.get_available_languages()
        
        assert "en" in languages
        assert "ru" in languages
        assert isinstance(languages, list)
    
    def test_fallback_to_english_for_unsupported_language(self):
        """Test fallback to English for unsupported language"""
        with patch('src.infrastructure.localization.i18n.Path.exists') as mock_exists:
            # Mock that the unsupported language file doesn't exist
            mock_exists.return_value = False
            
            manager = LocalizationManager("unsupported")
            # Should fallback to English
            assert manager.language == "en"
            assert manager.get("status.received") == "Received"
    
    def test_error_handling_in_message_loading(self):
        """Test error handling when message file is corrupted"""
        manager = LocalizationManager("unsupported_language")
        # Should fallback to default messages when file doesn't exist or is invalid
        assert len(manager.messages) > 0
        assert manager.get("status.received") == "Received"
    
    def test_format_error_handling(self):
        """Test error handling when message formatting fails"""
        manager = LocalizationManager("en")
        
        # Try to format a message that doesn't accept parameters
        result = manager.get("status.received", invalid_param="test")
        # Should return the unformatted message
        assert result == "Received"
    
    def test_russian_specific_messages(self):
        """Test specific Russian translations"""
        manager = LocalizationManager("ru")
        
        # Test status translations
        status_tests = {
            "status.received": "Получен",
            "status.overdue": "Просрочен",
            "status.pending": "Ожидается",
            "status.not_due": "Срок не наступил",
            "status.unclear": "Неопределенно"
        }
        
        for key, expected in status_tests.items():
            assert manager.get(key) == expected
        
        # Test report headers
        header_tests = {
            "report.header.garage": "Гараж",
            "report.header.amount": "Сумма (руб.)",
            "report.header.status": "Статус",
            "report.header.notes": "Примечания"
        }
        
        for key, expected in header_tests.items():
            assert manager.get(key) == expected
    
    def test_cli_messages_in_russian(self):
        """Test CLI messages in Russian"""
        manager = LocalizationManager("ru")
        
        cli_tests = {
            "cli.process.start": "Обработка платежей...",
            "cli.process.complete": "Обработка завершена успешно",
            "cli.process.failed": "Обработка не удалась"
        }
        
        for key, expected in cli_tests.items():
            assert manager.get(key) == expected
    
    def test_summary_messages_with_formatting(self):
        """Test summary messages with formatting in Russian"""
        manager = LocalizationManager("ru")
        
        # Test formatted summary messages
        assert manager.get("summary.total_garages", count=10) == "Всего гаражей: 10"
        assert manager.get("summary.received", count=5) == "Получено: 5"
        assert manager.get("summary.collection_rate", rate="75.0%") == "Процент сбора: 75.0%"
        assert manager.get("summary.expected_amount", amount="100000.00") == "Ожидаемая сумма: 100000.00 руб."