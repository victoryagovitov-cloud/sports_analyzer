#!/usr/bin/env python3
"""
Тестирование Telegram интеграции
"""

import logging
from telegram_integration import TelegramIntegration, test_telegram_integration

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Тестирование Telegram интеграции"""
    logger.info("🧪 ТЕСТИРОВАНИЕ TELEGRAM ИНТЕГРАЦИИ")
    logger.info("=" * 50)
    
    try:
        # Тестируем интеграцию
        test_telegram_integration()
        
        logger.info("=" * 50)
        logger.info("✅ Тестирование завершено!")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании: {e}")

if __name__ == "__main__":
    main()