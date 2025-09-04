#!/usr/bin/env python3
"""
Полная демонстрация AI-системы live-анализа ставок
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
║  🤖 AI LIVE BETTING ANALYSIS SYSTEM 🤖                                      ║
║                                                                              ║
║  Система искусственного интеллекта для анализа live-ставок                  ║
║  • Умный анализ всех найденных матчей                                       ║
║  • Многофакторная оценка уверенности                                        ║
║  • Автоматическая генерация рекомендаций для Telegram                       ║
║  • Поддержка футбола, тенниса, настольного тенниса, гандбола                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_system_info():
    """Выводит информацию о системе"""
    info = """
📊 ВОЗМОЖНОСТИ СИСТЕМЫ:
• AI-анализ матчей с учетом множества факторов
• Автоматическое определение качества лиг и турниров
• Динамический расчет коэффициентов
• Интеллектуальные обоснования рекомендаций
• Мульти-источниковый сбор данных (Betzona.ru + Scores24.live)
• Генерация отчетов для Telegram канала

🎯 ПОДДЕРЖИВАЕМЫЕ ВИДЫ СПОРТА:
• ⚽ Футбол: Анализ преимущества, времени, качества лиги
• 🎾 Теннис: Анализ сетов, геймов, турниров
• 🏓 Настольный теннис: Аналогично теннису
• 🤾 Гандбол: Прямые победы и тоталы

🔧 ИСТОЧНИКИ ДАННЫХ:
• Betzona.ru: Основной источник live-данных
• Scores24.live: Дополнительная статистика
• Автоматическая дедупликация и приоритизация
    """
    print(info)

def main():
    """Главная функция демонстрации"""
    print_banner()
    print_system_info()
    
    logger.info("🚀 ЗАПУСК ПОЛНОЙ ДЕМОНСТРАЦИИ AI-СИСТЕМЫ")
    logger.info("=" * 80)
    
    try:
        # Создаем AI-систему
        logger.info("Инициализация AI-системы...")
        system = EnhancedLiveSystem()
        logger.info("✅ AI-система успешно инициализирована")
        
        # Запускаем анализ
        logger.info("🤖 Запуск AI-анализа всех видов спорта...")
        start_time = datetime.now()
        
        system.run_analysis_cycle()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 80)
        logger.info("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        logger.info(f"⏱️ Время выполнения: {duration:.2f} секунд")
        
        # Информация о результатах
        logger.info("📁 СГЕНЕРИРОВАННЫЕ ФАЙЛЫ:")
        logger.info("• live_analysis_report_*.html - Обычный HTML отчет")
        logger.info("• ai_telegram_report_*.html - AI-отчет для Telegram")
        logger.info("• live_analysis.log - Детальные логи системы")
        
        # Рекомендации по использованию
        logger.info("💡 РЕКОМЕНДАЦИИ ПО ИСПОЛЬЗОВАНИЮ:")
        logger.info("• Для непрерывной работы: python3 enhanced_live_system.py --continuous")
        logger.info("• Для одиночного анализа: python3 enhanced_live_system.py --single")
        logger.info("• Для интеграции с Claude API: настройте claude_integration.py")
        
        logger.info("=" * 80)
        logger.info("💎 TrueLiveBet AI – Умные ставки с искусственным интеллектом! 💎")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске демонстрации: {e}")
        logger.error("Проверьте логи для получения подробной информации")
        raise

if __name__ == "__main__":
    main()