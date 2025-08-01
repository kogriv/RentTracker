"""
Flask web application for Garage Payment Tracker
"""

import os
import logging
import time
from pathlib import Path
from datetime import datetime, date
from typing import Optional
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
import markdown

from ...application.use_cases.process_payments import ProcessPaymentsUseCase
from ...application.dto.payment_request import PaymentProcessRequest
from ...application.dto.report_request import ReportGenerationRequest
from ...infrastructure.localization.i18n import LocalizationManager
from ...parsers.base.parser_factory import ParserFactory
from ...core.services.payment_matcher import PaymentMatcher
from ...infrastructure.file_handlers.excel_writer import ExcelReportWriter
from ...infrastructure.config.config_manager import ConfigManager


class WebApp:
    """Flask web application for garage payment processing"""
    
    def __init__(self, config: dict):
        self.app = Flask(__name__, 
                        template_folder='templates',
                        static_folder='static')
        self.app.secret_key = 'garage-tracker-secret-key-change-in-production'
        self.config = config
        
        # Configure upload settings
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
        self.upload_folder = Path('uploads')
        self.upload_folder.mkdir(exist_ok=True)
        
        # Clean up old uploaded files on startup
        self._cleanup_old_files()
        
        # Initialize services
        self._setup_services()
        self._setup_routes()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _setup_services(self):
        """Setup application services"""
        # Initialize localization (default to Russian for web)
        self.i18n = LocalizationManager('ru')
        
        # Initialize core services
        self.parser_factory = ParserFactory()
        self.payment_matcher = PaymentMatcher(
            search_window_days=self.config.get('payment_matching', {}).get('search_window_days', 7),
            grace_period_days=self.config.get('payment_matching', {}).get('grace_period_days', 3),
            i18n=self.i18n
        )
        self.excel_writer = ExcelReportWriter()
        
        # Initialize use cases
        self.process_payments_usecase = ProcessPaymentsUseCase(
            parser_factory=self.parser_factory,
            payment_matcher=self.payment_matcher,
            search_window_days=self.config.get('payment_matching', {}).get('search_window_days', 7),
            grace_period_days=self.config.get('payment_matching', {}).get('grace_period_days', 3)
        )
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main page with file upload form"""
            return render_template('index.html', date=date)
        
        @self.app.route('/upload', methods=['POST'])
        def upload_files():
            """Handle file uploads and process payments"""
            try:
                # Check if files were uploaded
                if 'garage_file' not in request.files or 'statement_file' not in request.files:
                    flash('Необходимо загрузить оба файла: справочник гаражей и банковскую выписку', 'error')
                    return redirect(url_for('index'))
                
                garage_file = request.files['garage_file']
                statement_file = request.files['statement_file']
                analysis_date_str = request.form.get('analysis_date')
                
                # Validate files
                if garage_file.filename == '' or statement_file.filename == '':
                    flash('Необходимо выбрать оба файла', 'error')
                    return redirect(url_for('index'))
                
                if not self._allowed_file(garage_file.filename or '') or not self._allowed_file(statement_file.filename or ''):
                    flash('Поддерживаются только Excel файлы (.xlsx, .xls)', 'error')
                    return redirect(url_for('index'))
                
                # Save uploaded files
                garage_filename = secure_filename(garage_file.filename or 'garage.xlsx')
                statement_filename = secure_filename(statement_file.filename or 'statement.xlsx')
                
                garage_path = self.upload_folder / f"garage_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{garage_filename}"
                statement_path = self.upload_folder / f"statement_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{statement_filename}"
                
                garage_file.save(garage_path)
                statement_file.save(statement_path)
                
                # Parse analysis date
                analysis_date = None
                if analysis_date_str:
                    try:
                        analysis_date = datetime.strptime(analysis_date_str, '%Y-%m-%d').date()
                    except ValueError:
                        flash('Неверный формат даты анализа. Используйте YYYY-MM-DD', 'warning')
                        analysis_date = date.today()
                else:
                    analysis_date = date.today()
                
                # Create output filename
                output_filename = f"payment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                output_path = Path('output') / output_filename
                output_path.parent.mkdir(exist_ok=True)
                
                # Process payments
                request_obj = PaymentProcessRequest(
                    garage_file=garage_path,
                    statement_file=statement_path,
                    analysis_date=analysis_date
                )
                
                response = self.process_payments_usecase.execute(request_obj)
                
                # Generate Excel report manually
                self.excel_writer.write_report(response.report, output_path, self.i18n)
                
                # Clean up uploaded files with proper error handling
                # Add a small delay to ensure files are fully closed
                time.sleep(0.5)
                
                # Try to delete files with retries
                for file_path in [garage_path, statement_path]:
                    if file_path.exists():
                        for attempt in range(3):  # Try up to 3 times
                            try:
                                file_path.unlink()
                                self.logger.info(f"Successfully deleted {file_path}")
                                break
                            except PermissionError as e:
                                self.logger.warning(f"Attempt {attempt + 1}: Could not delete {file_path}: {e}")
                                if attempt < 2:  # Not the last attempt
                                    time.sleep(1)  # Wait before retry
                                else:
                                    self.logger.warning(f"Failed to delete {file_path} after 3 attempts")
                            except Exception as e:
                                self.logger.warning(f"Error deleting {file_path}: {e}")
                                break
                
                # Show success message and provide download
                flash(f'Отчет успешно создан!', 'success')
                
                # Create summary data for display
                report_data = {
                    'filename': output_filename,
                    'analysis_date': analysis_date.strftime('%d.%m.%Y'),
                    'total_garages': response.report.summary.total_garages,
                    'received_count': response.report.summary.received_count,
                    'overdue_count': response.report.summary.overdue_count,
                    'pending_count': response.report.summary.pending_count,
                    'not_due_count': response.report.summary.not_due_count,
                    'collection_rate': response.report.summary.collection_rate,
                    'expected_amount': float(response.report.summary.total_expected),
                    'received_amount': float(response.report.summary.total_received),
                    'warnings': response.warnings
                }
                
                return render_template('result.html', report=report_data)
                
            except Exception as e:
                self.logger.error(f"Error processing files: {e}")
                flash(f'Ошибка при обработке файлов: {str(e)}', 'error')
                return redirect(url_for('index'))
        
        @self.app.route('/download/<filename>')
        def download_report(filename):
            """Download generated report"""
            try:
                # Get absolute path to project root output directory
                project_root = Path(__file__).parent.parent.parent.parent
                file_path = project_root / 'output' / filename
                
                self.logger.info(f"Looking for file at: {file_path.absolute()}")
                
                if file_path.exists():
                    return send_file(file_path.absolute(), as_attachment=True)
                else:
                    # List available files for debugging
                    output_dir = project_root / 'output'
                    if output_dir.exists():
                        available_files = list(output_dir.glob('*.xlsx'))
                        self.logger.error(f"File {filename} not found. Available files: {[f.name for f in available_files]}")
                    
                    flash('Файл отчета не найден', 'error')
                    return redirect(url_for('index'))
                
            except Exception as e:
                self.logger.error(f"Error downloading file: {e}")
                flash(f'Ошибка при скачивании файла: {str(e)}', 'error')
                return redirect(url_for('index'))
        
        @self.app.route('/docs')
        def docs_index():
            """Documentation index page"""
            docs_dir = Path('docs')
            docs_files = []
            
            if docs_dir.exists():
                for file_path in docs_dir.glob('*.md'):
                    docs_files.append({
                        'filename': file_path.name,
                        'title': self._get_doc_title(file_path),
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
                    })
            
            docs_files.sort(key=lambda x: x['title'])
            return render_template('docs_index.html', docs=docs_files)
        
        @self.app.route('/docs/<filename>')
        def view_doc(filename):
            """View specific documentation file"""
            try:
                file_path = Path('docs') / filename
                if not file_path.exists() or not filename.endswith('.md'):
                    flash('Документ не найден', 'error')
                    return redirect(url_for('docs_index'))
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Convert markdown to HTML
                html_content = markdown.markdown(content, extensions=['tables', 'fenced_code', 'toc'])
                
                return render_template('doc_view.html', 
                                     title=self._get_doc_title(file_path),
                                     content=html_content,
                                     filename=filename)
                
            except Exception as e:
                self.logger.error(f"Error viewing document: {e}")
                flash(f'Ошибка при просмотре документа: {str(e)}', 'error')
                return redirect(url_for('docs_index'))
        
        @self.app.route('/api/status')
        def api_status():
            """API endpoint for application status"""
            return jsonify({
                'status': 'ok',
                'version': '3.0',
                'language': getattr(self.i18n, 'language', 'ru'),
                'uptime': datetime.now().isoformat()
            })
    
    def _allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        if not filename:
            return False
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in {'xlsx', 'xls'}
    
    def _get_doc_title(self, file_path: Path) -> str:
        """Extract title from markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#'):
                    return first_line.lstrip('#').strip()
                return file_path.stem
        except:
            return file_path.stem
    
    def _cleanup_old_files(self):
        """Clean up old uploaded files"""
        try:
            current_time = time.time()
            max_age = 3600  # 1 hour in seconds
            
            for file_path in self.upload_folder.glob('*'):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age:
                        try:
                            file_path.unlink()
                            self.logger.info(f"Cleaned up old file: {file_path}")
                        except Exception as e:
                            self.logger.warning(f"Could not delete old file {file_path}: {e}")
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {e}")
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask application"""
        self.app.run(host=host, port=port, debug=debug)


def create_app():
    """Factory function to create Flask app"""
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    web_app = WebApp(config)
    return web_app.app


if __name__ == '__main__':
    # For development
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    app = WebApp(config)
    app.run(debug=True)