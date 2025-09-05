#!/usr/bin/env python3
"""
Скрипт для проверки статуса системы TrueLiveBet AI
"""

import psutil
import os
import time
from datetime import datetime

def check_system_status():
    """Проверяет статус системы TrueLiveBet AI"""
    print("🔍 ПРОВЕРКА СТАТУСА TRUELIVEBET AI")
    print("=" * 50)
    print(f"Время проверки: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}")
    print()
    
    # Ищем процессы системы
    running_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'start_production.py' in cmdline and 'continuous' in cmdline:
                running_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': cmdline,
                    'create_time': proc.info['create_time']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if running_processes:
        print(f"✅ Найдено {len(running_processes)} активных процессов:")
        for i, proc in enumerate(running_processes, 1):
            uptime = time.time() - proc['create_time']
            uptime_str = f"{int(uptime//3600)}ч {int((uptime%3600)//60)}м {int(uptime%60)}с"
            print(f"  {i}. PID: {proc['pid']} | Uptime: {uptime_str}")
            print(f"     Команда: {proc['cmdline'][:80]}...")
    else:
        print("❌ Система не запущена")
    
    # Проверяем логи
    print(f"\n📋 Последние логи:")
    log_files = ['production.log', 'live_betting_analysis.log']
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        print(f"  {log_file}: {last_line}")
                    else:
                        print(f"  {log_file}: (пустой файл)")
            except Exception as e:
                print(f"  {log_file}: Ошибка чтения - {e}")
        else:
            print(f"  {log_file}: (файл не найден)")
    
    # Проверяем отчеты
    print(f"\n📊 Последние отчеты:")
    reports_dir = "reports"
    if os.path.exists(reports_dir):
        try:
            report_files = [f for f in os.listdir(reports_dir) if f.endswith('.html')]
            if report_files:
                report_files.sort(key=lambda x: os.path.getmtime(os.path.join(reports_dir, x)), reverse=True)
                latest_report = report_files[0]
                report_path = os.path.join(reports_dir, latest_report)
                mtime = os.path.getmtime(report_path)
                mtime_str = datetime.fromtimestamp(mtime).strftime('%H:%M:%S %d.%m.%Y')
                print(f"  Последний отчет: {latest_report}")
                print(f"  Время создания: {mtime_str}")
            else:
                print("  Отчеты не найдены")
        except Exception as e:
            print(f"  Ошибка чтения папки reports: {e}")
    else:
        print("  Папка reports не найдена")
    
    print(f"\n{'='*50}")
    if running_processes:
        print("✅ СИСТЕМА РАБОТАЕТ")
    else:
        print("❌ СИСТЕМА НЕ РАБОТАЕТ")

if __name__ == "__main__":
    check_system_status()