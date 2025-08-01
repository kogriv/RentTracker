#!/usr/bin/env python3
"""
Web application launcher for Garage Payment Tracker
"""

import os
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from src.interfaces.web.app import create_app

def main():
    """Main entry point for web application"""
    # Create required directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Create Flask app
    app = create_app()
    
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("=" * 60)
    print("🚀 Запуск веб-интерфейса Трекера Платежей за Гаражи")
    print("=" * 60)
    print(f"📡 Сервер запущен на: http://{host}:{port}")
    print(f"🌐 Локальный доступ: http://localhost:{port}")
    print(f"📁 Загрузки: uploads/")
    print(f"📄 Отчеты: output/")
    print(f"📖 Документация: http://localhost:{port}/docs")
    print("=" * 60)
    print("Нажмите Ctrl+C для остановки сервера")
    print()
    
    # Run the application
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")

if __name__ == '__main__':
    main()