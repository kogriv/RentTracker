#!/usr/bin/env python3
"""
Garage Payment Tracker - Main Entry Point
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.interfaces.cli.cli_app import CLIApp
from src.infrastructure.config.config_manager import ConfigManager
from src.infrastructure.localization.i18n import LocalizationManager
from src.utils.logging_config import setup_logging


def create_app(language=None) -> CLIApp:
    """Create and configure the CLI application"""
    
    # Initialize logging with file output and minimal console output
    setup_logging(
        log_level="INFO",
        log_file=Path("logs/app.log"),
        console_level="WARNING"  # Only warnings and errors in console
    )
    
    # Load configuration
    config = ConfigManager.load_config()
    
    # Determine language (priority: parameter -> environment variable -> config)
    app_language = (
        language or 
        os.getenv('GARAGE_TRACKER_LANG') or 
        config.get('application', {}).get('default_language', 'en')
    )
    
    # Create localization manager
    i18n = LocalizationManager(app_language)
    
    # Create CLI application
    return CLIApp(config, i18n)


def main():
    """Main entry point"""
    try:
        app = create_app()
        app.run()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
