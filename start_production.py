#!/usr/bin/env python3
"""
Продакшен запуск AI-системы с Telegram интеграцией
"""

import logging
import sys
import signal
from datetime import datetime
from enhanced_live_system import EnhancedLiveSystem

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionSystem:
    """Продакшен система с обработкой сигналов"""
    
    def __init__(self):
        self.system = None
        self.running = False
        
    def signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        logger.info(f"Получен сигнал {signum}, завершение работы...")
        self.running = False
        
    def start(self, mode='continuous'):
        """Запуск системы"""
        try:
            # Настройка обработчиков сигналов
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            logger.info("🚀 ЗАПУСК ПРОДАКШЕН СИСТЕМЫ")
            logger.info("=" * 60)
            logger.info(f"Режим работы: {mode}")
            logger.info(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)
            
            # Инициализация системы
            logger.info("Инициализация AI-системы...")
            self.system = EnhancedLiveSystem()
            logger.info("✅ AI-система инициализирована")
            
            # Тестирование Telegram
            logger.info("Тестирование Telegram интеграции...")
            if not self.system.telegram_integration.test_connection():
                logger.error("❌ Telegram интеграция не работает!")
                logger.error("Проверьте настройки бота и канала")
                return False
            logger.info("✅ Telegram интеграция работает")
            
            self.running = True
            
            if mode == 'continuous':
                self.run_continuous()
                return True
            elif mode == 'single':
                return self.run_single()
            else:
                logger.error(f"Неизвестный режим: {mode}")
                return False
                
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            return False
    
    def run_continuous(self):
        """Запуск непрерывного режима"""
        logger.info("🔄 ЗАПУСК НЕПРЕРЫВНОГО РЕЖИМА")
        logger.info("Система будет работать 24/7")
        logger.info("Анализ каждые 50 минут")
        logger.info("Для остановки нажмите Ctrl+C")
        logger.info("-" * 60)
        
        try:
            self.system.run_continuous()
        except KeyboardInterrupt:
            logger.info("Получен сигнал остановки")
        except Exception as e:
            logger.error(f"Ошибка в непрерывном режиме: {e}")
        finally:
            self.shutdown()
    
    def run_single(self):
        """Запуск одиночного анализа"""
        logger.info("🔍 ЗАПУСК ОДИНОЧНОГО АНАЛИЗА")
        logger.info("-" * 60)
        
        try:
            self.system.run_single()
            logger.info("✅ Анализ завершен успешно")
            return True
        except Exception as e:
            logger.error(f"Ошибка при анализе: {e}")
            return False
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Корректное завершение работы"""
        logger.info("🛑 ЗАВЕРШЕНИЕ РАБОТЫ СИСТЕМЫ")
        logger.info(f"Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        self.running = False

def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python3 start_production.py continuous  # Непрерывная работа")
        print("  python3 start_production.py single     # Одиночный анализ")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode not in ['continuous', 'single']:
        print("Ошибка: режим должен быть 'continuous' или 'single'")
        sys.exit(1)
    
    production = ProductionSystem()
    success = production.start(mode)
    
    if success:
        logger.info("✅ Система завершила работу корректно")
        sys.exit(0)
    else:
        logger.error("❌ Система завершилась с ошибкой")
        sys.exit(1)

if __name__ == "__main__":
    main()