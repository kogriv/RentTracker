# Устранение неполадок

Полное руководство по диагностике и решению проблем в Трекере Платежей за Гаражи.

## 🚨 Частые проблемы и решения

### Проблемы установки

#### "Python не найден" или "python: command not found"

**Симптомы:**
```bash
python --version
'python' is not recognized as an internal or external command
# или
python: command not found
```

**Решения:**

**Windows:**
```cmd
# Проверьте установку Python
where python
# Если не найден, переустановите с опцией "Add Python to PATH"

# Или добавьте в PATH вручную:
set PATH=%PATH%;C:\Python311;C:\Python311\Scripts

# Постоянное добавление в PATH:
setx PATH "%PATH%;C:\Python311;C:\Python311\Scripts"

# Альтернативно используйте python3 или py:
python3 --version
py --version
```

**Linux/macOS:**
```bash
# Проверьте доступные версии Python
ls /usr/bin/python*
which python3

# Создайте симлинк
sudo ln -sf /usr/bin/python3.11 /usr/bin/python

# Или используйте python3 напрямую
python3 --version

# Установка Python (Ubuntu/Debian)
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv

# Установка Python (macOS через Homebrew)
brew install python@3.11
```

#### "pip не найден" или "pip: command not found"

**Решения:**
```bash
# Windows
python -m ensurepip --upgrade
python -m pip --version

# Linux/macOS
sudo apt install python3-pip  # Ubuntu/Debian
python3 -m ensurepip --upgrade

# Альтернативно
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

#### "Permission denied" при установке пакетов

**Решения:**
```bash
# Используйте виртуальное окружение (рекомендуется)
python -m venv garage_env
source garage_env/bin/activate  # Linux/macOS
garage_env\Scripts\activate     # Windows

# Или установите с --user
pip install --user openpyxl click pyyaml

# Linux: если нужны права sudo
sudo pip install openpyxl click pyyaml
```

#### "Microsoft Visual C++ 14.0 is required" (Windows)

**Решения:**
1. **Скачайте и установите Microsoft C++ Build Tools**:
   - Перейдите на [visualstudio.microsoft.com](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - Скачайте "Build Tools for Visual Studio"
   - Установите с компонентами C++

2. **Альтернативно установите Visual Studio Community**:
   - Включите "Desktop development with C++"

3. **Используйте предкомпилированные пакеты**:
   ```cmd
   pip install --only-binary=all openpyxl click pyyaml
   ```

### Проблемы с зависимостями

#### "No module named 'openpyxl'" (или другой модуль)

**Диагностика:**
```bash
# Проверьте активно ли виртуальное окружение
which python
echo $VIRTUAL_ENV  # Linux/macOS
echo %VIRTUAL_ENV% # Windows

# Проверьте установленные пакеты
pip list
pip show openpyxl
```

**Решения:**
```bash
# Переустановите зависимости
pip install --upgrade openpyxl click pyyaml pytest pytest-cov

# Если проблема в окружении, пересоздайте его
deactivate
rm -rf garage_env
python -m venv garage_env
source garage_env/bin/activate
pip install openpyxl click pyyaml pytest pytest-cov

# Проверьте версии Python
python --version
pip --version
```

#### Конфликты версий пакетов

**Диагностика:**
```bash
# Проверьте зависимости
pip check

# Список всех пакетов с версиями
pip freeze
```

**Решения:**
```bash
# Обновите все пакеты
pip install --upgrade pip
pip install --upgrade openpyxl click pyyaml

# Принудительная переустановка
pip install --force-reinstall openpyxl click pyyaml

# Создание requirements.txt с фиксированными версиями
pip freeze > requirements.txt
```

### Проблемы с файлами

#### "FileNotFoundError: [Errno 2] No such file or directory"

**Проверка файлов:**
```bash
# Проверьте структуру проекта
ls -la
ls -la attached_assets/

# Проверьте текущую директорию
pwd

# Проверьте права доступа
ls -la attached_assets/*.xlsx
```

**Решения:**
```bash
# Используйте абсолютные пути
python main.py process-payments \
  --garage-file "/полный/путь/к/arenda.xlsx" \
  --statement-file "/полный/путь/к/statement.xlsx"

# Создайте недостающие папки
mkdir -p attached_assets output logs

# Скопируйте файлы в правильные папки
cp /path/to/your/files/*.xlsx attached_assets/

# Проверьте кодировку имен файлов
ls -la attached_assets/ | hexdump -C
```

#### "PermissionError: [Errno 13] Permission denied"

**Решения:**
```bash
# Linux/macOS: исправьте права доступа
chmod 644 attached_assets/*.xlsx
chmod 755 attached_assets/ output/ logs/

# Windows: запустите как администратор или проверьте антивирус

# Проверьте что файлы не открыты в Excel
lsof attached_assets/*.xlsx  # Linux/macOS
```

#### "BadZipFile: File is not a zip file" или проблемы с Excel

**Диагностика:**
```bash
# Проверьте тип файла
file attached_assets/*.xlsx

# Проверьте размер файла
ls -lh attached_assets/

# Попробуйте открыть файл вручную
python -c "
import openpyxl
try:
    wb = openpyxl.load_workbook('attached_assets/arenda.xlsx')
    print('Файл открылся успешно')
    print('Листы:', wb.sheetnames)
except Exception as e:
    print('Ошибка:', e)
"
```

**Решения:**
```bash
# Пересохраните файл в Excel как .xlsx
# Убедитесь что файл не поврежден

# Конвертируйте .xls в .xlsx
python -c "
import pandas as pd
df = pd.read_excel('old_file.xls')
df.to_excel('attached_assets/arenda.xlsx', index=False)
"

# Проверьте кодировку файла
python -c "
import openpyxl
from openpyxl import load_workbook
wb = load_workbook('attached_assets/arenda.xlsx', read_only=True)
print('Файл читается в режиме только для чтения')
"
```

### Проблемы кодировки

#### "UnicodeDecodeError" или кракозябры в выводе

**Windows:**
```cmd
# Установите кодировку UTF-8
chcp 65001

# Постоянная установка
reg add "HKCU\Console" /v CodePage /t REG_DWORD /d 65001 /f

# В PowerShell
[Console]::OutputEncoding = [Text.Encoding]::UTF8
```

**Linux:**
```bash
# Проверьте локаль
locale

# Установите русскую локаль
sudo locale-gen ru_RU.UTF-8
export LANG=ru_RU.UTF-8
export LC_ALL=ru_RU.UTF-8

# Добавьте в ~/.bashrc для постоянного эффекта
echo 'export LANG=ru_RU.UTF-8' >> ~/.bashrc
echo 'export LC_ALL=ru_RU.UTF-8' >> ~/.bashrc
```

**Проблемы с Excel файлами:**
```python
# Принудительное указание кодировки
import openpyxl
wb = openpyxl.load_workbook('file.xlsx', read_only=True, data_only=True)
```

### Проблемы выполнения

#### "ImportError" или "ModuleNotFoundError"

**Диагностика:**
```bash
# Проверьте PYTHONPATH
python -c "import sys; print('\n'.join(sys.path))"

# Проверьте структуру проекта
find . -name "*.py" | head -10
```

**Решения:**
```bash
# Запускайте из корневой папки проекта
cd /path/to/garage-payment-tracker
python main.py --help

# Добавьте src в PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Или используйте python -m
python -m src.main --help
```

#### Медленная работа или зависание

**Диагностика:**
```bash
# Проверьте использование ресурсов
top -p $(pgrep python)

# Запустите с профилированием
python -m cProfile main.py process-payments \
  --garage-file attached_assets/arenda.xlsx \
  --statement-file attached_assets/statement.xlsx

# Проверьте размер файлов
ls -lh attached_assets/
```

**Решения:**
```bash
# Увеличьте уровень логирования для диагностики
python main.py -v process-payments \
  --garage-file attached_assets/arenda.xlsx \
  --statement-file attached_assets/statement.xlsx

# Проверьте доступную память
free -h  # Linux
vm_stat # macOS

# Обработайте меньшие файлы для тестирования
```

## 🔍 Диагностические команды

### Проверка окружения

```bash
# Полная диагностика системы
python -c "
import sys, platform, os
print('=== Диагностика системы ===')
print(f'Python версия: {sys.version}')
print(f'Python путь: {sys.executable}')
print(f'Платформа: {platform.platform()}')
print(f'Архитектура: {platform.architecture()}')
print(f'Текущая директория: {os.getcwd()}')
print(f'Переменные окружения Python:')
for key in sorted(os.environ.keys()):
    if 'PYTHON' in key or 'PATH' in key:
        print(f'  {key}: {os.environ[key][:100]}...')
"

# Проверка установленных пакетов
pip list | grep -E "(openpyxl|click|pyyaml|pytest)"

# Проверка виртуального окружения
python -c "
import sys
print('В виртуальном окружении:', hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
print('Путь к executable:', sys.executable)
"
```

### Проверка функциональности

```bash
# Тест импорта всех модулей
python -c "
modules = ['openpyxl', 'click', 'yaml', 'pathlib', 'datetime']
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}: OK')
    except ImportError as e:
        print(f'❌ {module}: {e}')
"

# Тест основных компонентов приложения
python -c "
import sys
sys.path.append('src')
components = [
    'core.models.garage',
    'core.models.payment', 
    'core.services.payment_matcher',
    'parsers.garage_parser',
    'infrastructure.localization.i18n'
]
for component in components:
    try:
        __import__(component)
        print(f'✅ {component}: OK')
    except ImportError as e:
        print(f'❌ {component}: {e}')
"

# Проверка файловой системы
python -c "
import os
folders = ['attached_assets', 'output', 'logs', 'config', 'src']
for folder in folders:
    exists = os.path.exists(folder)
    readable = os.access(folder, os.R_OK) if exists else False
    writable = os.access(folder, os.W_OK) if exists else False
    print(f'{folder}: существует={exists}, чтение={readable}, запись={writable}')
"
```

### Проверка данных

```bash
# Валидация Excel файлов
python -c "
import openpyxl
import os

files_to_check = []
for root, dirs, files in os.walk('attached_assets'):
    for file in files:
        if file.endswith(('.xlsx', '.xls')):
            files_to_check.append(os.path.join(root, file))

for file_path in files_to_check:
    try:
        wb = openpyxl.load_workbook(file_path, read_only=True)
        ws = wb.active
        print(f'✅ {file_path}: {ws.max_row} строк, {ws.max_column} колонок')
    except Exception as e:
        print(f'❌ {file_path}: {e}')
"

# Проверка конфигурации
python -c "
import yaml
import os

config_files = ['config/default_config.yaml']
for config_file in config_files:
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            print(f'✅ {config_file}: конфигурация загружена')
            for section, values in config.items():
                print(f'  {section}: {len(values)} параметров')
        except Exception as e:
            print(f'❌ {config_file}: {e}')
    else:
        print(f'⚠️  {config_file}: файл не найден')
"
```

## 🔧 Восстановление после ошибок

### Полная переустановка

```bash
# 1. Деактивируйте и удалите окружение
deactivate
rm -rf garage_env

# 2. Создайте новое окружение
python3.11 -m venv garage_env
source garage_env/bin/activate

# 3. Обновите pip
python -m pip install --upgrade pip

# 4. Установите зависимости
pip install openpyxl click pyyaml pytest pytest-cov

# 5. Проверьте установку
python main.py --help
```

### Сброс конфигурации

```bash
# Сохраните текущую конфигурацию
cp config/default_config.yaml config/backup_config.yaml

# Восстановите конфигурацию по умолчанию
git checkout config/default_config.yaml

# Или создайте минимальную конфигурацию
cat > config/default_config.yaml << 'EOF'
localization:
  default_language: "ru"
  fallback_language: "en"

payment_matching:
  search_window_days: 7
  grace_period_days: 3

parsing:
  search_window_days: 7
  grace_period_days: 3
EOF
```

### Очистка данных

```bash
# Очистите выходные файлы
rm -f output/*.xlsx

# Очистите логи
rm -f logs/*.log

# Создайте пустые папки заново
mkdir -p attached_assets output logs config
```

## 📊 Мониторинг и предотвращение проблем

### Регулярные проверки

Создайте скрипт для ежедневной проверки:

```bash
#!/bin/bash
# health_check.sh

echo "=== Проверка здоровья системы $(date) ==="

# Проверка Python
python --version > /dev/null 2>&1 && echo "✅ Python: OK" || echo "❌ Python: FAILED"

# Проверка зависимостей
python -c "import openpyxl, click, yaml" > /dev/null 2>&1 && echo "✅ Зависимости: OK" || echo "❌ Зависимости: FAILED"

# Проверка файлов
[ -d "attached_assets" ] && echo "✅ Папка attached_assets: OK" || echo "❌ Папка attached_assets: MISSING"
[ -d "output" ] && echo "✅ Папка output: OK" || echo "❌ Папка output: MISSING"

# Проверка места на диске
DISK_USAGE=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 90 ]; then
    echo "✅ Диск: ${DISK_USAGE}% использовано"
else
    echo "⚠️  Диск: ${DISK_USAGE}% использовано (мало места)"
fi

# Проверка логов на ошибки
ERROR_COUNT=$(grep -c "ERROR" logs/app.log 2>/dev/null || echo "0")
if [ $ERROR_COUNT -eq 0 ]; then
    echo "✅ Логи: нет ошибок"
else
    echo "⚠️  Логи: $ERROR_COUNT ошибок найдено"
fi

echo "=== Проверка завершена ==="
```

### Автоматическое архивирование

```bash
#!/bin/bash
# archive_old_files.sh

# Архивирование старых отчетов (> 30 дней)
find output/ -name "*.xlsx" -mtime +30 -exec mv {} archive/ \;

# Сжатие старых логов (> 7 дней)
find logs/ -name "*.log" -mtime +7 -exec gzip {} \;

# Удаление старых архивов (> 90 дней)
find archive/ -name "*.xlsx" -mtime +90 -delete

echo "Архивирование завершено: $(date)"
```

### Мониторинг производительности

```bash
# performance_monitor.sh
#!/bin/bash

# Мониторинг времени выполнения
START_TIME=$(date +%s)

python main.py process-payments \
  --garage-file attached_assets/arenda.xlsx \
  --statement-file attached_assets/statement.xlsx \
  --output output/performance_test.xlsx

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "Время выполнения: ${DURATION} секунд" >> logs/performance.log

# Проверка на аномалии
if [ $DURATION -gt 60 ]; then
    echo "⚠️  ПРЕДУПРЕЖДЕНИЕ: Обработка заняла ${DURATION} секунд (норма < 60)" >> logs/performance.log
fi
```

## 📞 Получение помощи

### Сбор информации для поддержки

При обращении за помощью соберите следующую информацию:

```bash
# Создание отчета о проблеме
cat > problem_report.txt << EOF
=== Отчет о проблеме ===
Дата: $(date)

Операционная система: $(uname -a 2>/dev/null || systeminfo | findstr /B "OS Name OS Version" 2>/dev/null)
Python версия: $(python --version 2>&1)
Pip версия: $(pip --version 2>&1)

Установленные пакеты:
$(pip list 2>&1 | grep -E "(openpyxl|click|pyyaml)")

Структура проекта:
$(ls -la 2>&1)

Последние логи:
$(tail -20 logs/app.log 2>&1 || echo "Логи недоступны")

Последние ошибки:
$(grep -i "error" logs/app.log 2>&1 | tail -5 || echo "Ошибок не найдено")

EOF

echo "Отчет создан: problem_report.txt"
```

### Контрольный список для диагностики

Перед обращением за помощью проверьте:

- [ ] Python установлен и доступен (`python --version`)
- [ ] Виртуальное окружение активировано
- [ ] Все зависимости установлены (`pip list`)
- [ ] Файлы находятся в правильных папках
- [ ] Файлы имеют правильные права доступа
- [ ] Достаточно места на диске
- [ ] Проверены логи на предмет ошибок
- [ ] Протестированы простые команды (`python main.py --help`)

### Ресурсы для самостоятельного решения

1. **Документация проекта**: `docs/` папка
2. **Внутренняя справка**: `python main.py --help`
3. **Интерактивная помощь**: `python run.py` → пункт 1
4. **Логи приложения**: `logs/app.log`
5. **Конфигурация**: `config/default_config.yaml`

---

*Руководство по устранению неполадок обновлено: Август 2025*
*Поддерживаемые платформы: Windows 10+, Linux Ubuntu 18.04+, macOS 10.14+*