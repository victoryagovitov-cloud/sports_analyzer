#!/usr/bin/env python3
"""
Демонстрация AI-системы live-анализа ставок
"""

import logging
from enhanced_live_system import EnhancedLiveSystem

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Демонстрация AI-системы"""
    logger.info("🤖 ЗАПУСК AI-СИСТЕМЫ LIVE-АНАЛИЗА СТАВОК 🤖")
    logger.info("=" * 60)
    
    try:
        # Создаем AI-систему
        system = EnhancedLiveSystem()
        logger.info("AI-система инициализирована")
        
        # Запускаем один цикл анализа
        logger.info("Запускаем AI-анализ...")
        system.run_analysis_cycle()
        
        logger.info("=" * 60)
        logger.info("✅ AI-АНАЛИЗ ЗАВЕРШЕН УСПЕШНО!")
        logger.info("Проверьте сгенерированные файлы отчетов:")
        logger.info("- live_analysis_report_*.html (обычный HTML отчет)")
        logger.info("- ai_telegram_report_*.html (AI-отчет для Telegram)")
        
    except Exception as e:
        logger.error(f"Ошибка при запуске AI-системы: {e}")
        raise

if __name__ == "__main__":
    main()