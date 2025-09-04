#!/usr/bin/env python3
"""
Управление системой TrueLiveBet AI
"""

import os
import sys
import subprocess
import signal
import psutil
import time
from datetime import datetime

class TrueLiveBetController:
    """Контроллер для управления системой TrueLiveBet AI"""
    
    def __init__(self):
        self.system_processes = []
        
    def check_status(self):
        """Проверка статуса системы"""
        print("🔍 ПРОВЕРКА СТАТУСА TRUELIVEBET AI")
        print("=" * 40)
        
        # Ищем процессы системы
        running_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if any(keyword in cmdline.lower() for keyword in 
                      ['start_improved', 'enhanced_live', 'truelivebet', 'sports_analyzer']):
                    running_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': cmdline
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if running_processes:
            print(f"✅ Найдено {len(running_processes)} активных процессов:")
            for i, proc in enumerate(running_processes, 1):
                print(f"  {i}. PID: {proc['pid']} - {proc['cmdline'][:80]}...")
        else:
            print("❌ Система не запущена")
        
        # Проверяем последние логи
        log_files = ['improved_production.log', 'production.log', 'live_betting_analysis.log']
        print(f"\n📋 Последние логи:")
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    mtime = os.path.getmtime(log_file)
                    last_modified = datetime.fromtimestamp(mtime).strftime('%H:%M:%S %d.%m.%Y')
                    size = os.path.getsize(log_file)
                    print(f"  📄 {log_file}: {size} байт, изменен {last_modified}")
                except Exception:
                    print(f"  📄 {log_file}: файл существует")
        
        return running_processes
    
    def stop_all(self):
        """Остановка всех процессов системы"""
        print("🛑 ОСТАНОВКА TRUELIVEBET AI")
        print("=" * 30)
        
        stopped_count = 0
        
        # Ищем и останавливаем процессы
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if any(keyword in cmdline.lower() for keyword in 
                      ['start_improved', 'enhanced_live', 'main.py', 'quick_start.py']):
                    
                    if 'sports_analyzer' in cmdline or 'truelivebet' in cmdline.lower():
                        print(f"🔄 Останавливаю процесс PID {proc.info['pid']}: {cmdline[:60]}...")
                        
                        try:
                            # Сначала пробуем мягкую остановку
                            os.kill(proc.info['pid'], signal.SIGTERM)
                            time.sleep(2)
                            
                            # Проверяем, завершился ли процесс
                            if psutil.pid_exists(proc.info['pid']):
                                print(f"⚠️  Принудительная остановка PID {proc.info['pid']}")
                                os.kill(proc.info['pid'], signal.SIGKILL)
                            
                            stopped_count += 1
                            print(f"✅ Процесс PID {proc.info['pid']} остановлен")
                            
                        except ProcessLookupError:
                            print(f"✅ Процесс PID {proc.info['pid']} уже завершен")
                            stopped_count += 1
                        except PermissionError:
                            print(f"❌ Нет прав для остановки PID {proc.info['pid']}")
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if stopped_count > 0:
            print(f"\n✅ Остановлено {stopped_count} процессов")
        else:
            print("\n✅ Система уже была остановлена")
        
        # Проверяем, что все остановлено
        time.sleep(1)
        remaining = self.check_status()
        if not remaining:
            print("\n🎯 Система полностью остановлена")
        
        return stopped_count
    
    def start_single(self):
        """Запуск одиночного анализа"""
        print("🚀 ЗАПУСК ОДИНОЧНОГО АНАЛИЗА")
        print("=" * 35)
        
        try:
            # Проверяем, что система не запущена
            if self.check_status():
                print("⚠️  Система уже запущена! Сначала остановите её.")
                return False
            
            # Запускаем одиночный анализ
            print("🔄 Запускаем python3 start_improved.py single...")
            result = subprocess.run([
                'python3', 'start_improved.py', 'single'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Одиночный анализ завершен успешно")
                return True
            else:
                print(f"❌ Ошибка анализа (код: {result.returncode})")
                if result.stderr:
                    print(f"Ошибки: {result.stderr[-500:]}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Анализ превысил таймаут 5 минут")
            return False
        except Exception as e:
            print(f"❌ Ошибка запуска: {e}")
            return False
    
    def start_continuous_background(self):
        """Запуск непрерывной работы в фоне"""
        print("🔄 ЗАПУСК НЕПРЕРЫВНОЙ РАБОТЫ В ФОНЕ")
        print("=" * 40)
        
        # Проверяем, что система не запущена
        if self.check_status():
            print("⚠️  Система уже запущена!")
            return False
        
        try:
            # Запускаем в фоне
            process = subprocess.Popen([
                'python3', 'start_improved.py', 'continuous'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print(f"✅ Система запущена в фоне (PID: {process.pid})")
            print("📋 Для остановки используйте: python3 control_system.py stop")
            print("📋 Для проверки статуса: python3 control_system.py status")
            print("📋 Для просмотра логов: tail -f improved_production.log")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка запуска в фоне: {e}")
            return False

def main():
    """Главная функция"""
    controller = TrueLiveBetController()
    
    if len(sys.argv) < 2:
        print("🎮 УПРАВЛЕНИЕ TRUELIVEBET AI")
        print("=" * 30)
        print("Использование:")
        print("  python3 control_system.py status      # Проверка статуса")
        print("  python3 control_system.py stop        # Остановка системы")
        print("  python3 control_system.py single      # Одиночный анализ")
        print("  python3 control_system.py start       # Запуск в фоне")
        print("  python3 control_system.py restart     # Перезапуск")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'status':
        controller.check_status()
        
    elif command == 'stop':
        controller.stop_all()
        
    elif command == 'single':
        controller.start_single()
        
    elif command == 'start':
        controller.start_continuous_background()
        
    elif command == 'restart':
        print("🔄 ПЕРЕЗАПУСК СИСТЕМЫ")
        print("=" * 20)
        controller.stop_all()
        time.sleep(3)
        controller.start_continuous_background()
        
    else:
        print(f"❌ Неизвестная команда: {command}")
        print("Доступные команды: status, stop, single, start, restart")
        sys.exit(1)

if __name__ == "__main__":
    main()