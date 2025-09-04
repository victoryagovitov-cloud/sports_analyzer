#!/usr/bin/env python3
"""
Демонстрация AI-системы с отправкой в Telegram канал
"""

import logging
from datetime import datetime
from enhanced_live_system import EnhancedLiveSystem

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Выводит баннер системы"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🤖 AI LIVE BETTING SYSTEM + TELEGRAM 🤖                                   ║
║                                                                              ║
║  Полная система с отправкой рекомендаций в Telegram канал                   ║
║  • AI-анализ всех live-матчей                                               ║
║  • Автоматическая отправка в @truelivebet                                   ║
║  • Умные рекомендации с обоснованиями                                        ║
║  • Мульти-источниковый сбор данных                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Демонстрация полной системы с Telegram"""
    print_banner()
    
    logger.info("🚀 ЗАПУСК ПОЛНОЙ AI-СИСТЕМЫ С TELEGRAM")
    logger.info("=" * 60)
    
    try:
        # Создаем AI-систему с Telegram интеграцией
        logger.info("Инициализация AI-системы с Telegram...")
        system = EnhancedLiveSystem()
        logger.info("✅ AI-система с Telegram успешно инициализирована")
        
        # Запускаем один цикл анализа с отправкой в Telegram
        logger.info("🤖 Запуск AI-анализа с отправкой в Telegram канал...")
        start_time = datetime.now()
        
        system.run_analysis_cycle()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 60)
        logger.info("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        logger.info(f"⏱️ Время выполнения: {duration:.2f} секунд")
        
        # Информация о результатах
        logger.info("📁 СГЕНЕРИРОВАННЫЕ ФАЙЛЫ:")
        logger.info("• live_analysis_report_*.html - Обычный HTML отчет")
        logger.info("• ai_telegram_report_*.html - AI-отчет для Telegram")
        logger.info("• live_analysis.log - Детальные логи системы")
        
        logger.info("📱 TELEGRAM КАНАЛ:")
        logger.info("• Канал: @truelivebet")
        logger.info("• Бот: @TrueLiveBetBot")
        logger.info("• Рекомендации отправлены автоматически")
        
        # Рекомендации по использованию
        logger.info("💡 РЕКОМЕНДАЦИИ ПО ИСПОЛЬЗОВАНИЮ:")
        logger.info("• Для непрерывной работы: python3 enhanced_live_system.py --continuous")
        logger.info("• Для одиночного анализа: python3 enhanced_live_system.py --single")
        logger.info("• Для тестирования Telegram: python3 test_telegram.py")
        
        logger.info("=" * 60)
        logger.info("💎 TrueLiveBet AI – Умные ставки с искусственным интеллектом! 💎")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске демонстрации: {e}")
        logger.error("Проверьте логи для получения подробной информации")
        raise

if __name__ == "__main__":
    main()