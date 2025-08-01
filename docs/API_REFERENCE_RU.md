# Справочник API и архитектуры

Техническая документация по архитектуре, компонентам и API Трекера Платежей за Гаражи.

## 🏗️ Архитектура системы

### Общая схема

```
┌─────────────────────────────────────────────────────────────┐
│                    Interface Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │
│  │   CLI Interface │  │  Future Web UI  │  │ Future Bot   │  │
│  │   (Click)       │  │                 │  │ Interface    │  │
│  └─────────────────┘  └─────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │
│  │ ProcessPayments │  │ GenerateReport  │  │ Future Use   │  │
│  │    UseCase      │  │    UseCase      │  │    Cases     │  │
│  └─────────────────┘  └─────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                      Domain Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐   │
│  │   Models     │  │   Services   │  │    Exceptions     │   │
│  │ Garage       │  │ PaymentMatcher│  │ ParseError       │   │
│  │ Payment      │  │ DateCalculator│  │ ValidationError  │   │
│  │ Transaction  │  │ StatusDeterminer│ │ DataIntegrityErr │   │
│  │ Report       │  │              │  │                  │   │
│  └──────────────┘  └──────────────┘  └───────────────────┘   │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐   │
│  │   Parsers    │  │ File Handlers│  │   Configuration   │   │
│  │ GarageParser │  │ ExcelWriter  │  │ ConfigManager    │   │
│  │ SberbankParser│  │ LogHandler   │  │ LocalizationMgr  │   │
│  └──────────────┘  └──────────────┘  └───────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Принципы архитектуры

1. **Clean Architecture** - четкое разделение слоев с инверсией зависимостей
2. **Dependency Injection** - зависимости передаются через конструкторы
3. **Single Responsibility** - каждый класс имеет одну ответственность
4. **Interface Segregation** - интерфейсы для расширяемости
5. **Domain-Driven Design** - бизнес-логика изолирована в Domain слое

## 📦 Модули и компоненты

### Domain Layer (`src/core/`)

#### Models

##### Garage
```python
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass(frozen=True)
class Garage:
    """Модель гаража с арендой"""
    id: int
    monthly_rent: Decimal
    start_date: date
    payment_day: int
    
    def __post_init__(self):
        # Валидация данных
        if self.id <= 0:
            raise ValueError("ID гаража должен быть положительным")
        if self.monthly_rent <= 0:
            raise ValueError("Сумма аренды должна быть положительной")
        if not (1 <= self.payment_day <= 31):
            raise ValueError("День платежа должен быть от 1 до 31")
```

##### Payment
```python
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional
from enum import Enum

class PaymentStatus(Enum):
    """Статусы платежей"""
    RECEIVED = "received"       # Получен
    OVERDUE = "overdue"         # Просрочен
    PENDING = "pending"         # Ожидается
    NOT_DUE = "not_due"         # Срок не наступил
    UNCLEAR = "unclear"         # Неясно

@dataclass(frozen=True)
class Payment:
    """Модель платежа"""
    garage_id: int
    expected_amount: Decimal
    expected_date: date
    status: PaymentStatus
    actual_amount: Optional[Decimal] = None
    actual_date: Optional[date] = None
    days_overdue: int = 0
    notes: str = ""
```

##### Transaction
```python
@dataclass(frozen=True)
class Transaction:
    """Модель банковской транзакции"""
    date: date
    amount: Decimal
    description: str
    category: str = ""
    source_row: int = 0
    
    def matches_amount(self, expected_amount: Decimal, tolerance: Decimal = Decimal('0.01')) -> bool:
        """Проверка соответствия суммы с допуском"""
        return abs(abs(self.amount) - expected_amount) <= tolerance
```

##### PaymentPeriod
```python
@dataclass(frozen=True) 
class PaymentPeriod:
    """Период платежей из банковской выписки"""
    start_date: date
    end_date: date
    source_text: str
    
    @property
    def target_month(self) -> date:
        """Целевой месяц для анализа (обычно start_date)"""
        return self.start_date.replace(day=1)
        
    @property
    def analysis_date(self) -> date:
        """Рекомендуемая дата анализа (end_date)"""
        return self.end_date
```

#### Services

##### PaymentMatcher
```python
class PaymentMatcher:
    """Сервис сопоставления платежей"""
    
    def __init__(self, 
                 search_window_days: int = 7,
                 grace_period_days: int = 3,
                 i18n: LocalizationManager = None):
        self.search_window_days = search_window_days
        self.grace_period_days = grace_period_days
        self.i18n = i18n or LocalizationManager()
    
    def match_payments(self, 
                      garages: List[Garage],
                      transactions: List[Transaction], 
                      payment_period: PaymentPeriod,
                      analysis_date: date) -> List[Payment]:
        """
        Основной метод сопоставления платежей
        
        Args:
            garages: Список гаражей
            transactions: Список транзакций
            payment_period: Период платежей
            analysis_date: Дата анализа
            
        Returns:
            Список обработанных платежей
        """
        # Реализация двухуровневого поиска
        # 1. Стандартный поиск в окне
        # 2. Расширенный поиск по всему периоду
        
    def _find_matching_transaction(self, 
                                  garage: Garage,
                                  expected_date: date,
                                  transactions: List[Transaction]) -> Tuple[Optional[Transaction], str]:
        """Поиск соответствующей транзакции для гаража"""
        
    def _create_matched_payment(self, 
                               payment: Payment, 
                               transaction: Transaction, 
                               conflict_info: str) -> Payment:
        """Создание платежа с найденной транзакцией"""
```

##### StatusDeterminer
```python
class StatusDeterminer:
    """Определение статуса платежей"""
    
    def __init__(self, grace_period_days: int = 3):
        self.grace_period_days = grace_period_days
    
    def determine_status(self, 
                        expected_date: date, 
                        analysis_date: date,
                        transaction_found: bool) -> PaymentStatus:
        """
        Определение статуса платежа
        
        Логика:
        - RECEIVED: транзакция найдена
        - OVERDUE: analysis_date > expected_date + grace_period И транзакция не найдена
        - PENDING: expected_date <= analysis_date <= expected_date + grace_period И транзакция не найдена
        - NOT_DUE: analysis_date < expected_date
        """
        
    def calculate_days_overdue(self, 
                              expected_date: date,
                              actual_date: Optional[date],
                              analysis_date: date,
                              status: PaymentStatus) -> int:
        """Расчет дней просрочки"""
```

### Application Layer (`src/application/`)

#### Use Cases

##### ProcessPaymentsUseCase
```python
class ProcessPaymentsUseCase:
    """Use case для обработки платежей"""
    
    def __init__(self, 
                 parser_factory: ParserFactory,
                 payment_matcher: PaymentMatcher,
                 search_window_days: int = 7,
                 grace_period_days: int = 3):
        
    def execute(self, request: PaymentProcessRequest) -> PaymentProcessResponse:
        """
        Выполнение обработки платежей
        
        Steps:
        1. Парсинг справочника гаражей
        2. Парсинг банковской выписки  
        3. Извлечение периода платежей
        4. Сопоставление платежей
        5. Создание отчета
        """
```

##### GenerateReportUseCase
```python
class GenerateReportUseCase:
    """Use case для генерации отчетов"""
    
    def execute(self, request: ReportGenerationRequest) -> ReportGenerationResponse:
        """Генерация Excel отчета с локализацией"""
```

#### DTOs

##### PaymentProcessRequest
```python
@dataclass
class PaymentProcessRequest:
    """Запрос на обработку платежей"""
    garage_file: Path
    statement_file: Path
    analysis_date: Optional[date] = None
    output_file: Optional[Path] = None
```

##### PaymentProcessResponse
```python
@dataclass
class PaymentProcessResponse:
    """Ответ обработки платежей"""
    report: PaymentReport
    warnings: List[str]
    processing_time: float
    output_file: Path
```

### Infrastructure Layer (`src/infrastructure/`)

#### Parsers

##### GarageRegistryParser
```python
class GarageRegistryParser:
    """Парсер справочника гаражей"""
    
    def parse(self, file_path: Path) -> List[Garage]:
        """
        Парсинг Excel файла с гаражами
        
        Expected format:
        | ID | Сумма аренды | Дата начала | День платежа |
        """
        
    def _validate_garage_data(self, row_data: dict) -> None:
        """Валидация данных гаража"""
```

##### SberbankStatementParser
```python
class SberbankStatementParser:
    """Парсер выписки Сбербанка"""
    
    def parse(self, file_path: Path) -> List[Transaction]:
        """Парсинг Excel выписки"""
        
    def extract_payment_period(self, file_path: Path) -> Optional[PaymentPeriod]:
        """
        Извлечение периода из текста выписки
        
        Ищет паттерны: "Итого по операциям с ДД.ММ.ГГГГ по ДД.ММ.ГГГГ"
        """
```

##### ParserFactory
```python
class ParserFactory:
    """Фабрика парсеров"""
    
    def create_garage_parser(self) -> GarageRegistryParser:
        """Создание парсера гаражей"""
        
    def create_statement_parser(self, bank_type: str = "sberbank") -> StatementParser:
        """Создание парсера выписки по типу банка"""
```

#### File Handlers

##### ExcelReportWriter
```python
class ExcelReportWriter:
    """Генератор Excel отчетов"""
    
    def write_report(self, 
                    report: PaymentReport, 
                    file_path: Path,
                    localization_manager: LocalizationManager) -> None:
        """
        Создание локализованного Excel отчета
        
        Structure:
        - Metadata (generation date, analysis date)
        - Headers (localized)
        - Payment data
        - Summary statistics
        """
        
    def _format_currency(self, amount: Decimal) -> str:
        """Форматирование валютных сумм"""
        
    def _format_date(self, date_obj: date) -> str:
        """Форматирование дат"""
```

#### Localization

##### LocalizationManager
```python
class LocalizationManager:
    """Менеджер локализации"""
    
    def __init__(self, language: str = 'en'):
        self.current_language = language
        self.messages = self._load_messages()
        
    def get(self, key: str, **kwargs) -> str:
        """
        Получение локализованного сообщения
        
        Args:
            key: Ключ сообщения (например: "status.received")
            **kwargs: Параметры для форматирования
            
        Returns:
            Форматированное сообщение
        """
        
    def switch_language(self, language: str) -> None:
        """Переключение языка"""
        
    def get_available_languages(self) -> List[str]:
        """Список доступных языков"""
```

### Interface Layer (`src/interfaces/`)

#### CLI Application

##### CLIApp
```python
class CLIApp:
    """Главное CLI приложение"""
    
    def __init__(self, config: dict, localization_manager: LocalizationManager):
        self.config = config
        self.i18n = localization_manager
        self._setup_services()
        
    def run(self) -> None:
        """Запуск Click CLI интерфейса"""
        
    @click.command('process-payments')
    @click.option('--garage-file', required=True, type=click.Path(exists=True))
    @click.option('--statement-file', required=True, type=click.Path(exists=True))
    @click.option('--output', '-o', type=click.Path())
    @click.option('--analysis-date', type=click.DateTime(formats=['%Y-%m-%d']))
    def process_payments(self, garage_file, statement_file, output, analysis_date):
        """Команда обработки платежей"""
```

## 🔌 API Reference

### Основные интерфейсы

#### Parser Interface
```python
from abc import ABC, abstractmethod
from typing import List
from pathlib import Path

class StatementParser(ABC):
    """Интерфейс парсера банковских выписок"""
    
    @abstractmethod
    def parse(self, file_path: Path) -> List[Transaction]:
        """Парсинг файла выписки"""
        pass
        
    @abstractmethod
    def extract_payment_period(self, file_path: Path) -> Optional[PaymentPeriod]:
        """Извлечение периода платежей"""
        pass
```

#### Report Writer Interface
```python
class ReportWriter(ABC):
    """Интерфейс для записи отчетов"""
    
    @abstractmethod
    def write_report(self, report: PaymentReport, file_path: Path) -> None:
        """Запись отчета в файл"""
        pass
```

### Конфигурация

#### Configuration Schema
```yaml
# config/default_config.yaml
localization:
  default_language: "ru"      # Язык по умолчанию
  fallback_language: "en"     # Резервный язык

payment_matching:
  search_window_days: 7       # Окно поиска платежей (дни)
  grace_period_days: 3        # Льготный период (дни)
  
parsing:
  search_window_days: 7       # Для обратной совместимости
  grace_period_days: 3
  
file_handling:
  max_file_size_mb: 100       # Максимальный размер файла
  supported_formats:          # Поддерживаемые форматы
    - ".xlsx"
    - ".xls"
```

#### Environment Variables
```bash
# Язык интерфейса
GARAGE_TRACKER_LANG=ru|en

# Уровень логирования  
GARAGE_TRACKER_LOG_LEVEL=DEBUG|INFO|WARNING|ERROR

# Директория конфигурации
GARAGE_TRACKER_CONFIG_DIR=/path/to/config

# Директория данных
GARAGE_TRACKER_DATA_DIR=/path/to/data
```

### Локализационные ключи

#### Status Messages
```json
{
  "status": {
    "received": "Получен",
    "overdue": "Просрочен", 
    "pending": "Ожидается",
    "not_due": "Срок не наступил",
    "unclear": "Неясно"
  }
}
```

#### Payment Notes
```json
{
  "notes": {
    "payment_found": "Платеж найден",
    "payment_not_found": "Платеж не найден",
    "wide_search_match": "Найден расширенным поиском",
    "multiple_matches": "Несколько совпадений найдено",
    "closest_match": "выбрано ближайшее к ожидаемой дате",
    "amount_shared": "Конфликт сумм с гаражами: {garages}"
  }
}
```

#### Summary Messages
```json
{
  "summary": {
    "total_garages": "Всего гаражей: {count}",
    "received_count": "Получено: {count}",
    "overdue_count": "Просрочено: {count}",
    "pending_count": "Ожидается: {count}",
    "not_due_count": "Срок не наступил: {count}",
    "collection_rate": "Процент сбора: {rate}%",
    "expected_amount": "Ожидаемая сумма: {amount} руб.",
    "received_amount": "Полученная сумма: {amount} руб."
  }
}
```

## 🧪 Testing Framework

### Unit Tests Structure
```
tests/
├── unit/
│   ├── core/
│   │   ├── test_garage.py
│   │   ├── test_payment.py
│   │   └── services/
│   │       ├── test_payment_matcher.py
│   │       └── test_status_determiner.py
│   ├── application/
│   │   └── test_process_payments_usecase.py
│   └── infrastructure/
│       ├── test_excel_writer.py
│       ├── test_localization.py
│       └── parsers/
│           ├── test_garage_parser.py
│           └── test_sberbank_parser.py
└── integration/
    ├── test_end_to_end.py
    └── test_file_processing.py
```

### Test Utilities
```python
# tests/conftest.py
import pytest
from pathlib import Path
from src.core.models.garage import Garage
from src.infrastructure.localization.i18n import LocalizationManager

@pytest.fixture
def sample_garage():
    """Фикстура для тестового гаража"""
    return Garage(
        id=1,
        monthly_rent=Decimal('5000'),
        start_date=date(2024, 1, 1),
        payment_day=1
    )

@pytest.fixture
def localization_manager():
    """Фикстура менеджера локализации"""
    return LocalizationManager('ru')

@pytest.fixture
def temp_excel_file(tmp_path):
    """Создание временного Excel файла"""
    file_path = tmp_path / "test.xlsx"
    # Создание тестового файла
    return file_path
```

## 📈 Performance Considerations

### Оптимизация производительности

1. **Lazy Loading** - файлы загружаются только при необходимости
2. **Memory Management** - использование генераторов для больших файлов
3. **Caching** - кеширование локализационных сообщений
4. **Batch Processing** - пакетная обработка транзакций

### Масштабируемость

```python
# Для больших файлов используйте streaming
def parse_large_statement(file_path: Path) -> Generator[Transaction, None, None]:
    """Streaming парсинг для больших выписок"""
    wb = openpyxl.load_workbook(file_path, read_only=True)
    ws = wb.active
    
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0]:  # Проверка что строка не пустая
            yield Transaction(
                date=row[0],
                amount=Decimal(str(row[1])),
                description=row[2] or ""
            )
```

## 🔒 Error Handling

### Exception Hierarchy
```python
class GarageTrackerError(Exception):
    """Базовое исключение приложения"""
    pass

class ParseError(GarageTrackerError):
    """Ошибки парсинга файлов"""
    pass

class ValidationError(GarageTrackerError):
    """Ошибки валидации данных"""
    pass

class DataIntegrityError(GarageTrackerError):
    """Ошибки целостности данных"""
    pass

class ConfigurationError(GarageTrackerError):
    """Ошибки конфигурации"""
    pass
```

### Error Recovery Strategies
```python
def safe_parse_amount(value: str) -> Optional[Decimal]:
    """Безопасное преобразование в Decimal"""
    try:
        return Decimal(str(value).replace(',', '.'))
    except (ValueError, TypeError, InvalidOperation):
        logger.warning(f"Could not parse amount: {value}")
        return None

def retry_with_backoff(func, max_retries: int = 3):
    """Повтор операции с экспоненциальной задержкой"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

## 🚀 Extension Points

### Добавление нового банка

1. **Создайте парсер**:
```python
class NewBankStatementParser(StatementParser):
    """Парсер для нового банка"""
    
    def parse(self, file_path: Path) -> List[Transaction]:
        # Реализация парсинга
        pass
        
    def extract_payment_period(self, file_path: Path) -> Optional[PaymentPeriod]:
        # Реализация извлечения периода
        pass
```

2. **Обновите фабрику**:
```python
def create_statement_parser(self, bank_type: str = "sberbank") -> StatementParser:
    if bank_type == "sberbank":
        return SberbankStatementParser()
    elif bank_type == "newbank":
        return NewBankStatementParser()
    else:
        raise ValueError(f"Unsupported bank type: {bank_type}")
```

### Добавление нового формата отчета

1. **Создайте writer**:
```python
class PDFReportWriter(ReportWriter):
    """Генератор PDF отчетов"""
    
    def write_report(self, report: PaymentReport, file_path: Path) -> None:
        # Реализация генерации PDF
        pass
```

2. **Обновите use case**:
```python
def execute(self, request: ReportGenerationRequest) -> ReportGenerationResponse:
    if request.format == "excel":
        writer = ExcelReportWriter()
    elif request.format == "pdf":
        writer = PDFReportWriter()
    # ...
```

### Добавление веб-интерфейса

```python
# src/interfaces/web/app.py
from flask import Flask, request, jsonify

class WebApp:
    """Flask веб-приложение"""
    
    def __init__(self, process_payments_usecase: ProcessPaymentsUseCase):
        self.app = Flask(__name__)
        self.process_payments_usecase = process_payments_usecase
        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.route('/api/process-payments', methods=['POST'])
        def process_payments():
            # Обработка через тот же use case
            request_data = request.get_json()
            # ...
```

---

*Справочник API обновлен: Август 2025*
*Версия архитектуры: 3.0 (Clean Architecture с полной локализацией)*