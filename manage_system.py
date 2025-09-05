#!/usr/bin/env python3
"""
Скрипт для управления системой TrueLiveBet AI
"""

import os
import sys
import subprocess
import signal
import psutil
import time
from datetime import datetime

def find_system_processes():
    """Находит процессы системы TrueLiveBet AI"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'start_production.py' in cmdline and 'continuous' in cmdline:
                processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes

def start_system():
    """Запускает систему"""
    print("🚀 ЗАПУСК СИСТЕМЫ TRUELIVEBET AI")
    print("=" * 40)
    
    # Проверяем, не запущена ли уже система
    processes = find_system_processes()
    if processes:
        print(f"❌ Система уже запущена ({len(processes)} процессов)")
        for proc in processes:
            print(f"  PID: {proc.pid}")
        return False
    
    # Запускаем систему
    try:
        cmd = ["python3", "start_production.py", "continuous"]
        process = subprocess.Popen(cmd, stdout=open('production.log', 'w'), stderr=subprocess.STDOUT)
        print(f"✅ Система запущена с PID: {process.pid}")
        print("📋 Логи записываются в production.log")
        return True
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        return False

def stop_system():
    """Останавливает систему"""
    print("🛑 ОСТАНОВКА СИСТЕМЫ TRUELIVEBET AI")
    print("=" * 40)
    
    processes = find_system_processes()
    if not processes:
        print("❌ Система не запущена")
        return False
    
    stopped_count = 0
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=5)
            print(f"✅ Процесс {proc.pid} остановлен")
            stopped_count += 1
        except psutil.TimeoutExpired:
            try:
                proc.kill()
                print(f"⚠️  Процесс {proc.pid} принудительно завершен")
                stopped_count += 1
            except psutil.NoSuchProcess:
                print(f"✅ Процесс {proc.pid} уже завершен")
                stopped_count += 1
        except psutil.NoSuchProcess:
            print(f"✅ Процесс {proc.pid} уже завершен")
            stopped_count += 1
        except Exception as e:
            print(f"❌ Ошибка остановки процесса {proc.pid}: {e}")
    
    print(f"✅ Остановлено {stopped_count} процессов")
    return stopped_count > 0

def restart_system():
    """Перезапускает систему"""
    print("🔄 ПЕРЕЗАПУСК СИСТЕМЫ TRUELIVEBET AI")
    print("=" * 40)
    
    if stop_system():
        print("⏳ Ожидание 3 секунды...")
        time.sleep(3)
    
    return start_system()

def show_status():
    """Показывает статус системы"""
    print("📊 СТАТУС СИСТЕМЫ TRUELIVEBET AI")
    print("=" * 40)
    
    processes = find_system_processes()
    if processes:
        print(f"✅ Система запущена ({len(processes)} процессов)")
        for proc in processes:
            try:
                uptime = time.time() - proc.create_time()
                uptime_str = f"{int(uptime//3600)}ч {int((uptime%3600)//60)}м {int(uptime%60)}с"
                print(f"  PID: {proc.pid} | Uptime: {uptime_str}")
            except:
                print(f"  PID: {proc.pid}")
    else:
        print("❌ Система не запущена")
    
    # Проверяем логи
    if os.path.exists('production.log'):
        try:
            with open('production.log', 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    print(f"\n📋 Последняя запись в логе:")
                    print(f"  {last_line}")
        except:
            pass

def show_menu():
    """Показывает меню управления"""
    print("\n🎛️  УПРАВЛЕНИЕ СИСТЕМОЙ TRUELIVEBET AI")
    print("=" * 40)
    print("1. Запустить систему")
    print("2. Остановить систему")
    print("3. Перезапустить систему")
    print("4. Показать статус")
    print("5. Выход")
    print("=" * 40)

def main():
    """Основная функция"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'start':
            start_system()
        elif command == 'stop':
            stop_system()
        elif command == 'restart':
            restart_system()
        elif command == 'status':
            show_status()
        else:
            print("❌ Неизвестная команда. Используйте: start, stop, restart, status")
    else:
        # Интерактивный режим
        while True:
            show_menu()
            try:
                choice = input("Выберите действие (1-5): ").strip()
                if choice == '1':
                    start_system()
                elif choice == '2':
                    stop_system()
                elif choice == '3':
                    restart_system()
                elif choice == '4':
                    show_status()
                elif choice == '5':
                    print("👋 До свидания!")
                    break
                else:
                    print("❌ Неверный выбор. Попробуйте снова.")
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()