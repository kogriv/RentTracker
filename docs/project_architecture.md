# АРХИТЕКТУРА ПРОЕКТА
## Система отслеживания арендных платежей

---

## 1. ПРИНЦИПЫ АРХИТЕКТУРЫ

### 1.1 Основные принципы
- **Простота**: Минимальная необходимая сложность для базовой функциональности
- **Расширяемость**: Возможность добавления новых компонентов без изменения существующих
- **Поэтапность**: Разработка от ядра к периферии
- **Инкапсуляция**: Четкое разделение ответственности между модулями
- **Конфигурируемость**: Настройка поведения через конфигурационные файлы

### 1.2 Архитектурные слои
```
┌─────────────────────────────────────┐
│        INTERFACE LAYER              │  ← CLI, Web, Bot (поэтапно)
├─────────────────────────────────────┤
│        APPLICATION LAYER            │  ← Бизнес-логика, сценарии
├─────────────────────────────────────┤
│        DOMAIN LAYER                 │  ← Ядро системы, модели
├─────────────────────────────────────┤
│        INFRASTRUCTURE LAYER         │  ← Файлы, парсеры, отчеты
└─────────────────────────────────────┘
```

---

## 2. СТРУКТУРА ПРОЕКТА

### 2.1 Файловая структура
```
garage-payment-tracker/
│
├── src/
│   ├── core/                          # Ядро системы (Domain Layer)
│   │   ├── models/
│   │   │   ├── garage.py              # Модель гаража
│   │   │   ├── payment.py             # Модель платежа
│   │   │   ├── transaction.py         # Модель транзакции
│   │   │   └── report.py              # Модель отчета
│   │   ├── services/
│   │   │   ├── payment_matcher.py     # Сопоставление платежей
│   │   │   ├── date_calculator.py     # Расчет дат
│   │   │   └── status_determiner.py   # Определение статусов
│   │   └── exceptions.py              # Специфичные исключения
│   │
│   ├── parsers/                       # Infrastructure Layer - Парсеры
│   │   ├── base/
│   │   │   ├── parser_interface.py    # Абстрактный интерфейс парсера
│   │   │   └── parser_factory.py      # Фабрика парсеров
│   │   ├── file_parsers/
│   │   │   ├── excel_parser.py        # Парсинг Excel файлов
│   │   │   └── sberbank_parser.py     # Специфичный парсер Сбербанка
│   │   └── llm_parsers/               # Для будущего развития
│   │       └── llm_parser.py          # LLM-парсер (заглушка)
│   │
│   ├── application/                   # Application Layer - Сценарии
│   │   ├── use_cases/
│   │   │   ├── process_payments.py    # Основной сценарий обработки
│   │   │   └── generate_report.py     # Генерация отчета
│   │   └── dto/
│   │       ├── payment_request.py     # DTO для запросов
│   │       └── report_response.py     # DTO для ответов
│   │
│   ├── interfaces/                    # Interface Layer - Интерфейсы
│   │   ├── cli/
│   │   │   ├── cli_app.py            # CLI приложение
│   │   │   └── commands/
│   │   │       ├── process_command.py
│   │   │       └── report_command.py
│   │   ├── web/                       # Для будущего развития
│   │   │   └── web_app.py            # Flask/FastAPI приложение
│   │   └── bot/                       # Для будущего развития
│   │       └── telegram_bot.py       # Telegram бот
│   │
│   ├── infrastructure/                # Infrastructure Layer - Утилиты
│   │   ├── file_handlers/
│   │   │   ├── excel_reader.py       # Чтение Excel файлов
│   │   │   └── excel_writer.py       # Запись Excel файлов
│   │   ├── config/
│   │   │   ├── config_manager.py     # Управление конфигурацией
│   │   │   └── settings.py           # Настройки приложения
│   │   └── localization/
│   │       ├── i18n.py              # Система локализации
│   │       ├── messages_en.json     # Английские сообщения
│   │       └── messages_ru.json     # Русские сообщения (будущее)
│   │
│   └── utils/
│       ├── date_utils.py             # Утилиты для работы с датами
│       ├── validation.py             # Валидация данных
│       └── logging_config.py         # Настройка логирования
│
├── config/
│   ├── default_config.yaml           # Конфигурация по умолчанию
│   └── parser_rules.yaml             # Правила парсинга
│
├── tests/
│   ├── unit/                         # Юнит-тесты (TDD)
│   │   ├── core/
│   │   │   ├── models/
│   │   │   │   ├── test_garage.py
│   │   │   │   ├── test_payment.py
│   │   │   │   └── test_transaction.py
│   │   │   └── services/
│   │   │       ├── test_payment_matcher.py
│   │   │       ├── test_date_calculator.py
│   │   │       └── test_status_determiner.py
│   │   ├── parsers/
│   │   │   ├── test_excel_parser.py
│   │   │   └── test_sberbank_parser.py
│   │   ├── application/
│   │   │   └── test_process_payments_use_case.py
│   │   └── infrastructure/
│   │       ├── test_config_manager.py
│   │       └── test_localization.py
│   ├── integration/                  # Интеграционные тесты
│   │   ├── test_full_payment_flow.py
│   │   └── test_cli_integration.py
│   ├── fixtures/                     # Тестовые данные и моки
│   │   ├── sample_arenda.xlsx
│   │   ├── sample_statement.xlsx
│   │   └── mock_data.py
│   └── conftest.py                   # Pytest конфигурация и общие фикстуры
│
├── docs/
│   ├── architecture.md               # Архитектурная документация
│   └── user_guide.md                 # Руководство пользователя
│
├── requirements.txt                  # Python зависимости
├── requirements-dev.txt              # Зависимости для разработки (pytest, coverage, etc.)
├── setup.py                         # Установочный скрипт
├── pytest.ini                       # Конфигурация pytest
├── .coverage                        # Настройки покрытия кода
├── Makefile                         # Команды для TDD workflow
└── main.py                          # Точка входа в приложение
```

---

## 3. КЛЮЧЕВЫЕ КОМПОНЕНТЫ

### 3.1 Core Models (Доменные модели)

```python
# src/core/models/garage.py
@dataclass
class Garage:
    id: str
    monthly_rent: Decimal
    payment_day: int
    start_date: date
    
# src/core/models/payment.py
@dataclass  
class Payment:
    garage_id: str
    amount: Decimal
    expected_date: date
    actual_date: Optional[date]
    status: PaymentStatus
    
# src/core/models/transaction.py
@dataclass
class Transaction:
    date: date
    amount: Decimal
    category: str
    source: str
```

### 3.2 Parser Interface (Инкапсуляция парсинга)

```python
# src/parsers/base/parser_interface.py
from abc import ABC, abstractmethod

class StatementParser(ABC):
    @abstractmethod
    def parse_transactions(self, source) -> List[Transaction]:
        """Парсинг транзакций из источника"""
        pass
    
    @abstractmethod
    def validate_source(self, source) -> bool:
        """Валидация источника данных"""
        pass

# src/parsers/base/parser_factory.py
class ParserFactory:
    def create_parser(self, parser_type: str) -> StatementParser:
        if parser_type == "excel":
            return ExcelStatementParser()
        elif parser_type == "llm":
            return LLMStatementParser()  # Будущая реализация
        else:
            raise ValueError(f"Unknown parser type: {parser_type}")
```

### 3.3 Application Use Cases (Сценарии использования)

```python
# src/application/use_cases/process_payments.py
class ProcessPaymentsUseCase:
    def __init__(self, parser_factory, payment_matcher, status_determiner):
        self.parser_factory = parser_factory
        self.payment_matcher = payment_matcher
        self.status_determiner = status_determiner
    
    def execute(self, request: PaymentProcessRequest) -> PaymentProcessResponse:
        # 1. Парсинг справочника гаражей
        # 2. Парсинг банковской выписки  
        # 3. Сопоставление платежей
        # 4. Определение статусов
        # 5. Возврат результата
        pass
```

### 3.4 Configuration System (Система конфигурации)

```yaml
# config/default_config.yaml
application:
  name: "Garage Payment Tracker"
  version: "1.0.0"
  default_language: "en"

parsing:
  grace_period_days: 3
  search_window_days: 7
  date_formats: ["DD.MM.YYYY", "DD/MM/YYYY"]
  
parsers:
  default: "excel"
  available: ["excel", "llm"]
  
output:
  format: "xlsx"
  include_summary: true
```

### 3.5 Localization System (Система локализации)

```python
# src/infrastructure/localization/i18n.py
class LocalizationManager:
    def __init__(self, language="en"):
        self.language = language
        self.messages = self._load_messages()
    
    def get(self, key: str, **kwargs) -> str:
        message = self.messages.get(key, key)
        return message.format(**kwargs) if kwargs else message
```

```json
// src/infrastructure/localization/messages_en.json
{
  "status.received": "Received",
  "status.overdue": "Overdue", 
  "status.pending": "Pending",
  "error.file_not_found": "File not found: {filename}",
  "report.generated": "Report generated successfully"
}
```

---

## 9. ПОЭТАПНЫЙ ПЛАН РАЗРАБОТКИ

### 9.1 Этап 1: Минимальное ядро (MVP)

**Цель:** Базовая функциональность с CLI интерфейсом

**Компоненты:**
- Core models (Garage, Payment, Transaction)
- Excel parser для справочника и выписки Сбербанка
- Базовая логика сопоставления платежей
- CLI интерфейс с командой `process-payments`
- Генерация Excel отчета

**Конкретные результаты:**
- ✅ **Работающий CLI**: `python main.py process-payments --garage-file arenda.xlsx --statement-file print2.xlsx`
- ✅ **Парсинг данных**: чтение справочника гаражей и банковской выписки
- ✅ **Сопоставление платежей**: поиск соответствий по точной сумме
- ✅ **Определение статусов**: Received, Overdue, Pending, NotDue
- ✅ **Excel отчет**: файл с колонками (Garage, Amount, Expected Date, Actual Date, Status, Notes)
- ✅ **Обработка реальных данных**: 15 гаражей, 66 транзакций из тестовых файлов

**Критерии готовности (TDD):**
- Базовые тесты для моделей проходят
- Парсер корректно извлекает все 66 транзакций
- Система находит 10+ совпадений из 14 возможных сумм
- CLI генерирует читаемый Excel отчет

### 9.2 Этап 2: Улучшение парсинга

**Цель:** Более гибкий и надежный парсинг

**Компоненты:**
- Рефакторинг в сторону Parser Interface
- Добавление правил парсинга в конфигурацию
- Улучшенная обработка ошибок
- Логирование процесса парсинга

**Конкретные результаты:**
- ✅ **Абстракция парсеров**: StatementParser интерфейс с возможностью добавления новых банков
- ✅ **Конфигурируемые правила**: YAML файл с паттернами дат и сумм
- ✅ **Обработка ошибок**: информативные сообщения при некорректных файлах
- ✅ **Логирование**: запись процесса парсинга в лог-файл
- ✅ **Валидация входных данных**: проверка структуры файлов перед обработкой
- ✅ **Обработка edge cases**: пустые строки, некорректные форматы, отсутствующие файлы

**Критерии готовности (TDD):**
- Тесты парсеров с различными входными данными проходят
- Система корректно обрабатывает поврежденные файлы
- Логи содержат полную информацию о процессе

### 9.3 Этап 3: Расширение функциональности

**Цель:** Дополнительные возможности и интерфейсы

**Компоненты:**
- Система локализации (русский язык)
- Дополнительные статусы и аналитика
- Конфигурируемые правила валидации
- Веб-интерфейс (опционально)

**Конкретные результаты:**
- ✅ **Русский интерфейс**: `--lang ru` переключает CLI и отчеты на русский
- ✅ **Расширенная аналитика**: сводная статистика в конце отчета
- ✅ **Дополнительные статусы**: "Неопределенно" для конфликтных случаев
- ✅ **Конфигурируемые правила**: настройка льготных периодов, временных окон
- ✅ **Улучшенные отчеты**: дополнительные колонки (Days Overdue, Next Payment Date)
- ✅ **Заготовка веб-интерфейса**: базовая HTML страница для загрузки файлов

**Критерии готовности (TDD):**
- Локализация работает для основных элементов
- Конфигурационные изменения применяются корректно
- Дополнительная аналитика рассчитывается правильно

### 9.4 Этап 4: Интеграции и автоматизация

**Цель:** LLM парсинг и дополнительные интерфейсы

**Компоненты:**
- LLM Parser для сложных форматов выписок
- Telegram бот интерфейс
- API для интеграции с другими системами
- Планировщик задач

**Конкретные результаты:**
- ✅ **LLM парсер**: отправка выписки в ChatGPT/Claude для извлечения транзакций
- ✅ **Telegram бот**: загрузка файлов через бота, получение отчета
- ✅ **REST API**: эндпоинты для программной интеграции
- ✅ **Планировщик**: автоматический запуск обработки по расписанию
- ✅ **Уведомления**: отправка алертов о просроченных платежах
- ✅ **История обработки**: сохранение результатов предыдущих запусков

**Критерии готовности (TDD):**
- LLM парсер корректно извлекает данные из нестандартных форматов
- API возвращает правильные ответы на тестовых данных
- Планировщик выполняет задачи по расписанию

### 9.5 Итоговый результат

**Финальная система включает:**
- 🎯 **CLI приложение** с полной функциональностью
- 📊 **Точная обработка** банковских выписок различных форматов
- 🤖 **ИИ-парсинг** для сложных случаев
- 🌐 **Веб-интерфейс** и **Telegram бот**
- 🔧 **REST API** для интеграций
- 📈 **Аналитика и отчетность**
- 🌍 **Многоязычность** (английский/русский)
- ⚙️ **Гибкая конфигурация** под разные сценарии использования

**Масштабируемость:** Архитектура позволяет легко добавлять новые банки, интерфейсы и интеграции без изменения базового кода.

---

## 10. АРХИТЕКТУРНЫЕ ПАТТЕРНЫ

### 5.1 Dependency Injection
```python
# main.py
def create_app() -> Application:
    config = ConfigManager.load_config()
    
    # Infrastructure
    parser_factory = ParserFactory()
    excel_reader = ExcelReader()
    excel_writer = ExcelWriter()
    
    # Core services
    payment_matcher = PaymentMatcher(config.parsing)
    status_determiner = StatusDeterminer(config.parsing)
    
    # Application services
    process_use_case = ProcessPaymentsUseCase(
        parser_factory, payment_matcher, status_determiner
    )
    
    # Interface
    cli_app = CLIApp(process_use_case, config.localization)
    
    return cli_app
```

### 5.2 Strategy Pattern (для парсеров)
```python
class PaymentProcessor:
    def __init__(self, parser_strategy: StatementParser):
        self.parser = parser_strategy
    
    def set_parser(self, parser: StatementParser):
        self.parser = parser
    
    def process(self, statement_source):
        return self.parser.parse_transactions(statement_source)
```

### 5.3 Factory Pattern (для создания компонентов)
```python
class ComponentFactory:
    @staticmethod
    def create_parser(config: dict) -> StatementParser:
        parser_type = config.get('parsers', {}).get('default', 'excel')
        return ParserFactory().create_parser(parser_type)
    
    @staticmethod  
    def create_interface(interface_type: str, use_cases: dict):
        if interface_type == "cli":
            return CLIApp(use_cases)
        elif interface_type == "web":
            return WebApp(use_cases)
        # и т.д.
```

---

## 11. КОНФИГУРАЦИЯ И РАСШИРЯЕМОСТЬ

### 6.1 Конфигурационные файлы
- `default_config.yaml` - основные настройки
- `parser_rules.yaml` - правила парсинга для разных банков
- `messages_*.json` - тексты интерфейса на разных языках

### 6.2 Механизм плагинов (для будущего)
```python
# src/plugins/plugin_interface.py
class Plugin(ABC):
    @abstractmethod
    def initialize(self, config: dict):
        pass
    
    @abstractmethod  
    def get_parser(self) -> Optional[StatementParser]:
        pass
        
    @abstractmethod
    def get_interface(self) -> Optional[UserInterface]:
        pass
```

### 6.3 Конфигурируемые правила бизнес-логики
```yaml
# config/business_rules.yaml
payment_matching:
  exact_amount_match: true
  tolerance_percentage: 0.0
  search_window_days: 7
  grace_period_days: 3

status_determination:
  overdue_threshold_days: 3
  pending_grace_period: 3
  future_payment_window: 30
```

---

## 7. ПРЕИМУЩЕСТВА АРХИТЕКТУРЫ

### 7.1 Простота
- Четкое разделение слоев
- Минимальная связанность между компонентами
- Простые интерфейсы взаимодействия

### 7.2 Расширяемость
- Новые парсеры через Strategy Pattern
- Новые интерфейсы через Factory Pattern
- Новая бизнес-логика через конфигурацию

### 7.3 Тестируемость
- Изолированные компоненты
- Внедрение зависимостей
- Моки для тестирования

### 7.4 Поэтапность
- Независимые модули
- Возможность замены компонентов
- Обратная совместимость

---

## 8. TDD (TEST-DRIVEN DEVELOPMENT) АРХИТЕКТУРА

### 8.1 TDD Принципы в архитектуре

**Red-Green-Refactor цикл:**
1. **Red**: Написать падающий тест для новой функциональности
2. **Green**: Написать минимальный код для прохождения теста
3. **Refactor**: Улучшить код, сохраняя работоспособность тестов

**Архитектурные требования для TDD:**
- **Высокая тестируемость**: Все компоненты должны быть легко тестируемы в изоляции
- **Внедрение зависимостей**: Для подмены зависимостей моками
- **Четкие интерфейсы**: Абстракции для создания тест-дублеров
- **Быстрые тесты**: Минимизация внешних зависимостей в юнит-тестах

### 8.2 Структура тестов

```
tests/
├── unit/                    # Быстрые изолированные тесты
│   ├── core/               # Тесты доменной логики
│   ├── parsers/            # Тесты парсеров
│   ├── application/        # Тесты use cases
│   └── infrastructure/     # Тесты утилит
├── integration/            # Тесты взаимодействия компонентов
├── fixtures/               # Общие тестовые данные
└── conftest.py            # Pytest фикстуры
```

### 8.3 Примеры TDD реализации

#### Доменная модель с тестами
```python
# tests/unit/core/models/test_garage.py
import pytest
from decimal import Decimal
from datetime import date
from src.core.models.garage import Garage

class TestGarage:
    def test_garage_creation_with_valid_data(self):
        # Arrange & Act
        garage = Garage(
            id="1",
            monthly_rent=Decimal("3500.00"),
            payment_day=15,
            start_date=date(2025, 1, 15)
        )
        
        # Assert
        assert garage.id == "1"
        assert garage.monthly_rent == Decimal("3500.00")
        assert garage.payment_day == 15
        assert garage.start_date == date(2025, 1, 15)
    
    def test_garage_creation_with_invalid_payment_day_raises_error(self):
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Payment day must be between 1 and 31"):
            Garage(
                id="1",
                monthly_rent=Decimal("3500.00"),
                payment_day=32,  # Invalid day
                start_date=date(2025, 1, 15)
            )
    
    def test_garage_next_payment_date_calculation(self):
        # Arrange
        garage = Garage(
            id="1",
            monthly_rent=Decimal("3500.00"),
            payment_day=15,
            start_date=date(2025, 1, 15)
        )
        
        # Act
        next_payment = garage.get_next_payment_date(date(2025, 2, 1))
        
        # Assert
        assert next_payment == date(2025, 2, 15)
```

```python
# src/core/models/garage.py (реализация после тестов)
from dataclass import dataclass
from decimal import Decimal
from datetime import date, datetime
from calendar import monthrange

@dataclass
class Garage:
    id: str
    monthly_rent: Decimal
    payment_day: int
    start_date: date
    
    def __post_init__(self):
        if not 1 <= self.payment_day <= 31:
            raise ValueError("Payment day must be between 1 and 31")
    
    def get_next_payment_date(self, current_date: date) -> date:
        """Calculate next payment date based on payment day"""
        year = current_date.year
        month = current_date.month
        
        # If current day is past payment day, next payment is next month
        if current_date.day > self.payment_day:
            month += 1
            if month > 12:
                month = 1
                year += 1
        
        # Handle month-end edge cases
        days_in_month = monthrange(year, month)[1]
        payment_day = min(self.payment_day, days_in_month)
        
        return date(year, month, payment_day)
```

#### Парсер с моками
```python
# tests/unit/parsers/test_excel_parser.py
import pytest  
from unittest.mock import Mock, patch
from src.parsers.file_parsers.excel_parser import ExcelStatementParser
from src.core.models.transaction import Transaction

class TestExcelStatementParser:
    def test_parse_transactions_returns_valid_transactions(self):
        # Arrange
        parser = ExcelStatementParser()
        mock_excel_data = [
            ['12.06.2025 12:00', '12:00', '', 'Перевод на карту', '+2 750,00'],
            ['11.06.2025 11:30', '11:30', '', 'Перевод СБП', '+3 500,00']
        ]
        
        with patch('src.parsers.file_parsers.excel_parser.read_excel') as mock_read:
            mock_read.return_value = mock_excel_data
            
            # Act
            transactions = parser.parse_transactions('fake_file.xlsx')
            
            # Assert
            assert len(transactions) == 2
            assert transactions[0].amount == 2750.00
            assert transactions[0].date.strftime('%d.%m.%Y') == '12.06.2025'
            assert transactions[1].amount == 3500.00
            assert transactions[1].category == 'Перевод СБП'
    
    def test_parse_transactions_with_invalid_format_raises_error(self):
        # Arrange
        parser = ExcelStatementParser()
        
        with patch('src.parsers.file_parsers.excel_parser.read_excel') as mock_read:
            mock_read.side_effect = FileNotFoundError("File not found")
            
            # Act & Assert
            with pytest.raises(FileNotFoundError):
                parser.parse_transactions('non_existent_file.xlsx')
```

#### Use Case с инъекцией зависимостей
```python
# tests/unit/application/test_process_payments_use_case.py
import pytest
from unittest.mock import Mock
from src.application.use_cases.process_payments import ProcessPaymentsUseCase
from src.application.dto.payment_request import PaymentProcessRequest

class TestProcessPaymentsUseCase:
    def test_execute_successfully_processes_payments(self):
        # Arrange
        mock_parser_factory = Mock()
        mock_payment_matcher = Mock() 
        mock_status_determiner = Mock()
        mock_report_generator = Mock()
        
        use_case = ProcessPaymentsUseCase(
            parser_factory=mock_parser_factory,
            payment_matcher=mock_payment_matcher,
            status_determiner=mock_status_determiner,
            report_generator=mock_report_generator
        )
        
        request = PaymentProcessRequest(
            garage_file='garages.xlsx',
            statement_file='statement.xlsx'
        )
        
        # Mock возвращаемые значения
        mock_parser_factory.create_parser.return_value.parse_garages.return_value = []
        mock_parser_factory.create_parser.return_value.parse_transactions.return_value = []
        mock_payment_matcher.match_payments.return_value = []
        mock_status_determiner.determine_statuses.return_value = []
        
        # Act
        result = use_case.execute(request)
        
        # Assert
        assert result.success == True
        mock_parser_factory.create_parser.assert_called()
        mock_payment_matcher.match_payments.assert_called_once()
        mock_status_determiner.determine_statuses.assert_called_once()
```

### 8.4 Конфигурация для TDD

#### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

#### requirements-dev.txt
```
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.0.0
pytest-xdist>=3.0.0  # Parallel test execution
coverage>=7.0.0
factory-boy>=3.0.0   # Test data factories
freezegun>=1.2.0     # Date mocking
```

#### Makefile для TDD workflow
```makefile
.PHONY: test test-unit test-integration coverage clean install-dev

# TDD Commands
test:
	pytest

test-unit:
	pytest tests/unit -m "not slow"

test-integration:
	pytest tests/integration

test-fast:
	pytest tests/unit -x --ff

coverage:
	pytest --cov=src --cov-report=html --cov-report=term

# TDD Workflow
tdd:
	pytest --looponfail tests/unit

# Development setup
install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

clean:
	rm -rf .coverage htmlcov/ .pytest_cache/
	find . -type d -name __pycache__ -delete
```

### 8.5 TDD-ориентированные архитектурные паттерны

#### Фабрика тестовых данных
```python
# tests/fixtures/factories.py
import factory
from decimal import Decimal
from datetime import date
from src.core.models.garage import Garage
from src.core.models.transaction import Transaction

class GarageFactory(factory.Factory):
    class Meta:
        model = Garage
    
    id = factory.Sequence(lambda n: str(n))
    monthly_rent = factory.LazyFunction(lambda: Decimal("3500.00"))
    payment_day = 15
    start_date = date(2025, 1, 15)

class TransactionFactory(factory.Factory):
    class Meta:
        model = Transaction
    
    date = date(2025, 6, 15)
    amount = factory.LazyFunction(lambda: Decimal("3500.00"))
    category = "Перевод на карту"
    source = "bank_statement"
```

#### Тестовые дублеры (Test Doubles)
```python
# tests/fixtures/mock_data.py
class MockStatementParser:
    def __init__(self, transactions=None):
        self.transactions = transactions or []
    
    def parse_transactions(self, source):
        return self.transactions
    
    def validate_source(self, source):
        return True

class MockPaymentMatcher:
    def __init__(self, matches=None):
        self.matches = matches or {}
    
    def match_payments(self, garages, transactions):
        return self.matches
```

### 8.6 TDD этапы разработки

#### Этап 1: Доменные модели (TDD Core)
1. Написать тесты для `Garage` модели
2. Реализовать `Garage` класс 
3. Написать тесты для `Payment` модели
4. Реализовать `Payment` класс
5. Рефакторинг и оптимизация

#### Этап 2: Сервисы (TDD Services) 
1. Тесты для `DateCalculator`
2. Реализация `DateCalculator`
3. Тесты для `PaymentMatcher`
4. Реализация `PaymentMatcher`
5. Интеграционные тесты сервисов

#### Этап 3: Use Cases (TDD Application)
1. Тесты для `ProcessPaymentsUseCase`
2. Реализация use case с моками
3. Интеграционные тесты с реальными сервисами

### 8.6 Упрощенный TDD подход

Для небольшого приложения используем прагматичный TDD:
- **Пишем тесты для критической логики**: парсинг, сопоставление платежей, расчет дат
- **Простые юнит-тесты**: без сложных моков, фокус на бизнес-логике
- **Быстрая обратная связь**: тесты должны выполняться за секунды
- **Тесты как критерий готовности**: каждый этап считается завершенным при прохождении тестов

TDD интегрируется естественно: пишем тест → реализуем функцию → рефакторим при необходимости.