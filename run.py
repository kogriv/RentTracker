#!/usr/bin/env python3
"""
Interactive wrapper for Garage Payment Tracker CLI
"""

import os
import sys
from pathlib import Path
from datetime import date

def main():
    """Interactive CLI wrapper"""
    print("=== Garage Payment Tracker ===")
    print("CLI Interface for processing garage rental payments")
    print()
    
    # Language selection
    while True:
        print("Select language / Выберите язык:")
        print("1. English")
        print("2. Русский")
        print()
        
        lang_choice = input("Enter your choice (1-2): ").strip()
        
        if lang_choice == '1':
            language = 'en'
            break
        elif lang_choice == '2':
            language = 'ru'
            break
        else:
            print("Invalid choice. Please enter 1 or 2.\n")
    
    print()
    if language == 'ru':
        print("📁 Расположение файлов:")
        print("   • Входные файлы: папка attached_assets/") 
        print("   • Отчеты: папка output/")
        print("   • Текущая директория:", os.getcwd())
    else:
        print("📁 File Locations:")
        print("   • Input files: attached_assets/ folder") 
        print("   • Output reports: output/ folder")
        print("   • Current directory:", os.getcwd())
    print()
    
    # Check if files exist
    garage_files = list(Path("attached_assets").glob("arenda*.xlsx"))
    statement_files = list(Path("attached_assets").glob("print*.xlsx"))
    
    if garage_files:
        if language == 'ru':
            print(f"✅ Найден файл справочника: {garage_files[0]}")
        else:
            print(f"✅ Found garage file: {garage_files[0]}")
        garage_file = garage_files[0]
    else:
        if language == 'ru':
            print("❌ Файлы справочника гаражей не найдены в папке attached_assets/")
        else:
            print("❌ No garage registry files found in attached_assets/")
        return
        
    if statement_files:
        if language == 'ru':
            print(f"✅ Найден файл выписки: {statement_files[0]}")
        else:
            print(f"✅ Found statement file: {statement_files[0]}")
        statement_file = statement_files[0]
    else:
        if language == 'ru':
            print("❌ Файлы банковских выписок не найдены в папке attached_assets/")
        else:
            print("❌ No bank statement files found in attached_assets/")
        return
    
    # Auto-detect payment period from statement
    detected_period = None
    try:
        import sys
        sys.path.insert(0, 'src')
        
        # Initialize silent logging for period detection
        from src.utils.logging_config import setup_logging
        setup_logging(
            log_level="INFO",
            log_file=Path("logs/app.log"),
            console_level="ERROR"  # Only errors in console
        )
        
        from src.parsers.file_parsers.sberbank_parser import SberbankStatementParser
        parser = SberbankStatementParser()
        detected_period = parser.extract_payment_period(statement_file)
        if detected_period:
            if language == 'ru':
                print(f"📅 Обнаружен период платежей: {detected_period.start_date} до {detected_period.end_date}")
                print(f"🗓️  Рекомендуемый месяц анализа: {detected_period.start_date.strftime('%B %Y')}")
            else:
                print(f"📅 Detected payment period: {detected_period.start_date} to {detected_period.end_date}")
                print(f"🗓️  Recommended analysis month: {detected_period.start_date.strftime('%B %Y')}")
    except Exception:
        pass  # Silently ignore detection errors
    
    print()
    if language == 'ru':
        print("Доступные команды:")
        print("1. Показать справку")
        print("2. Показать версию")
        
        # Add detailed descriptions with detected period info
        if detected_period:
            end_date = detected_period.end_date.strftime('%d-%m-%Y')
            start_date = detected_period.start_date.strftime('%d-%m-%Y')
            print(f"3. Обработать платежи (дата анализа по умолчанию: {end_date})")
            print(f"   Анализирует все платежи до {end_date} на основе обнаруженного периода")
            print(f"4. Обработать платежи (пользовательская дата анализа)")
            print(f"   Рекомендуемый диапазон: {start_date} до {end_date}")
            print(f"   Принцип: более ранние даты показывают меньше просроченных платежей")
        else:
            print("3. Обработать платежи (дата анализа по умолчанию: сегодня)")
            print("   Анализирует все платежи до сегодняшней даты")
            print("4. Обработать платежи (пользовательская дата анализа)")
            print("   Введите любую дату для анализа статуса платежей на эту дату")
        
        print("5. Интерактивная оболочка (примеры: 'ls output/', 'python main.py --help')")
    else:
        print("Available commands:")
        print("1. Show help")
        print("2. Show version")
        
        # Add detailed descriptions with detected period info
        if detected_period:
            end_date = detected_period.end_date.strftime('%d-%m-%Y')
            start_date = detected_period.start_date.strftime('%d-%m-%Y')
            print(f"3. Process payments (default analysis date: {end_date})")
            print(f"   Analyzes all payments before {end_date} based on detected period")
            print(f"4. Process payments (custom analysis date)")
            print(f"   Recommended range: {start_date} to {end_date}")
            print(f"   Principle: earlier dates show fewer overdue payments")
        else:
            print("3. Process payments (default analysis date: today)")
            print("   Analyzes all payments before today's date")
            print("4. Process payments (custom analysis date)")
            print("   Enter any date to analyze payment status as of that date")
        
        print("5. Interactive shell (examples: 'ls output/', 'python main.py --help')")
    print()
    
    while True:
        try:
            if language == 'ru':
                choice = input("Введите ваш выбор (1-5) или 'q' для выхода: ").strip()
            else:
                choice = input("Enter your choice (1-5) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                break
                
            if choice == '1':
                if language == 'ru':
                    os.system("python main.py --lang ru --help")
                else:
                    os.system("python main.py --help")
                
            elif choice == '2':
                print()
                print("=" * 60)
                if language == 'ru':
                    print("ИНФОРМАЦИЯ О ВЕРСИИ:")
                else:
                    print("VERSION INFO:")
                print("=" * 60)
                if language == 'ru':
                    os.system("python main.py --lang ru version")
                else:
                    os.system("python main.py version")
                print("=" * 60)
                
            elif choice == '3':
                # Use detected period's end date as analysis date, or today if no period detected
                if detected_period:
                    analysis_date_str = detected_period.end_date.strftime('%Y-%m-%d')
                    output_file = f"output/payment_report_{detected_period.end_date.strftime('%Y%m%d')}.xlsx"
                    if language == 'ru':
                        cmd = f'python main.py --lang ru process-payments --garage-file "{garage_file}" --statement-file "{statement_file}" --analysis-date "{analysis_date_str}" --output "{output_file}"'
                    else:
                        cmd = f'python main.py process-payments --garage-file "{garage_file}" --statement-file "{statement_file}" --analysis-date "{analysis_date_str}" --output "{output_file}"'
                else:
                    output_file = f"output/payment_report_{date.today().strftime('%Y%m%d')}.xlsx"
                    if language == 'ru':
                        cmd = f'python main.py --lang ru process-payments --garage-file "{garage_file}" --statement-file "{statement_file}" --output "{output_file}"'
                    else:
                        cmd = f'python main.py process-payments --garage-file "{garage_file}" --statement-file "{statement_file}" --output "{output_file}"'
                if language == 'ru':
                    print(f"Выполняется: {cmd}")
                else:
                    print(f"Running: {cmd}")
                
                # Capture output and separate logs from results
                import subprocess
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                # Show only critical logs, then results clearly separated
                lines = result.stdout.split('\n')
                
                # Find where actual results start (after processing completion message)
                result_start = -1
                for i, line in enumerate(lines):
                    if "Processing completed successfully" in line or "Обработка завершена успешно" in line:
                        result_start = i
                        break
                
                if result_start != -1:
                    print()
                    print("=" * 60)
                    if language == 'ru':
                        print("РЕЗУЛЬТАТЫ ОБРАБОТКИ:")
                    else:
                        print("PROCESSING RESULTS:")
                    print("=" * 60)
                    for line in lines[result_start:]:
                        if line.strip():
                            print(line)
                    print("=" * 60)
                else:
                    # Fallback if pattern not found
                    print()
                    print("=" * 60)
                    if language == 'ru':
                        print("ВЫХОДНЫЕ ДАННЫЕ ОБРАБОТКИ:")
                    else:
                        print("PROCESSING OUTPUT:")
                    print("=" * 60)
                    print(result.stdout)
                    print("=" * 60)
                
                if result.stderr:
                    if language == 'ru':
                        print("Ошибки:", result.stderr)
                    else:
                        print("Errors:", result.stderr)
                
            elif choice == '4':
                if detected_period:
                    if language == 'ru':
                        print(f"Рекомендуемый диапазон дат: {detected_period.start_date} до {detected_period.end_date}")
                        print("Совет: более ранние даты покажут меньше просроченных платежей")
                    else:
                        print(f"Recommended date range: {detected_period.start_date} to {detected_period.end_date}")
                        print("Tip: Earlier dates will show fewer overdue payments")
                
                if language == 'ru':
                    analysis_date = input("Введите дату анализа (ГГГГ-ММ-ДД): ").strip()
                else:
                    analysis_date = input("Enter analysis date (YYYY-MM-DD): ").strip()
                
                if not analysis_date:
                    if language == 'ru':
                        print("Дата не введена, возврат в меню.")
                    else:
                        print("No date entered, returning to menu.")
                    continue
                
                output_file = f"output/payment_report_{analysis_date.replace('-', '')}.xlsx"
                if language == 'ru':
                    cmd = f'python main.py --lang ru process-payments --garage-file "{garage_file}" --statement-file "{statement_file}" --analysis-date "{analysis_date}" --output "{output_file}"'
                    print(f"Выполняется: {cmd}")
                else:
                    cmd = f'python main.py process-payments --garage-file "{garage_file}" --statement-file "{statement_file}" --analysis-date "{analysis_date}" --output "{output_file}"'
                    print(f"Running: {cmd}")
                
                # Capture output and separate logs from results
                import subprocess
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                lines = result.stdout.split('\n')
                result_start = -1
                for i, line in enumerate(lines):
                    if "Processing completed successfully" in line or "Обработка завершена успешно" in line:
                        result_start = i
                        break
                
                if result_start != -1:
                    print()
                    print("=" * 60)
                    if language == 'ru':
                        print("РЕЗУЛЬТАТЫ ОБРАБОТКИ:")
                    else:
                        print("PROCESSING RESULTS:")
                    print("=" * 60)
                    for line in lines[result_start:]:
                        if line.strip():
                            print(line)
                    print("=" * 60)
                else:
                    print()
                    print("=" * 60)
                    if language == 'ru':
                        print("ВЫХОДНЫЕ ДАННЫЕ ОБРАБОТКИ:")
                    else:
                        print("PROCESSING OUTPUT:")
                    print("=" * 60)
                    print(result.stdout)
                    print("=" * 60)
                
                if result.stderr:
                    if language == 'ru':
                        print("Ошибки:", result.stderr)
                    else:
                        print("Errors:", result.stderr)
                
            elif choice == '5':
                if language == 'ru':
                    print("Вход в интерактивную оболочку...")
                    print("Доступные файлы:")
                    print(f"  Файл справочника: {garage_file}")
                    print(f"  Файл выписки: {statement_file}")
                    print("Введите команду (например, 'python main.py process-payments --help')")
                    exit_msg = "Введите 'exit', 'quit' или 'q' для выхода"
                    prompt = "CLI> "
                else:
                    print("Entering interactive shell...")
                    print("Available files:")
                    print(f"  Garage file: {garage_file}")
                    print(f"  Statement file: {statement_file}")
                    print("Type your command (e.g., 'python main.py process-payments --help')")
                    exit_msg = "Type 'exit', 'quit' or 'q' to return to menu"
                    prompt = "CLI> "
                
                print(exit_msg)
                while True:
                    user_cmd = input(prompt).strip()
                    if user_cmd.lower() in ['exit', 'quit', 'q']:
                        break
                    if user_cmd:
                        os.system(user_cmd)
                        
            else:
                if language == 'ru':
                    print("Неверный выбор. Пожалуйста, попробуйте снова.")
                else:
                    print("Invalid choice. Please try again.")
                
            print()
            
        except KeyboardInterrupt:
            if language == 'ru':
                print("\nДо свидания!")
            else:
                print("\nGoodbye!")
            break
        except Exception as e:
            if language == 'ru':
                print(f"Ошибка: {e}")
            else:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()