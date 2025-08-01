# Исправление ошибки "Процесс не может получить доступ к файлу" в веб-интерфейсе

## 🐛 Проблема

Ошибка: `[WinError 32] Процесс не может получить доступ к файлу, так как этот файл занят другим процессом: 'uploads\\statement_20250801_194641_print.xlsx'`

## 🔍 Причина

Проблема возникала из-за того, что файлы Excel оставались открытыми в памяти после обработки, и система не могла их удалить.

## ✅ Исправления

### 1. Улучшенное управление файлами в парсерах

**Файлы:**
- `src/parsers/file_parsers/excel_parser.py`
- `src/parsers/file_parsers/sberbank_parser.py`

**Изменения:**
- Добавлены `finally` блоки для гарантированного закрытия файлов
- Улучшена обработка исключений при закрытии файлов

```python
workbook = None
try:
    workbook = load_workbook(source, read_only=True, data_only=True)
    # ... обработка файла
finally:
    if workbook:
        try:
            workbook.close()
        except Exception as e:
            self.logger.warning(f"Error closing workbook: {e}")
```

### 2. Улучшенная очистка файлов в веб-интерфейсе

**Файл:** `src/interfaces/web/app.py`

**Изменения:**
- Добавлена задержка перед удалением файлов
- Реализована система повторных попыток удаления
- Добавлена автоматическая очистка старых файлов при запуске

```python
# Add a small delay to ensure files are fully closed
time.sleep(0.5)

# Try to delete files with retries
for file_path in [garage_path, statement_path]:
    if file_path.exists():
        for attempt in range(3):  # Try up to 3 times
            try:
                file_path.unlink()
                break
            except PermissionError as e:
                if attempt < 2:
                    time.sleep(1)  # Wait before retry
```

### 3. Новые методы в ExcelReader

**Файл:** `src/infrastructure/file_handlers/excel_reader.py`

**Добавлены методы:**
- `read_workbook_safe()` - безопасное чтение с гарантированной очисткой
- `read_file_data_safe()` - чтение данных с автоматическим закрытием файла

### 4. Автоматическая очистка старых файлов

**Функция:** `_cleanup_old_files()`

- Удаляет файлы старше 1 часа при запуске веб-приложения
- Логирует процесс очистки

## 🧪 Тестирование

Создан тестовый скрипт `test_web_fix.py` для проверки исправлений:

```bash
python test_web_fix.py
```

## 📋 Результат

После внесения исправлений:

✅ **Файлы корректно закрываются** после обработки  
✅ **Система повторных попыток** для удаления файлов  
✅ **Автоматическая очистка** старых файлов  
✅ **Улучшенное логирование** ошибок  
✅ **Задержки** для освобождения файлов  

## 🚀 Использование

Веб-интерфейс теперь должен работать без ошибок доступа к файлам:

1. Запустите веб-сервер: `python web_app.py`
2. Загрузите файлы через веб-интерфейс
3. Файлы будут автоматически обработаны и удалены

## 📝 Логи

Проверьте логи в `logs/app.log` для диагностики:

```bash
tail -f logs/app.log
```

Ищите сообщения:
- `"Successfully deleted"`
- `"Cleaned up old file"`
- `"Error closing workbook"`

---

*Исправления внесены: Август 2025*
*Версия: 3.1.1* 