"""
Configuration management
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

from ...core.exceptions import ConfigurationError


class ConfigManager:
    """
    Manager for application configuration
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._config_cache: Optional[Dict[str, Any]] = None
    
    @classmethod
    def load_config(cls, config_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Load configuration from YAML file
        
        Args:
            config_path: Path to configuration file (uses default if None)
            
        Returns:
            Configuration dictionary
            
        Raises:
            ConfigurationError: If configuration cannot be loaded
        """
        manager = cls()
        return manager._load_config(config_path)
    
    def _load_config(self, config_path: Optional[Path] = None) -> Dict[str, Any]:
        """Load configuration from file"""
        
        if config_path is None:
            config_path = self._find_default_config()
        
        try:
            if not config_path.exists():
                self.logger.warning(f"Config file not found: {config_path}, using defaults")
                return self._get_default_config()
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Merge with defaults
            default_config = self._get_default_config()
            merged_config = self._merge_configs(default_config, config)
            
            self.logger.info(f"Configuration loaded from {config_path}")
            return merged_config
            
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file {config_path}: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load config from {config_path}: {e}")
    
    def _find_default_config(self) -> Path:
        """Find default configuration file"""
        # Look for config in several locations
        search_paths = [
            Path("config/default_config.yaml"),
            Path("./default_config.yaml"),
            Path.home() / ".garage-tracker" / "config.yaml"
        ]
        
        for path in search_paths:
            if path.exists():
                return path
        
        # Return the standard location even if it doesn't exist
        return Path("config/default_config.yaml")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "application": {
                "name": "Garage Payment Tracker",
                "version": "1.0.0",
                "default_language": "en",
                "available_languages": ["en", "ru"]
            },
            "parsing": {
                "grace_period_days": 3,
                "search_window_days": 7,
                "date_formats": ["DD.MM.YYYY", "DD/MM/YYYY", "YYYY-MM-DD"],
                "amount_tolerance": 0.01
            },
            "parsers": {
                "default_statement": "sberbank_excel",
                "default_garage": "excel",
                "available": ["excel", "sberbank_excel"]
            },
            "output": {
                "format": "xlsx",
                "include_summary": True,
                "auto_open": False
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge user configuration with defaults
        
        Args:
            default: Default configuration
            user: User configuration
            
        Returns:
            Merged configuration
        """
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration structure and values
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if configuration is valid
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Check required sections
        required_sections = ["application", "parsing", "parsers", "output"]
        for section in required_sections:
            if section not in config:
                raise ConfigurationError(f"Missing required configuration section: {section}")
        
        # Validate parsing settings
        parsing = config.get("parsing", {})
        if parsing.get("grace_period_days", 0) < 0:
            raise ConfigurationError("grace_period_days must be non-negative")
        
        if parsing.get("search_window_days", 0) < 0:
            raise ConfigurationError("search_window_days must be non-negative")
        
        # Validate language settings
        app_config = config.get("application", {})
        default_lang = app_config.get("default_language")
        available_langs = app_config.get("available_languages", [])
        
        if default_lang and default_lang not in available_langs:
            raise ConfigurationError(f"Default language '{default_lang}' not in available languages")
        
        return True
