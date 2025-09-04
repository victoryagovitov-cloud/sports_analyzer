#!/usr/bin/env python3
"""
Демонстрация Live Betting Analysis System
"""

import subprocess
import time
import os
from datetime import datetime

def print_banner():
    """Печать баннера"""
    print("=" * 80)
    print("🎯 LIVE BETTING ANALYSIS SYSTEM - ДЕМОНСТРАЦИЯ")
    print("=" * 80)
    print("Система анализа live-ставок с реальными данными")
    print("Источник данных: Scores24.live")
    print("=" * 80)

def run_demo():
    """Запуск демонстрации"""
    print_banner()
    
    print("\n🔍 Запуск единичного анализа...")
    print("-" * 50)
    
    try:
        # Запускаем единичный анализ
        result = subprocess.run(
            ['python3', 'live_betting_system.py', 'single'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Анализ завершен успешно!")
            print("\n📊 Результаты:")
            print(result.stdout)
            
            # Ищем последний сгенерированный отчет
            report_files = [f for f in os.listdir('.') if f.startswith('live_report_') and f.endswith('.html')]
            if report_files:
                latest_report = max(report_files)
                print(f"\n📁 Последний отчет: {latest_report}")
                
                # Показываем содержимое отчета
                with open(latest_report, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"\n📄 Содержимое отчета ({len(content)} символов):")
                    print("-" * 50)
                    print(content)
                    print("-" * 50)
            
        else:
            print("❌ Ошибка при выполнении анализа:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Таймаут выполнения анализа")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def show_system_info():
    """Показ информации о системе"""
    print("\n📋 Информация о системе:")
    print("-" * 50)
    
    # Проверяем файлы
    files_to_check = [
        'live_betting_system.py',
        'enhanced_real_controller.py',
        'real_data_controller.py',
        'requirements.txt'
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file} ({size} байт)")
        else:
            print(f"❌ {file} - не найден")
    
    # Проверяем логи
    if os.path.exists('live_betting.log'):
        log_size = os.path.getsize('live_betting.log')
        print(f"📝 live_betting.log ({log_size} байт)")
    
    # Проверяем отчеты
    report_files = [f for f in os.listdir('.') if f.startswith('live_report_') and f.endswith('.html')]
    print(f"📊 Сгенерировано отчетов: {len(report_files)}")
    
    if report_files:
        latest_report = max(report_files)
        print(f"📁 Последний отчет: {latest_report}")

def main():
    """Основная функция"""
    print("🚀 Запуск демонстрации Live Betting Analysis System")
    
    # Показываем информацию о системе
    show_system_info()
    
    # Запускаем демо
    run_demo()
    
    print("\n" + "=" * 80)
    print("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 80)
    print("\n💡 Для использования системы:")
    print("   python3 live_betting_system.py single      # Единичный анализ")
    print("   python3 live_betting_system.py continuous  # Непрерывный анализ")
    print("\n📚 Документация: README_LIVE_SYSTEM.md")
    print("=" * 80)

if __name__ == "__main__":
    main()