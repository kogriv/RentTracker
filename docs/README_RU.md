# Трекер Платежей за Гаражи

Автоматизированная система отслеживания арендных платежей за гаражи с интеллектуальной обработкой транзакций и комплексной финансовой отчетностью.

## 📋 Содержание

- [Обзор системы](#обзор-системы)
- [Настройка окружения](#настройка-окружения)
- [Установка и запуск](#установка-и-запуск)
- [Руководство пользователя](#руководство-пользователя)
- [Командный интерфейс](#командный-интерфейс)
- [Интерактивная оболочка](#интерактивная-оболочка)
- [Примеры использования](#примеры-использования)
- [Устранение неполадок](#устранение-неполадок)

## 🎯 Обзор системы

Трекер Платежей за Гаражи - это Python-приложение командной строки, которое автоматизирует процесс сопоставления транзакций из банковской выписки с ожидаемыми арендными платежами за гараж, определяет статусы платежей и генерирует комплексные Excel отчеты.

### Ключевые возможности

- ✅ **Автоматическое сопоставление платежей** - интеллектуальное сопоставление банковских транзакций с ожидаемыми платежами
- ✅ **Автоматическое определение периода** - извлечение периода анализа непосредственно из банковской выписки
- ✅ **Расширенный поиск платежей** - двухуровневая система поиска для максимального обнаружения платежей
- ✅ **Комплексная отчетность** - детальные Excel отчеты с сводной статистикой
- ✅ **Полная русификация** - поддержка русского и английского языков
- ✅ **Интерактивный интерфейс** - удобное меню с автоматическим обнаружением файлов
- ✅ **Расчет просрочки** - точный расчет дней просрочки для всех типов платежей

### Поддерживаемые форматы файлов

- **Входные файлы**: Excel (.xlsx, .xls) для справочника гаражей и банковских выписок
- **Выходные файлы**: Excel отчеты с форматированными листами и статистикой
- **Конфигурация**: YAML файлы для настроек приложения

## 🔧 Настройка окружения

### Системные требования

- Python 3.11 или выше
- Операционная система: Windows 10/11, Linux (Ubuntu 20.04+), macOS

### Установка Python

#### Windows

1. **Скачайте Python** с официального сайта [python.org](https://python.org/downloads/)
2. **Запустите установщик** и обязательно отметьте:
   - ☑️ "Add Python to PATH"
   - ☑️ "Install pip"
3. **Проверьте установку**:
   ```cmd
   python --version
   pip --version
   ```

#### Linux (Ubuntu/Debian)

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python 3.11
sudo apt install python3.11 python3.11-pip python3.11-venv -y

# Создание симлинка (опционально)
sudo ln -sf /usr/bin/python3.11 /usr/bin/python

# Проверка установки
python --version
pip --version
```

#### Linux (CentOS/RHEL/Fedora)

```bash
# Для Fedora
sudo dnf install python3.11 python3.11-pip -y

# Для CentOS/RHEL (требуется EPEL)
sudo yum install epel-release -y
sudo yum install python3.11 python3.11-pip -y
```

### Настройка виртуального окружения

#### Windows

```cmd
# Создание виртуального окружения
python -m venv garage_tracker_env

# Активация
garage_tracker_env\Scripts\activate

# Проверка активации (должно появиться (garage_tracker_env) в начале строки)
```

#### Linux/macOS

```bash
# Создание виртуального окружения
python3.11 -m venv garage_tracker_env

# Активация
source garage_tracker_env/bin/activate

# Проверка активации (должно появиться (garage_tracker_env) в начале строки)
```

## 🚀 Установка и запуск

### 1. Клонирование проекта

```bash
# Если у вас есть доступ к репозиторию
git clone <repository-url>
cd garage-payment-tracker

# Или загрузите архив и распакуйте его
```

### 2. Установка зависимостей

```bash
# Убедитесь что виртуальное окружение активировано
pip install -r requirements.txt

# Или установите зависимости вручную
pip install openpyxl click pyyaml pytest pytest-cov
```

### 3. Проверка установки

```bash
# Проверка работы приложения
python main.py --help

# Должен отобразиться список доступных команд
```

### 4. Подготовка файлов

1. **Поместите файлы в папку `attached_assets/`**:
   - Справочник гаражей (например: `arenda.xlsx`)
   - Банковская выписка (например: `print.xlsx`)

2. **Проверьте формат файлов**:
   - Справочник должен содержать колонки: ID, сумма аренды, дата начала, день платежа
   - Выписка должна содержать колонки: дата, сумма, описание

## 📖 Руководство пользователя

### Быстрый старт

1. **Запустите интерактивный режим**:
   ```bash
   python run.py
   ```

2. **Выберите язык интерфейса**:
   - `1` - English
   - `2` - Русский

3. **Используйте автоматически обнаруженные файлы** или укажите свои

4. **Выберите команду** из интерактивного меню

### Структура проекта

```
garage-payment-tracker/
├── attached_assets/          # Входные файлы
│   ├── arenda.xlsx          # Справочник гаражей
│   └── print.xlsx           # Банковская выписка
├── output/                  # Выходные отчеты
├── logs/                    # Файлы логов
├── config/                  # Конфигурационные файлы
├── src/                     # Исходный код
├── tests/                   # Тесты
├── docs/                    # Документация
├── main.py                  # Основная точка входа
└── run.py                   # Интерактивный интерфейс
```

### Форматы входных файлов

#### Справочник гаражей (Excel)

| ID гаража | Сумма аренды | Дата начала | День платежа |
|-----------|--------------|-------------|--------------|
| 1         | 4295         | 2024-01-01  | 1            |
| 2         | 3301         | 2024-01-01  | 1            |

#### Банковская выписка (Excel)

| Дата       | Сумма операции | Категория | Описание           |
|------------|----------------|-----------|--------------------|
| 01.05.2025 | -3301.00       | Прочее    | Платеж по аренде   |
| 03.05.2025 | -3250.00       | Прочее    | Оплата за гараж    |

## 🖥️ Командный интерфейс

### Основные команды

#### 1. Интерактивный режим

```bash
python run.py
```

**Возможности:**
- Автоматическое обнаружение файлов в папке `attached_assets/`
- Автоматическое определение периода платежей из выписки
- Рекомендации по датам анализа
- Выбор языка интерфейса

#### 2. Обработка платежей

```bash
python main.py process-payments [OPTIONS]
```

**Обязательные параметры:**
- `--garage-file` - путь к файлу справочника гаражей
- `--statement-file` - путь к файлу банковской выписки

**Опциональные параметры:**
- `--output, -o` - путь для сохранения отчета (по умолчанию: `output/`)
- `--analysis-date` - дата анализа в формате YYYY-MM-DD (по умолчанию: текущая дата)
- `--lang, --language` - язык интерфейса (`en`/`ru`)
- `--verbose, -v` - подробные логи

**Примеры:**

```bash
# Базовая обработка
python main.py process-payments \
  --garage-file attached_assets/arenda.xlsx \
  --statement-file attached_assets/print.xlsx

# С указанием даты анализа
python main.py process-payments \
  --garage-file attached_assets/arenda.xlsx \
  --statement-file attached_assets/print.xlsx \
  --analysis-date 2025-05-20

# С русским интерфейсом и выводом в конкретный файл
python main.py --lang ru process-payments \
  --garage-file attached_assets/arenda.xlsx \
  --statement-file attached_assets/print.xlsx \
  --output my_report.xlsx

# С подробными логами
python main.py -v process-payments \
  --garage-file attached_assets/arenda.xlsx \
  --statement-file attached_assets/print.xlsx
```

#### 3. Справка

```bash
# Общая справка
python main.py --help

# Справка по конкретной команде
python main.py process-payments --help
```

### Переменные окружения

```bash
# Установка языка по умолчанию
export GARAGE_TRACKER_LANG=ru  # Linux/macOS
set GARAGE_TRACKER_LANG=ru     # Windows

# Установка уровня логирования
export GARAGE_TRACKER_LOG_LEVEL=DEBUG
```

## 🔧 Интерактивная оболочка

### Что такое интерактивная оболочка?

Интерактивная оболочка (пункт 5 в главном меню) - это встроенная командная строка, которая позволяет выполнять системные команды и команды приложения без выхода из программы.

### Зачем она нужна?

1. **Быстрый доступ к файлам** - просмотр содержимого папок без переключения окон
2. **Отладка и диагностика** - проверка версий, просмотр логов, анализ файлов
3. **Удобство работы** - выполнение команд не покидая приложение
4. **Обучение** - изучение возможностей приложения через справочную систему

### Доступные команды

#### Системные команды

```bash
# Просмотр содержимого папок
ls                          # Текущая папка
ls attached_assets/         # Входные файлы
ls output/                  # Выходные отчеты
ls logs/                    # Файлы логов

# Просмотр файлов
cat attached_assets/arenda.xlsx     # Не работает для Excel
head logs/app.log                   # Первые строки лога
tail logs/app.log                   # Последние строки лога

# Информация о системе
python --version            # Версия Python
pip list                    # Установленные пакеты
pwd                         # Текущая директория
```

#### Команды приложения

```bash
# Справочная система
python main.py --help                    # Общая справка
python main.py process-payments --help   # Справка по команде

# Тестирование с различными параметрами
python main.py --lang ru process-payments \
  --garage-file attached_assets/arenda.xlsx \
  --statement-file attached_assets/print.xlsx \
  --analysis-date 2025-05-15

# Проверка конфигурации
python -c "import yaml; print(yaml.safe_load(open('config/default_config.yaml')))"

# Запуск тестов
python -m pytest tests/ -v             # Все тесты
python -m pytest tests/unit/ -v        # Только unit тесты
```

#### Диагностические команды

```bash
# Проверка структуры файлов
file attached_assets/*.xlsx            # Тип файлов
du -h attached_assets/                 # Размер файлов
wc -l logs/*.log                       # Количество строк в логах

# Анализ отчетов
ls -la output/                         # Список созданных отчетов
python -c "
import openpyxl
wb = openpyxl.load_workbook('output/latest_report.xlsx')
print('Листы:', wb.sheetnames)
print('Данные первой строки:', [cell.value for cell in wb.active[1]])
"
```

### Практические примеры использования

#### Пример 1: Быстрая диагностика

```bash
# Вход в интерактивную оболочку
Введите ваш выбор (1-5) или 'q' для выхода: 5

# Проверка наличия файлов
>>> ls attached_assets/
arenda.xlsx  print.xlsx

# Проверка последних отчетов
>>> ls -t output/ | head -3
report_2025-08-01_11-36-31.xlsx
russian_test_report.xlsx
payment_report_20250801_113528.xlsx

# Просмотр последних логов
>>> tail -10 logs/app.log
```

#### Пример 2: Тестирование разных дат

```bash
# Тест с ранней датой
>>> python main.py process-payments \
    --garage-file attached_assets/arenda.xlsx \
    --statement-file attached_assets/print.xlsx \
    --analysis-date 2025-05-10 \
    --output output/test_early.xlsx

# Тест с поздней датой
>>> python main.py process-payments \
    --garage-file attached_assets/arenda.xlsx \
    --statement-file attached_assets/print.xlsx \
    --analysis-date 2025-06-01 \
    --output output/test_late.xlsx

# Сравнение результатов
>>> ls -la output/test_*.xlsx
```

#### Пример 3: Анализ производительности

```bash
# Запуск с подробными логами
>>> python main.py -v process-payments \
    --garage-file attached_assets/arenda.xlsx \
    --statement-file attached_assets/print.xlsx 2>&1 | tee logs/verbose.log

# Анализ времени выполнения
>>> grep "INFO" logs/verbose.log | tail -5

# Поиск предупреждений
>>> grep "WARNING" logs/verbose.log
```

### Выход из интерактивной оболочки

```bash
# Любой из способов:
>>> exit
>>> quit()
>>> Ctrl+C
>>> Ctrl+D
```

## 💡 Примеры использования

### Сценарий 1: Ежемесячная обработка

```bash
# 1. Подготовка
mkdir -p monthly_reports/2025-05

# 2. Запуск обработки
python main.py --lang ru process-payments \
  --garage-file attached_assets/arenda.xlsx \
  --statement-file attached_assets/statement_may_2025.xlsx \
  --analysis-date 2025-05-31 \
  --output monthly_reports/2025-05/may_report.xlsx

# 3. Просмотр результатов
ls -la monthly_reports/2025-05/
```

### Сценарий 2: Анализ просрочек

```bash
# Анализ на разные даты для отслеживания динамики просрочек
for date in 2025-05-15 2025-05-25 2025-06-01; do
  python main.py process-payments \
    --garage-file attached_assets/arenda.xlsx \
    --statement-file attached_assets/statement.xlsx \
    --analysis-date $date \
    --output "output/analysis_$date.xlsx"
done
```

### Сценарий 3: Автоматизация через скрипт

Создайте файл `process_monthly.sh` (Linux) или `process_monthly.bat` (Windows):

```bash
#!/bin/bash
# process_monthly.sh

# Настройки
GARAGE_FILE="attached_assets/arenda.xlsx"
STATEMENT_FILE="attached_assets/statement_$(date +%Y_%m).xlsx"
OUTPUT_DIR="monthly_reports/$(date +%Y-%m)"
ANALYSIS_DATE=$(date +%Y-%m-31)

# Создание папки для отчетов
mkdir -p "$OUTPUT_DIR"

# Обработка платежей
python main.py --lang ru process-payments \
  --garage-file "$GARAGE_FILE" \
  --statement-file "$STATEMENT_FILE" \
  --analysis-date "$ANALYSIS_DATE" \
  --output "$OUTPUT_DIR/monthly_report.xlsx"

echo "Отчет создан: $OUTPUT_DIR/monthly_report.xlsx"
```

## 🛠️ Устранение неполадок

### Частые проблемы и решения

#### 1. Ошибка "Python не найден"

**Windows:**
```cmd
# Проверка установки
where python
# Если не найден, переустановите Python с опцией "Add to PATH"
```

**Linux:**
```bash
# Установка Python
sudo apt install python3.11 python3.11-pip

# Создание симлинка
sudo ln -sf /usr/bin/python3.11 /usr/bin/python
```

#### 2. Ошибка "Модуль не найден"

```bash
# Проверка виртуального окружения
which python
pip list

# Переустановка зависимостей
pip install --upgrade -r requirements.txt
```

#### 3. Ошибка "Файл не найден"

```bash
# Проверка структуры папок
ls -la attached_assets/
ls -la output/

# Проверка прав доступа
chmod 755 attached_assets/
chmod 755 output/
```

#### 4. Ошибка "Неверный формат Excel"

```bash
# Проверка файла
file attached_assets/arenda.xlsx

# Конвертация в нужный формат (если нужно)
python -c "
import pandas as pd
df = pd.read_excel('old_file.xls')
df.to_excel('attached_assets/arenda.xlsx', index=False)
"
```

#### 5. Проблемы с кодировкой

```bash
# Установка переменных окружения для русского языка
export LANG=ru_RU.UTF-8  # Linux
export LC_ALL=ru_RU.UTF-8

# Windows (в cmd)
chcp 65001
```

### Диагностика проблем

#### Проверка конфигурации

```bash
# Просмотр активной конфигурации
python -c "
import yaml
with open('config/default_config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
    print('Конфигурация:')
    for key, value in config.items():
        print(f'  {key}: {value}')
"
```

#### Анализ логов

```bash
# Просмотр всех логов
ls -la logs/

# Поиск ошибок
grep -i "error" logs/app.log
grep -i "exception" logs/app.log

# Просмотр последних записей
tail -20 logs/app.log
```

#### Тестирование компонентов

```bash
# Запуск unit тестов
python -m pytest tests/unit/ -v

# Запуск integration тестов
python -m pytest tests/integration/ -v

# Тестирование конкретного модуля
python -m pytest tests/unit/test_payment_matcher.py -v
```

### Получение помощи

1. **Внутренняя справка**:
   ```bash
   python main.py --help
   python run.py  # выберите пункт 1 "Показать справку"
   ```

2. **Проверка версий**:
   ```bash
   python --version
   pip list | grep -E "(openpyxl|click|pyyaml)"
   ```

3. **Создание отчета о проблеме**:
   ```bash
   # Сохранение информации о системе
   python -c "
   import sys, platform
   print(f'Python: {sys.version}')
   print(f'Платформа: {platform.platform()}')
   print(f'Архитектура: {platform.architecture()}')
   " > debug_info.txt
   
   # Добавление логов
   tail -50 logs/app.log >> debug_info.txt
   ```

## 📊 Понимание результатов

### Статусы платежей

- **Получен** - платеж найден в допустимом временном окне
- **Просрочен** - текущая дата > ожидаемая дата + 3 дня И платеж не найден
- **Ожидается** - ожидаемая дата ≤ текущая дата ≤ ожидаемая дата + 3 дня И платеж не найден
- **Срок не наступил** - текущая дата < ожидаемой даты
- **Неясно** - найдено несколько совпадающих платежей или платежи вне допустимого окна

### Примечания в отчете

- **"Платеж найден"** - платеж найден в стандартном 7-дневном окне
- **"Найден расширенным поиском"** - платеж найден при поиске по всему периоду выписки
- **"Платеж не найден"** - соответствующий платеж не обнаружен

### Расчет дней просрочки

- **Положительные значения** - количество дней просрочки
- **Отрицательные значения** - платеж внесен раньше срока
- **Ноль** - платеж внесен точно в срок

---

*Документация обновлена: Август 2025*
*Версия системы: 3.0 (Полная русификация)*