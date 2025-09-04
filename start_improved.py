#!/usr/bin/env python3
"""
Улучшенный запуск AI-системы с защитой от зависания
"""

import logging
import sys
import signal
import os
import time
from datetime import datetime
from enhanced_live_system import EnhancedLiveSystem
from system_watchdog import system_watchdog, AnalysisTimeoutManager
from config import ANALYSIS_SETTINGS

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('improved_production.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImprovedProductionSystem:
    """Улучшенная продакшен система с защитой от зависания"""
    
    def __init__(self):
        self.system = None
        self.running = False
        self.timeout_manager = AnalysisTimeoutManager(ANALYSIS_SETTINGS['analysis_timeout_seconds'])
        
    def signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        logger.info(f"🛑 Получен сигнал {signum}, завершение работы...")
        self.running = False
        if self.system:
            system_watchdog.stop()
        
    def start(self, mode='continuous'):
        """Запуск системы с улучшенной защитой"""
        try:
            # Настройка обработчиков сигналов
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            logger.info("🚀 ЗАПУСК УЛУЧШЕННОЙ ПРОДАКШЕН СИСТЕМЫ")
            logger.info("=" * 70)
            logger.info(f"Режим работы: {mode}")
            logger.info(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"Таймаут анализа: {ANALYSIS_SETTINGS['analysis_timeout_seconds']} сек")
            logger.info(f"Максимальное использование памяти: {ANALYSIS_SETTINGS['max_memory_usage_percent']}%")
            logger.info("=" * 70)
            
            # Проверка системных требований
            if not self._check_system_requirements():
                return False
            
            # Инициализация системы
            logger.info("🔧 Инициализация AI-системы...")
            self.system = EnhancedLiveSystem()
            logger.info("✅ AI-система инициализирована")
            
            # Тестирование Telegram
            logger.info("📱 Тестирование Telegram интеграции...")
            if not self.system.telegram_integration.test_connection():
                logger.error("❌ Telegram интеграция не работает!")
                logger.error("Проверьте настройки бота и канала")
                return False
            logger.info("✅ Telegram интеграция работает")
            
            self.running = True
            
            if mode == 'continuous':
                return self.run_continuous()
            elif mode == 'single':
                return self.run_single()
            else:
                logger.error(f"Неизвестный режим: {mode}")
                return False
                
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            logger.exception("Детали критической ошибки:")
            return False
    
    def _check_system_requirements(self):
        """Проверка системных требований"""
        try:
            import psutil
            
            # Проверка памяти
            memory = psutil.virtual_memory()
            if memory.available < 500 * 1024 * 1024:  # Менее 500 МБ
                logger.warning(f"⚠️  Мало свободной памяти: {memory.available / (1024*1024):.1f} МБ")
            
            # Проверка места на диске
            disk = psutil.disk_usage('/')
            if disk.free < 1024 * 1024 * 1024:  # Менее 1 ГБ
                logger.warning(f"⚠️  Мало свободного места: {disk.free / (1024*1024*1024):.1f} ГБ")
            
            # Проверка зависимостей
            required_modules = {
                'requests': 'requests',
                'beautifulsoup4': 'bs4',  # beautifulsoup4 импортируется как bs4
                'fuzzywuzzy': 'fuzzywuzzy',
                'schedule': 'schedule',
                'psutil': 'psutil'
            }
            for package_name, import_name in required_modules.items():
                try:
                    __import__(import_name)
                except ImportError:
                    logger.error(f"❌ Отсутствует модуль: {package_name} (импорт: {import_name})")
                    return False
            
            logger.info("✅ Системные требования выполнены")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки системных требований: {e}")
            return True  # Продолжаем работу
    
    def run_continuous(self):
        """Запуск непрерывного режима с защитой от зависания"""
        logger.info("🔄 ЗАПУСК НЕПРЕРЫВНОГО РЕЖИМА С ЗАЩИТОЙ ОТ ЗАВИСАНИЯ")
        logger.info("Система будет работать 24/7")
        logger.info("Анализ каждые 50 минут")
        logger.info("Автоматический перезапуск при проблемах")
        logger.info("Для остановки нажмите Ctrl+C")
        logger.info("-" * 70)
        
        restart_count = 0
        max_restarts = 5
        
        while self.running and restart_count < max_restarts:
            try:
                logger.info(f"🔄 Попытка запуска #{restart_count + 1}")
                self.system.run_continuous()
                break  # Успешное завершение
                
            except KeyboardInterrupt:
                logger.info("Получен сигнал остановки")
                break
                
            except Exception as e:
                restart_count += 1
                logger.error(f"❌ Ошибка в непрерывном режиме (попытка {restart_count}/{max_restarts}): {e}")
                logger.exception("Детали ошибки:")
                
                if restart_count < max_restarts:
                    logger.info(f"🔄 Перезапуск через 30 секунд...")
                    time.sleep(30)
                    
                    # Пересоздаем систему
                    try:
                        self.system = EnhancedLiveSystem()
                        logger.info("✅ Система пересоздана")
                    except Exception as restart_error:
                        logger.error(f"❌ Ошибка пересоздания системы: {restart_error}")
                        break
                else:
                    logger.error("❌ Превышено максимальное количество перезапусков")
                    break
        
        self.shutdown()
        return restart_count < max_restarts
    
    def run_single(self):
        """Запуск одиночного анализа с таймаутом"""
        logger.info("🔍 ЗАПУСК ОДИНОЧНОГО АНАЛИЗА С ТАЙМАУТОМ")
        logger.info("-" * 70)
        
        try:
            # Запускаем таймаут-менеджер
            self.timeout_manager.start_analysis()
            
            # Выполняем анализ
            self.system.run_single()
            
            # Проверяем, не было ли превышения таймаута
            if self.timeout_manager.check_timeout():
                logger.error("❌ Анализ был прерван по таймауту")
                return False
            else:
                logger.info("✅ Анализ завершен успешно")
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка при анализе: {e}")
            logger.exception("Детали ошибки:")
            return False
        finally:
            self.timeout_manager.finish_analysis()
            self.shutdown()
    
    def shutdown(self):
        """Корректное завершение работы"""
        logger.info("🛑 ЗАВЕРШЕНИЕ РАБОТЫ УЛУЧШЕННОЙ СИСТЕМЫ")
        logger.info(f"Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Остановка watchdog
        try:
            system_watchdog.stop()
            logger.info("✅ Watchdog остановлен")
        except Exception as e:
            logger.error(f"Ошибка остановки watchdog: {e}")
        
        logger.info("=" * 70)
        self.running = False

def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python3 start_improved.py continuous  # Непрерывная работа с защитой")
        print("  python3 start_improved.py single     # Одиночный анализ с таймаутом")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode not in ['continuous', 'single']:
        print("Ошибка: режим должен быть 'continuous' или 'single'")
        sys.exit(1)
    
    production = ImprovedProductionSystem()
    success = production.start(mode)
    
    if success:
        logger.info("✅ Система завершила работу корректно")
        sys.exit(0)
    else:
        logger.error("❌ Система завершилась с ошибкой")
        sys.exit(1)

if __name__ == "__main__":
    main()