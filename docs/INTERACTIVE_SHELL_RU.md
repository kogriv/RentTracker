# Интерактивная оболочка - Подробное руководство

Полное руководство по использованию встроенной интерактивной оболочки Трекера Платежей за Гаражи.

## 🎯 Что такое интерактивная оболочка?

Интерактивная оболочка - это встроенная командная строка, доступная через пункт 5 главного меню. Она позволяет выполнять системные команды, команды приложения и диагностические операции без выхода из программы.

### Основные преимущества

✅ **Удобство** - не нужно переключаться между окнами  
✅ **Контекст** - работа в правильной директории с активированным окружением  
✅ **Диагностика** - быстрый доступ к логам и состоянию системы  
✅ **Обучение** - изучение возможностей через интерактивные команды  
✅ **Отладка** - тестирование различных параметров и сценариев  

## 🚀 Запуск интерактивной оболочки

### Через главное меню

1. Запустите приложение:
   ```bash
   python run.py
   ```

2. Выберите язык (2 для русского)

3. В главном меню выберите:
   ```
   5. Интерактивная оболочка (примеры: 'ls output/', 'python main.py --help')
   ```

4. Появится приглашение командной строки:
   ```bash
   >>> 
   ```

### Прямой запуск (альтернативный способ)

```bash
# Активируйте виртуальное окружение
source garage_env/bin/activate  # Linux/macOS
garage_env\Scripts\activate     # Windows

# Перейдите в директорию проекта
cd /path/to/garage-payment-tracker

# Запустите Python в интерактивном режиме
python
```

## 📁 Навигация и файловые операции

### Просмотр структуры проекта

```bash
# Просмотр текущей директории
>>> ls
attached_assets/  config/  docs/  logs/  output/  src/  tests/  main.py  run.py

# Подробный список с размерами и датами
>>> ls -la
total 156
drwxr-xr-x  8 user user  4096 Aug  1 12:00 .
drwxr-xr-x  3 user user  4096 Aug  1 11:30 ..
drwxr-xr-x  2 user user  4096 Aug  1 11:45 attached_assets
drwxr-xr-x  2 user user  4096 Aug  1 11:30 config
drwxr-xr-x  2 user user  4096 Aug  1 12:00 docs
drwxr-xr-x  2 user user  4096 Aug  1 11:50 logs
drwxr-xr-x  2 user user  4096 Aug  1 11:55 output
-rw-r--r--  1 user user  2156 Aug  1 11:30 main.py
-rw-r--r--  1 user user  4832 Aug  1 11:40 run.py

# Просмотр содержимого конкретных папок
>>> ls attached_assets/
arenda_1754033731239.xlsx  print_2_1754033731239.xlsx

>>> ls output/
payment_report_20250801_113528.xlsx
russian_test_report.xlsx
report_2025-08-01_11-36-31.xlsx

>>> ls logs/
app.log  error.log
```

### Анализ файлов

```bash
# Информация о типе файла
>>> file attached_assets/*.xlsx
attached_assets/arenda_1754033731239.xlsx: Microsoft Excel 2007+
attached_assets/print_2_1754033731239.xlsx: Microsoft Excel 2007+

# Размер файлов
>>> ls -lh attached_assets/
total 64K
-rw-r--r-- 1 user user 31K Aug  1 09:30 arenda_1754033731239.xlsx
-rw-r--r-- 1 user user 29K Aug  1 09:30 print_2_1754033731239.xlsx

# Дата создания файлов
>>> stat attached_assets/arenda_1754033731239.xlsx
  File: attached_assets/arenda_1754033731239.xlsx
  Size: 31744     Blocks: 64         IO Block: 4096   regular file
Access: 2025-08-01 09:30:15.123456789 +0000
Modify: 2025-08-01 09:30:15.123456789 +0000
Change: 2025-08-01 09:30:15.123456789 +0000
```

### Работа с отчетами

```bash
# Список отчетов по дате создания (новые сначала)
>>> ls -t output/
russian_test_report.xlsx
report_2025-08-01_11-36-31.xlsx
payment_report_20250801_113528.xlsx

# Поиск отчетов за конкретную дату
>>> ls output/*2025-08-01*
output/report_2025-08-01_11-36-31.xlsx

# Подсчет количества отчетов
>>> ls output/*.xlsx | wc -l
3

# Общий размер всех отчетов
>>> du -sh output/
156K    output/
```

## 🛠️ Команды приложения

### Справочная система

```bash
# Общая справка
>>> python main.py --help
Usage: main.py [OPTIONS] COMMAND [ARGS]...

  Garage Payment Tracker - Track rental payments and generate reports

Options:
  --verbose, -v       Enable verbose logging
  --lang, --language  Interface language (en=English, ru=Russian)
  --help              Show this message and exit.

Commands:
  process-payments  Process garage payments and generate report

# Справка по конкретной команде
>>> python main.py process-payments --help
Usage: main.py process-payments [OPTIONS]

  Process garage payments and generate report

Options:
  --garage-file PATH              Path to garage registry Excel file
  --statement-file PATH           Path to bank statement Excel file
  --output, -o PATH              Output file path for report
  --analysis-date [%Y-%m-%d]     Analysis date (default: today)
  --help                         Show this message and exit.
```

### Тестирование команд

```bash
# Базовая обработка
>>> python main.py --lang ru process-payments \
    --garage-file attached_assets/arenda_1754033731239.xlsx \
    --statement-file "attached_assets/print 2_1754033731239.xlsx" \
    --output output/test_report.xlsx
Обработка платежей...
Обработка завершена успешно
Отчет создан: output/test_report.xlsx

# Тест с разными датами анализа
>>> python main.py --lang ru process-payments \
    --garage-file attached_assets/arenda_1754033731239.xlsx \
    --statement-file "attached_assets/print 2_1754033731239.xlsx" \
    --analysis-date 2025-05-15 \
    --output output/early_analysis.xlsx

>>> python main.py --lang ru process-payments \
    --garage-file attached_assets/arenda_1754033731239.xlsx \
    --statement-file "attached_assets/print 2_1754033731239.xlsx" \
    --analysis-date 2025-06-01 \
    --output output/late_analysis.xlsx

# Сравнение результатов
>>> ls -la output/*analysis*
-rw-r--r-- 1 user user 7112 Aug  1 12:15 output/early_analysis.xlsx
-rw-r--r-- 1 user user 7324 Aug  1 12:16 output/late_analysis.xlsx
```

### Проверка версий и конфигурации

```bash
# Версия Python и установленные пакеты
>>> python --version
Python 3.11.9

>>> pip list | grep -E "(openpyxl|click|pyyaml)"
click              8.1.7
openpyxl           3.1.5
PyYAML             6.0.1

# Просмотр конфигурации
>>> python -c "
import yaml
with open('config/default_config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
    print('Конфигурация приложения:')
    for section, values in config.items():
        print(f'  {section}:')
        for key, value in values.items():
            print(f'    {key}: {value}')
"
```

## 📊 Диагностика и мониторинг

### Анализ логов

```bash
# Просмотр последних записей в логе
>>> tail -10 logs/app.log
2025-08-01 12:15:23,456 - src.application.use_cases.process_payments - INFO - Starting payment processing
2025-08-01 12:15:23,567 - src.parsers.garage_parser - INFO - Parsed 15 garages from registry
2025-08-01 12:15:23,678 - src.parsers.sberbank_parser - INFO - Parsed 66 transactions from statement
2025-08-01 12:15:23,789 - src.core.services.payment_matcher - INFO - Processing payments for analysis date 2025-05-15
2025-08-01 12:15:23,890 - src.core.services.payment_matcher - INFO - Payment matching completed: 7 matched, 8 unmatched

# Поиск ошибок и предупреждений
>>> grep -i "error" logs/app.log
>>> grep -i "warning" logs/app.log
2025-08-01 12:15:23,345 - src.core.services.payment_matcher - WARNING - Duplicate rental amount 3500: garages 6, 13

# Подсчет количества обработанных файлов
>>> grep "Starting payment processing" logs/app.log | wc -l
5

# Анализ производительности
>>> grep "completed in" logs/app.log
2025-08-01 12:15:24,123 - src.application.use_cases.process_payments - INFO - Payment processing completed in 0.67 seconds
```

### Мониторинг ресурсов

```bash
# Использование диска
>>> df -h .
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        50G   15G   33G  32% /

# Размер проекта
>>> du -sh .
45M     .

# Размер по папкам
>>> du -sh */
156K    attached_assets/
8.0K    config/
24K     docs/
64K     logs/
156K    output/
2.1M    src/
456K    tests/

# Свободное место для отчетов
>>> df -h output/
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        50G   15G   33G  32% /
```

### Анализ производительности

```bash
# Время выполнения команды
>>> time python main.py --lang ru process-payments \
    --garage-file attached_assets/arenda_1754033731239.xlsx \
    --statement-file "attached_assets/print 2_1754033731239.xlsx"

real    0m2.345s
user    0m1.876s
sys     0m0.234s

# Профилирование Python кода
>>> python -m cProfile -s cumulative main.py process-payments \
    --garage-file attached_assets/arenda_1754033731239.xlsx \
    --statement-file "attached_assets/print 2_1754033731239.xlsx" 2>&1 | head -20
```

## 🧪 Тестирование и отладка

### Запуск тестов

```bash
# Все тесты
>>> python -m pytest tests/ -v
========================= test session starts =========================
collected 28 items

tests/unit/core/test_garage.py::TestGarage::test_creation PASSED    [ 3%]
tests/unit/core/test_payment.py::TestPayment::test_creation PASSED  [ 7%]
...
========================= 28 passed in 2.45s =========================

# Только unit тесты
>>> python -m pytest tests/unit/ -v

# Тесты с покрытием кода
>>> python -m pytest tests/ --cov=src --cov-report=term-missing
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/core/models/garage.py                  45      2    96%   78-79
src/core/models/payment.py                 52      3    94%   89-91
...
TOTAL                                    1234     45    96%

# Конкретный тест
>>> python -m pytest tests/unit/infrastructure/test_localization.py -v
========================= test session starts =========================
collected 12 items

tests/unit/infrastructure/test_localization.py::TestLocalizationManager::test_init_with_russian PASSED [8%]
...
========================= 12 passed in 0.15s =========================
```

### Интерактивное тестирование Python

```bash
# Запуск Python REPL с загруженными модулями
>>> python -c "
import sys
sys.path.append('src')
from core.models.garage import Garage
from core.models.payment import Payment
from datetime import date

# Создание тестового гаража
garage = Garage(id=1, monthly_rent=5000, start_date=date(2024,1,1), payment_day=1)
print('Тестовый гараж:', garage)

# Создание тестового платежа
payment = Payment(
    garage_id=1, 
    expected_amount=5000, 
    expected_date=date(2025,5,1),
    status='PENDING'
)
print('Тестовый платеж:', payment)
"

# Интерактивная работа с модулями
>>> python
Python 3.11.9 (main, Jul  8 2025, 12:34:56) [GCC 9.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import sys
>>> sys.path.append('src')
>>> from core.services.payment_matcher import PaymentMatcher
>>> from infrastructure.localization.i18n import LocalizationManager
>>> 
>>> # Создание сервисов
>>> i18n = LocalizationManager('ru')
>>> matcher = PaymentMatcher(search_window_days=7, grace_period_days=3, i18n=i18n)
>>> print("Сервисы созданы успешно")
>>> exit()
```

### Отладка конкретных модулей

```bash
# Тестирование парсера гаражей
>>> python -c "
import sys
sys.path.append('src')
from parsers.garage_parser import GarageRegistryParser

parser = GarageRegistryParser()
garages = parser.parse('attached_assets/arenda_1754033731239.xlsx')
print(f'Найдено гаражей: {len(garages)}')
for garage in garages[:3]:
    print(f'  Гараж {garage.id}: {garage.monthly_rent} руб., дата начала: {garage.start_date}')
"

# Тестирование парсера выписки
>>> python -c "
import sys
sys.path.append('src')
from parsers.sberbank_parser import SberbankStatementParser

parser = SberbankStatementParser()
transactions = parser.parse('attached_assets/print 2_1754033731239.xlsx')
print(f'Найдено транзакций: {len(transactions)}')
for transaction in transactions[:3]:
    print(f'  {transaction.date}: {transaction.amount} руб. - {transaction.description[:50]}...')
"

# Тестирование локализации
>>> python -c "
import sys
sys.path.append('src')
from infrastructure.localization.i18n import LocalizationManager

i18n = LocalizationManager('ru')
print('Тестовые сообщения:')
print(f'  Статус получен: {i18n.get(\"status.received\")}')
print(f'  Платеж найден: {i18n.get(\"notes.payment_found\")}')
print(f'  Сводка: {i18n.get(\"summary.total_garages\", count=15)}')
"
```

## 📈 Анализ данных

### Изучение Excel файлов

```bash
# Анализ структуры справочника гаражей
>>> python -c "
import openpyxl
wb = openpyxl.load_workbook('attached_assets/arenda_1754033731239.xlsx')
ws = wb.active
print('Структура справочника гаражей:')
print('Заголовки:', [cell.value for cell in ws[1]])
print('Количество строк:', ws.max_row)
print('Количество колонок:', ws.max_column)
print('Первые 3 записи:')
for row in range(2, 5):
    values = [ws.cell(row=row, column=col).value for col in range(1, ws.max_column+1)]
    print(f'  Строка {row}: {values}')
"

# Анализ банковской выписки
>>> python -c "
import openpyxl
wb = openpyxl.load_workbook('attached_assets/print 2_1754033731239.xlsx')
ws = wb.active
print('Структура банковской выписки:')
print('Заголовки:', [cell.value for cell in ws[1]])
print('Количество транзакций:', ws.max_row - 1)

# Поиск информации о периоде
for row in range(1, min(20, ws.max_row)):
    for col in range(1, ws.max_column+1):
        cell_value = ws.cell(row=row, column=col).value
        if cell_value and 'операциям с' in str(cell_value):
            print(f'Найден период: {cell_value}')
"

# Анализ созданного отчета
>>> python -c "
import openpyxl
wb = openpyxl.load_workbook('output/russian_test_report.xlsx')
ws = wb.active
print('Структура отчета:')
print('Метаданные:')
for row in range(1, 5):
    col1 = ws.cell(row=row, column=1).value
    col2 = ws.cell(row=row, column=2).value
    if col1: print(f'  {col1}: {col2}')

print('Статистика по статусам:')
statuses = {}
for row in range(5, ws.max_row+1):
    status = ws.cell(row=row, column=5).value  # колонка Статус
    if status:
        statuses[status] = statuses.get(status, 0) + 1
for status, count in statuses.items():
    print(f'  {status}: {count}')
"
```

### Статистический анализ

```bash
# Подсчет статистики по отчетам
>>> python -c "
import os
from datetime import datetime

reports = [f for f in os.listdir('output') if f.endswith('.xlsx')]
print(f'Всего отчетов: {len(reports)}')

# Анализ по дате создания
report_dates = []
for report in reports:
    filepath = os.path.join('output', report)
    mtime = os.path.getmtime(filepath)
    date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
    report_dates.append(date_str)
    
from collections import Counter
date_counts = Counter(report_dates)
print('Отчеты по датам:')
for date, count in sorted(date_counts.items()):
    print(f'  {date}: {count} отчетов')
"

# Анализ размеров файлов
>>> python -c "
import os
total_size = 0
for file in os.listdir('output'):
    if file.endswith('.xlsx'):
        filepath = os.path.join('output', file)
        size = os.path.getsize(filepath)
        total_size += size
        print(f'{file}: {size/1024:.1f} KB')
print(f'Общий размер: {total_size/1024:.1f} KB')
"
```

## 🔧 Утилиты и автоматизация

### Создание скриптов автоматизации

```bash
# Создание скрипта для ежедневной обработки
>>> cat > daily_process.sh << 'EOF'
#!/bin/bash
# Ежедневная обработка платежей

DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=== Ежедневная обработка $DATE ==="

# Обработка с текущей датой
python main.py --lang ru process-payments \
  --garage-file attached_assets/arenda_1754033731239.xlsx \
  --statement-file "attached_assets/print 2_1754033731239.xlsx" \
  --analysis-date $DATE \
  --output "output/daily_${TIMESTAMP}.xlsx"

echo "Отчет создан: output/daily_${TIMESTAMP}.xlsx"

# Показать краткую статистику
echo "=== Статистика файлов ==="
ls -lh output/daily_*.xlsx | tail -5
EOF

>>> chmod +x daily_process.sh
>>> ls -la daily_process.sh
-rwxr-xr-x 1 user user 678 Aug  1 12:30 daily_process.sh
```

### Очистка и архивирование

```bash
# Создание архива старых отчетов
>>> mkdir -p archive/$(date +%Y-%m)
>>> mv output/*$(date -d "last month" +%Y-%m)* archive/$(date +%Y-%m)/ 2>/dev/null || echo "Нет файлов для архивирования"

# Очистка старых логов
>>> find logs/ -name "*.log" -mtime +30 -exec gzip {} \;
>>> ls -la logs/
total 128
-rw-r--r-- 1 user user  45234 Aug  1 12:30 app.log
-rw-r--r-- 1 user user   2567 Jul 25 10:15 app.log.gz
-rw-r--r-- 1 user user   1234 Aug  1 12:30 error.log

# Мониторинг использования диска
>>> echo "=== Использование диска ==="
>>> du -sh * | sort -hr
2.1M    src
456K    tests
156K    output
156K    attached_assets
64K     logs
24K     docs
8.0K    config
```

### Создание отчетов о работе

```bash
# Генерация сводного отчета
>>> python -c "
import os
from datetime import datetime, timedelta

print('=== Сводный отчет работы системы ===')
print(f'Дата: {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}')
print()

# Статистика файлов
print('Файлы в системе:')
for folder in ['attached_assets', 'output', 'logs']:
    if os.path.exists(folder):
        files = os.listdir(folder)
        size = sum(os.path.getsize(os.path.join(folder, f)) for f in files if os.path.isfile(os.path.join(folder, f)))
        print(f'  {folder}: {len(files)} файлов, {size/1024:.1f} KB')

# Анализ логов
if os.path.exists('logs/app.log'):
    with open('logs/app.log', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    today = datetime.now().strftime('%Y-%m-%d')
    today_lines = [l for l in lines if today in l]
    
    print(f'\\nЛоги за сегодня: {len(today_lines)} записей')
    
    errors = [l for l in today_lines if 'ERROR' in l]
    warnings = [l for l in today_lines if 'WARNING' in l]
    
    print(f'  Ошибки: {len(errors)}')
    print(f'  Предупреждения: {len(warnings)}')
    
    if warnings:
        print('  Последние предупреждения:')
        for warning in warnings[-3:]:
            print(f'    {warning.strip()}')
"
```

## 🚪 Выход из интерактивной оболочки

### Способы выхода

```bash
# Команда exit
>>> exit

# Команда quit
>>> quit()

# Сочетание клавиш Ctrl+C
>>> ^C

# Сочетание клавиш Ctrl+D (Linux/macOS)
>>> ^D

# Команда для возврата в главное меню (если запущено через run.py)
>>> menu
```

### Сохранение истории команд

```bash
# Просмотр истории команд (Linux/macOS)
>>> history | tail -10

# Сохранение полезных команд в файл
>>> cat > useful_commands.txt << 'EOF'
# Полезные команды для интерактивной оболочки

# Проверка статуса файлов
ls -la attached_assets/
ls -t output/ | head -5

# Быстрая обработка
python main.py --lang ru process-payments \
  --garage-file attached_assets/arenda_1754033731239.xlsx \
  --statement-file "attached_assets/print 2_1754033731239.xlsx"

# Анализ логов
tail -20 logs/app.log
grep "WARNING" logs/app.log | tail -5

# Тестирование
python -m pytest tests/unit/ -v

# Диагностика
python --version
pip list | grep -E "(openpyxl|click|pyyaml)"
du -sh output/
EOF
```

## 💡 Практические сценарии использования

### Сценарий 1: Ежедневная проверка

```bash
>>> # Утренняя проверка системы
>>> echo "=== Утренняя проверка $(date) ==="
>>> 
>>> # Проверка новых файлов
>>> ls -lt attached_assets/ | head -3
>>> 
>>> # Проверка места на диске
>>> df -h . | tail -1
>>> 
>>> # Последние логи
>>> tail -5 logs/app.log
>>> 
>>> # Быстрый тест
>>> python main.py --help > /dev/null && echo "✅ Приложение работает" || echo "❌ Проблема с приложением"
```

### Сценарий 2: Месячная отчетность

```bash
>>> # Создание месячного отчета
>>> MONTH=$(date +%Y-%m)
>>> echo "=== Месячная отчетность за $MONTH ==="
>>> 
>>> # Обработка с последним днем месяца
>>> LAST_DAY=$(date -d "$(date +%Y-%m-01) +1 month -1 day" +%Y-%m-%d)
>>> echo "Дата анализа: $LAST_DAY"
>>> 
>>> python main.py --lang ru process-payments \
    --garage-file attached_assets/arenda_1754033731239.xlsx \
    --statement-file "attached_assets/print 2_1754033731239.xlsx" \
    --analysis-date $LAST_DAY \
    --output "output/monthly_${MONTH}.xlsx"
>>> 
>>> # Создание архива
>>> mkdir -p archive/$MONTH
>>> cp output/monthly_${MONTH}.xlsx archive/$MONTH/
>>> echo "Архив создан: archive/$MONTH/"
```

### Сценарий 3: Анализ проблем

```bash
>>> # Диагностика проблем
>>> echo "=== Диагностика системы ==="
>>> 
>>> # Проверка ошибок в логах
>>> echo "Ошибки за последние 24 часа:"
>>> grep "ERROR" logs/app.log | tail -10
>>> 
>>> # Проверка предупреждений
>>> echo "Предупреждения:"
>>> grep "WARNING" logs/app.log | tail -5
>>> 
>>> # Проверка целостности данных
>>> python -c "
import sys
sys.path.append('src')
try:
    from parsers.garage_parser import GarageRegistryParser
    parser = GarageRegistryParser()
    garages = parser.parse('attached_assets/arenda_1754033731239.xlsx')
    print(f'✅ Справочник гаражей: {len(garages)} записей')
except Exception as e:
    print(f'❌ Ошибка в справочнике: {e}')

try:
    from parsers.sberbank_parser import SberbankStatementParser
    parser = SberbankStatementParser()
    transactions = parser.parse('attached_assets/print 2_1754033731239.xlsx')
    print(f'✅ Банковская выписка: {len(transactions)} транзакций')
except Exception as e:
    print(f'❌ Ошибка в выписке: {e}')
"
```

---

*Руководство по интерактивной оболочке обновлено: Август 2025*
*Версия системы: 3.0 (Полная русификация)*