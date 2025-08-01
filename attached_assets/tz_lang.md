Да, в предложенной архитектуре система локализации предусмотрена и детально проработана. Давайте рассмотрим все компоненты:
Система локализации в архитектуре
1. Структура файлов для локализации
```python
src/infrastructure/localization/
├── i18n.py                    # Менеджер локализации
├── messages_en.json           # Английские сообщения (базовые)
└── messages_ru.json           # Русские сообщения (для добавления)
```

2. Менеджер локализации
```python
# src/infrastructure/localization/i18n.py
class LocalizationManager:
    def __init__(self, language="en"):
        self.language = language
        self.messages = self._load_messages()
    
    def _load_messages(self) -> dict:
        try:
            with open(f"messages_{self.language}.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback к английскому
            with open("messages_en.json", 'r', encoding='utf-8') as f:
                return json.load(f)
    
    def get(self, key: str, **kwargs) -> str:
        message = self.messages.get(key, key)
        return message.format(**kwargs) if kwargs else message
    
    def set_language(self, language: str):
        self.language = language
        self.messages = self._load_messages()
```

3. Конфигурация языка
```python
# config/default_config.yaml
application:
  name: "Garage Payment Tracker"
  default_language: "en"      # Язык по умолчанию
  available_languages: ["en", "ru"]  # Доступные языки
```

4. Файлы сообщений
Английский (messages_en.json):
```json
{
  "status.received": "Received",
  "status.overdue": "Overdue",
  "status.pending": "Pending", 
  "status.not_due": "Not due yet",
  "status.unclear": "Unclear",
  
  "report.header.garage": "Garage",
  "report.header.amount": "Amount (RUB)",
  "report.header.expected_date": "Expected Date",
  "report.header.actual_date": "Actual Date",
  "report.header.status": "Status",
  "report.header.days_overdue": "Days Overdue",
  "report.header.notes": "Notes",
  
  "cli.process.start": "Processing payments...",
  "cli.process.complete": "Processing completed successfully",
  "cli.report.generated": "Report generated: {filename}",
  
  "error.file_not_found": "File not found: {filename}",
  "error.invalid_format": "Invalid file format: {filename}",
  "error.duplicate_amounts": "Duplicate amounts found: {amounts}",
  
  "summary.total_garages": "Total garages: {count}",
  "summary.received": "Received: {count}",
  "summary.overdue": "Overdue: {count}",
  "summary.pending": "Pending: {count}"
}
```

Русский (messages_ru.json) - для будущего добавления:
```json
{
  "status.received": "Получен",
  "status.overdue": "Просрочен", 
  "status.pending": "Ожидается",
  "status.not_due": "Срок не наступил",
  "status.unclear": "Неопределенно",
  
  "report.header.garage": "Гараж",
  "report.header.amount": "Сумма (руб.)",
  "report.header.expected_date": "Ожидаемая дата",
  "report.header.actual_date": "Фактическая дата", 
  "report.header.status": "Статус",
  "report.header.days_overdue": "Дней просрочки",
  "report.header.notes": "Примечания",
  
  "cli.process.start": "Обработка платежей...",
  "cli.process.complete": "Обработка завершена успешно",
  "cli.report.generated": "Отчет создан: {filename}",
  
  "error.file_not_found": "Файл не найден: {filename}",
  "error.invalid_format": "Неверный формат файла: {filename}",
  "error.duplicate_amounts": "Найдены дублирующие суммы: {amounts}"
}
```

5. Использование в коде
```python
# src/interfaces/cli/cli_app.py
class CLIApp:
    def __init__(self, use_case, localization_manager):
        self.use_case = use_case
        self.i18n = localization_manager
    
    def process_payments(self, garage_file, statement_file):
        print(self.i18n.get("cli.process.start"))
        
        try:
            result = self.use_case.execute(garage_file, statement_file)
            print(self.i18n.get("cli.process.complete"))
            print(self.i18n.get("cli.report.generated", filename=result.report_path))
        except FileNotFoundError as e:
            print(self.i18n.get("error.file_not_found", filename=str(e)))

# src/application/use_cases/generate_report.py
class GenerateReportUseCase:
    def __init__(self, localization_manager):
        self.i18n = localization_manager
    
    def generate_excel_headers(self) -> List[str]:
        return [
            self.i18n.get("report.header.garage"),
            self.i18n.get("report.header.amount"),
            self.i18n.get("report.header.expected_date"),
            self.i18n.get("report.header.actual_date"),
            self.i18n.get("report.header.status"),
            self.i18n.get("report.header.days_overdue"),
            self.i18n.get("report.header.notes")
        ]
```
6. CLI поддержка смены языка

```python
# src/interfaces/cli/commands/language_command.py
class LanguageCommand:
    def __init__(self, app):
        self.app = app
    
    def execute(self, language: str):
        if language in self.app.config.available_languages:
            self.app.i18n.set_language(language)
            print(self.app.i18n.get("cli.language.changed", language=language))
        else:
            print(self.app.i18n.get("error.unsupported_language", language=language))
```

7. Инициализация с учетом локали
```python
# main.py
def create_app(language=None) -> CLIApp:
    config = ConfigManager.load_config()
    
    # Определение языка (приоритет: параметр -> переменная среды -> конфиг)
    app_language = (
        language or 
        os.getenv('GARAGE_TRACKER_LANG') or 
        config.application.default_language
    )
    
    # Создание менеджера локализации
    i18n = LocalizationManager(app_language)
    
    # Остальные компоненты...
    use_case = ProcessPaymentsUseCase(...)
    
    return CLIApp(use_case, i18n)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', choices=['en', 'ru'], help='Interface language')
    args = parser.parse_args()
    
    app = create_app(language=args.lang)
    app.run()
```

