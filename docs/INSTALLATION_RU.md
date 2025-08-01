# Руководство по установке

Подробная инструкция по установке и настройке Трекера Платежей за Гаражи на различных операционных системах.

## 📋 Системные требования

### Минимальные требования

- **Операционная система**: Windows 10/11, Linux (Ubuntu 18.04+), macOS 10.14+
- **Python**: версия 3.11 или выше
- **Оперативная память**: 512 МБ свободной памяти
- **Дисковое пространство**: 100 МБ свободного места
- **Дополнительно**: Доступ к интернету для установки зависимостей

### Рекомендуемые требования

- **Python**: версия 3.11+
- **Оперативная память**: 1 ГБ или больше
- **Дисковое пространство**: 500 МБ свободного места

## 🖥️ Установка на Windows

### Шаг 1: Установка Python

#### Способ 1: Через официальный сайт (рекомендуется)

1. **Перейдите на** [python.org](https://python.org/downloads/)
2. **Скачайте** последнюю версию Python 3.11+
3. **Запустите установщик** с правами администратора
4. **Обязательно отметьте**:
   - ☑️ "Add Python to PATH"
   - ☑️ "Install for all users"
   - ☑️ "Install pip"

5. **Проверьте установку**:
   ```cmd
   python --version
   pip --version
   ```

#### Способ 2: Через Microsoft Store

1. Откройте **Microsoft Store**
2. Найдите **"Python 3.11"**
3. Нажмите **"Установить"**
4. Проверьте установку в командной строке

#### Способ 3: Через Chocolatey

```cmd
# Установите Chocolatey (если не установлен)
# Затем установите Python
choco install python311
```

### Шаг 2: Создание виртуального окружения

```cmd
# Откройте командную строку (cmd) или PowerShell
# Перейдите в папку проекта
cd C:\path\to\garage-payment-tracker

# Создайте виртуальное окружение
python -m venv garage_env

# Активируйте окружение
garage_env\Scripts\activate

# Проверьте активацию (должно появиться (garage_env) в начале строки)
```

### Шаг 3: Установка зависимостей

```cmd
# Убедитесь что окружение активировано
# Обновите pip
python -m pip install --upgrade pip

# Установите зависимости
pip install openpyxl click pyyaml pytest pytest-cov

# Или установите из requirements.txt (если есть)
pip install -r requirements.txt
```

### Шаг 4: Проверка установки

```cmd
# Проверьте работу приложения
python main.py --help

# Запустите интерактивный режим
python run.py
```

## 🐧 Установка на Linux

### Ubuntu/Debian

#### Шаг 1: Обновление системы

```bash
# Обновите списки пакетов
sudo apt update && sudo apt upgrade -y

# Установите необходимые пакеты
sudo apt install software-properties-common build-essential -y
```

#### Шаг 2: Установка Python 3.11

```bash
# Добавьте репозиторий deadsnakes (для Ubuntu < 22.04)
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Установите Python 3.11
sudo apt install python3.11 python3.11-pip python3.11-venv python3.11-dev -y

# Создайте симлинк (опционально)
sudo ln -sf /usr/bin/python3.11 /usr/bin/python

# Проверьте установку
python3.11 --version
```

#### Шаг 3: Создание виртуального окружения

```bash
# Перейдите в папку проекта
cd /path/to/garage-payment-tracker

# Создайте виртуальное окружение
python3.11 -m venv garage_env

# Активируйте окружение
source garage_env/bin/activate

# Проверьте активацию
which python
```

#### Шаг 4: Установка зависимостей

```bash
# Обновите pip
pip install --upgrade pip

# Установите зависимости
pip install openpyxl click pyyaml pytest pytest-cov

# Проверьте установку
pip list
```

### CentOS/RHEL/Rocky Linux

#### Подготовка системы

```bash
# Обновите систему
sudo yum update -y

# Установите EPEL репозиторий
sudo yum install epel-release -y

# Установите инструменты разработки
sudo yum groupinstall "Development Tools" -y
```

#### Установка Python 3.11

```bash
# Установите зависимости
sudo yum install openssl-devel bzip2-devel libffi-devel zlib-devel -y

# Скачайте и скомпилируйте Python 3.11
cd /tmp
wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz
tar xzf Python-3.11.9.tgz
cd Python-3.11.9

# Настройте и скомпилируйте
./configure --enable-optimizations --with-ensurepip=install
make altinstall

# Проверьте установку
python3.11 --version
```

### Fedora

```bash
# Установите Python 3.11
sudo dnf install python3.11 python3.11-pip python3.11-devel -y

# Остальные шаги аналогичны Ubuntu
```

### Arch Linux

```bash
# Установите Python
sudo pacman -S python python-pip

# Создайте виртуальное окружение
python -m venv garage_env
source garage_env/bin/activate
```

## 🍎 Установка на macOS

### Способ 1: Через Homebrew (рекомендуется)

```bash
# Установите Homebrew (если не установлен)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установите Python 3.11
brew install python@3.11

# Проверьте установку
python3.11 --version
```

### Способ 2: Через официальный сайт

1. Скачайте установщик с [python.org](https://python.org/downloads/macos/)
2. Запустите .pkg файл и следуйте инструкциям
3. Проверьте установку в Terminal

### Создание окружения на macOS

```bash
# Перейдите в папку проекта
cd /path/to/garage-payment-tracker

# Создайте виртуальное окружение
python3.11 -m venv garage_env

# Активируйте окружение
source garage_env/bin/activate

# Установите зависимости
pip install --upgrade pip
pip install openpyxl click pyyaml pytest pytest-cov
```

## 🛠️ Альтернативные способы установки

### Через Conda/Miniconda

```bash
# Установите Miniconda
# Затем создайте окружение
conda create -n garage_env python=3.11
conda activate garage_env

# Установите зависимости
conda install -c conda-forge openpyxl click pyyaml pytest pytest-cov
```

### Через Poetry

```bash
# Установите Poetry
curl -sSL https://install.python-poetry.org | python3 -

# В папке проекта
poetry install
poetry shell
```

### Через Docker

```dockerfile
# Создайте Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "run.py"]
```

```bash
# Сборка и запуск
docker build -t garage-tracker .
docker run -it --rm -v $(pwd)/attached_assets:/app/attached_assets -v $(pwd)/output:/app/output garage-tracker
```

## ⚙️ Настройка окружения

### Переменные окружения

#### Windows (Командная строка)

```cmd
# Установка языка по умолчанию
set GARAGE_TRACKER_LANG=ru

# Установка уровня логирования
set GARAGE_TRACKER_LOG_LEVEL=INFO

# Постоянная установка (через системные настройки)
setx GARAGE_TRACKER_LANG ru
```

#### Windows (PowerShell)

```powershell
# Установка переменных
$env:GARAGE_TRACKER_LANG = "ru"
$env:GARAGE_TRACKER_LOG_LEVEL = "INFO"

# Постоянная установка
[Environment]::SetEnvironmentVariable("GARAGE_TRACKER_LANG", "ru", "User")
```

#### Linux/macOS

```bash
# Временная установка
export GARAGE_TRACKER_LANG=ru
export GARAGE_TRACKER_LOG_LEVEL=INFO

# Постоянная установка (добавьте в ~/.bashrc или ~/.zshrc)
echo 'export GARAGE_TRACKER_LANG=ru' >> ~/.bashrc
echo 'export GARAGE_TRACKER_LOG_LEVEL=INFO' >> ~/.bashrc
source ~/.bashrc
```

### Настройка кодировки

#### Windows

```cmd
# Установка кодировки UTF-8
chcp 65001

# Постоянная установка в реестре
reg add "HKCU\Console" /v CodePage /t REG_DWORD /d 65001 /f
```

#### Linux

```bash
# Проверка текущей локали
locale

# Установка русской локали (если нужно)
sudo locale-gen ru_RU.UTF-8
export LANG=ru_RU.UTF-8
export LC_ALL=ru_RU.UTF-8
```

## 📁 Подготовка структуры проекта

### Создание необходимых папок

```bash
# Linux/macOS/Windows (в PowerShell)
mkdir -p attached_assets output logs config docs

# Windows (в cmd)
mkdir attached_assets
mkdir output
mkdir logs
mkdir config
mkdir docs
```

### Права доступа (Linux/macOS)

```bash
# Установка правильных прав
chmod 755 attached_assets output logs
chmod 644 config/*.yaml
chmod +x main.py run.py
```

## ✅ Проверка установки

### Тест основных компонентов

```bash
# Активируйте виртуальное окружение
# Затем выполните тесты

# 1. Проверка Python и зависимостей
python --version
pip list | grep -E "(openpyxl|click|pyyaml)"

# 2. Проверка основной функциональности
python main.py --help

# 3. Проверка интерактивного режима
python run.py

# 4. Запуск unit тестов
python -m pytest tests/unit/ -v

# 5. Проверка импорта модулей
python -c "
import openpyxl
import click
import yaml
print('Все модули импортированы успешно')
"
```

### Создание тестовых файлов

```bash
# Создайте простой тестовый файл
python -c "
import openpyxl
wb = openpyxl.Workbook()
ws = wb.active
ws['A1'] = 'ID'
ws['B1'] = 'Сумма'
ws['A2'] = 1
ws['B2'] = 1000
wb.save('attached_assets/test_garage.xlsx')
print('Тестовый файл создан: attached_assets/test_garage.xlsx')
"
```

## 🆘 Устранение проблем установки

### Частые ошибки и решения

#### Ошибка: "python: command not found"

**Linux/macOS:**
```bash
# Проверьте установку
which python3
ls -la /usr/bin/python*

# Создайте симлинк
sudo ln -sf /usr/bin/python3.11 /usr/bin/python
```

**Windows:**
```cmd
# Переустановите Python с опцией "Add to PATH"
# Или добавьте в PATH вручную:
set PATH=%PATH%;C:\Python311;C:\Python311\Scripts
```

#### Ошибка: "pip: command not found"

```bash
# Linux/macOS
sudo apt install python3-pip  # Ubuntu
brew install python           # macOS

# Windows
python -m ensurepip --upgrade
```

#### Ошибка: "Permission denied"

```bash
# Linux/macOS - используйте виртуальное окружение
python3 -m venv garage_env
source garage_env/bin/activate

# Или установите с --user
pip install --user openpyxl click pyyaml
```

#### Ошибка: "Microsoft Visual C++ required"

**Windows:**
1. Скачайте и установите "Microsoft C++ Build Tools"
2. Или установите Visual Studio Community с компонентами C++

#### Ошибка SSL/TLS при установке пакетов

```bash
# Обновите сертификаты
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --upgrade pip

# Или используйте другой индекс
pip install -i https://pypi.douban.com/simple/ openpyxl
```

### Диагностика проблем

```bash
# Проверка окружения
python -c "
import sys
print('Python executable:', sys.executable)
print('Python version:', sys.version)
print('Python path:', sys.path)
"

# Проверка установленных пакетов
pip list
pip show openpyxl

# Проверка виртуального окружения
which python
echo $VIRTUAL_ENV
```

### Полная переустановка

```bash
# Удаление виртуального окружения
rm -rf garage_env

# Создание нового окружения
python3.11 -m venv garage_env
source garage_env/bin/activate
pip install --upgrade pip
pip install openpyxl click pyyaml pytest pytest-cov
```

## 📝 Финальная проверка

После завершения установки выполните следующие команды:

```bash
# 1. Активируйте окружение
source garage_env/bin/activate  # Linux/macOS
# или
garage_env\Scripts\activate     # Windows

# 2. Проверьте версии
python --version
pip --version

# 3. Проверьте зависимости
pip list

# 4. Проверьте работу приложения
python main.py --help
python run.py

# 5. Запустите тесты
python -m pytest tests/ -v
```

Если все команды выполняются без ошибок, установка завершена успешно!

---

*Руководство по установке обновлено: Август 2025*
*Совместимость: Windows 10+, Linux Ubuntu 18.04+, macOS 10.14+*