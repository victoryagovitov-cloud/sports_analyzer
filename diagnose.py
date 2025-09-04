#!/usr/bin/env python3
"""
Скрипт быстрой диагностики системы
"""

import sys
import time
import requests
import psutil
from datetime import datetime

def check_dependencies():
    """Проверка зависимостей"""
    print("🔍 Проверка зависимостей...")
    
    required_modules = {
        'requests': 'requests',
        'beautifulsoup4': 'bs4',
        'fuzzywuzzy': 'fuzzywuzzy',
        'schedule': 'schedule',
        'psutil': 'psutil'
    }
    
    all_ok = True
    for package_name, import_name in required_modules.items():
        try:
            __import__(import_name)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  ❌ {package_name} - ОТСУТСТВУЕТ")
            all_ok = False
    
    return all_ok

def check_system_resources():
    """Проверка системных ресурсов"""
    print("\n💻 Проверка системных ресурсов...")
    
    # Память
    memory = psutil.virtual_memory()
    print(f"  📊 Память: {memory.percent}% использовано, {memory.available / (1024*1024*1024):.1f} ГБ свободно")
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"  🖥️  CPU: {cpu_percent}% загружен")
    
    # Диск
    disk = psutil.disk_usage('/')
    disk_percent = (disk.used / disk.total) * 100
    print(f"  💾 Диск: {disk_percent:.1f}% использовано, {disk.free / (1024*1024*1024):.1f} ГБ свободно")
    
    # Проверка критических значений
    issues = []
    if memory.percent > 80:
        issues.append(f"Высокое потребление памяти: {memory.percent}%")
    if cpu_percent > 90:
        issues.append(f"Высокая загрузка CPU: {cpu_percent}%")
    if disk_percent > 90:
        issues.append(f"Мало места на диске: {disk_percent:.1f}%")
    
    if issues:
        print("  ⚠️  Предупреждения:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print("  ✅ Все ресурсы в норме")

def check_network():
    """Проверка сетевых подключений"""
    print("\n🌐 Проверка сетевых подключений...")
    
    urls_to_check = [
        ('Betzona футбол', 'https://betzona.ru/live-futbol.html'),
        ('Scores24 футбол', 'https://scores24.live/ru/soccer?matchesFilter=live'),
        ('Telegram API', 'https://api.telegram.org'),
    ]
    
    for name, url in urls_to_check:
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"  ✅ {name}: {response.status_code} ({response_time:.2f}с)")
            else:
                print(f"  ⚠️  {name}: {response.status_code} ({response_time:.2f}с)")
                
        except requests.exceptions.Timeout:
            print(f"  ❌ {name}: ТАЙМАУТ (>10с)")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {name}: ОШИБКА - {e}")

def check_telegram():
    """Проверка Telegram интеграции"""
    print("\n📱 Проверка Telegram интеграции...")
    
    try:
        from telegram_integration import TelegramIntegration
        
        telegram = TelegramIntegration()
        if telegram.test_connection():
            print("  ✅ Telegram интеграция работает")
        else:
            print("  ❌ Telegram интеграция не работает")
            
    except Exception as e:
        print(f"  ❌ Ошибка проверки Telegram: {e}")

def check_config():
    """Проверка конфигурации"""
    print("\n⚙️  Проверка конфигурации...")
    
    try:
        from config import ANALYSIS_SETTINGS
        
        important_settings = [
            'http_timeout_seconds',
            'analysis_timeout_seconds',
            'max_retries',
            'max_memory_usage_percent'
        ]
        
        for setting in important_settings:
            if setting in ANALYSIS_SETTINGS:
                value = ANALYSIS_SETTINGS[setting]
                print(f"  ✅ {setting}: {value}")
            else:
                print(f"  ❌ {setting}: НЕ НАЙДЕНО")
                
    except Exception as e:
        print(f"  ❌ Ошибка загрузки конфигурации: {e}")

def run_quick_test():
    """Быстрый тест системы"""
    print("\n🧪 Быстрый тест системы...")
    
    try:
        print("  🔄 Запуск тестового анализа...")
        import subprocess
        
        result = subprocess.run([
            'timeout', '30', 'python3', 'start_improved.py', 'single'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ Тестовый анализ прошел успешно")
        else:
            print(f"  ❌ Тестовый анализ завершился с ошибкой (код: {result.returncode})")
            if result.stderr:
                print(f"    Ошибки: {result.stderr[:200]}...")
                
    except Exception as e:
        print(f"  ❌ Ошибка тестового анализа: {e}")

def main():
    """Главная функция диагностики"""
    print("🔧 ДИАГНОСТИКА СИСТЕМЫ TRUELIVEBET AI")
    print("=" * 50)
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Выполняем все проверки
    deps_ok = check_dependencies()
    check_system_resources()
    check_network()
    check_telegram()
    check_config()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_quick_test()
    
    print("\n" + "=" * 50)
    if deps_ok:
        print("🎯 ДИАГНОСТИКА ЗАВЕРШЕНА - система готова к работе")
        print("\nДля запуска используйте:")
        print("  python3 start_improved.py single    # Одиночный анализ")
        print("  python3 start_improved.py continuous # Непрерывная работа")
    else:
        print("❌ ДИАГНОСТИКА ВЫЯВИЛА ПРОБЛЕМЫ - установите недостающие модули")
        print("\nДля установки зависимостей:")
        print("  pip3 install --break-system-packages -r requirements.txt")

if __name__ == "__main__":
    main()