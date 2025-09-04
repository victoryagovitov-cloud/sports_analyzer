"""
Пример запуска системы анализа live-ставок
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import LiveBettingAnalyzer
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_single_analysis():
    """Запуск единичного анализа для демонстрации"""
    print("=" * 60)
    print("ЗАПУСК ЕДИНИЧНОГО АНАЛИЗА LIVE-СТАВОК")
    print("=" * 60)
    
    analyzer = LiveBettingAnalyzer()
    
    try:
        # Выполняем один цикл анализа
        analyzer.run_single_analysis()
        
        # Показываем статистику
        counts = analyzer.report_generator.get_recommendations_count()
        total = analyzer.report_generator.get_total_recommendations_count()
        
        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТЫ АНАЛИЗА:")
        print("=" * 60)
        print(f"Футбол: {counts['football']} рекомендаций")
        print(f"Теннис: {counts['tennis']} рекомендаций")
        print(f"Настольный теннис: {counts['table_tennis']} рекомендаций")
        print(f"Гандбол: {counts['handball']} рекомендаций")
        print(f"ВСЕГО: {total} рекомендаций")
        
        if total > 0:
            print("\nОтчет сохранен в папке reports/")
            print("Для просмотра откройте последний созданный HTML файл")
        
    except Exception as e:
        logger.error(f"Ошибка при выполнении анализа: {e}")
        import traceback
        traceback.print_exc()
    finally:
        analyzer.stop_analysis()


def run_continuous_analysis():
    """Запуск непрерывного анализа (каждые 50 минут)"""
    print("=" * 60)
    print("ЗАПУСК НЕПРЕРЫВНОГО АНАЛИЗА LIVE-СТАВОК")
    print("=" * 60)
    print("Анализ будет выполняться каждые 50 минут")
    print("Для остановки нажмите Ctrl+C")
    print("=" * 60)
    
    analyzer = LiveBettingAnalyzer()
    
    try:
        analyzer.start_analysis()
    except KeyboardInterrupt:
        print("\nПолучен сигнал остановки...")
        analyzer.stop_analysis()
        print("Анализ остановлен")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        analyzer.stop_analysis()


def show_help():
    """Показать справку"""
    print("=" * 60)
    print("СИСТЕМА АНАЛИЗА LIVE-СТАВОК")
    print("=" * 60)
    print("Использование:")
    print("  python run_example.py single    - Единичный анализ")
    print("  python run_example.py continuous - Непрерывный анализ")
    print("  python run_example.py help      - Эта справка")
    print("")
    print("Примеры:")
    print("  python run_example.py single")
    print("  python run_example.py continuous")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "single":
        run_single_analysis()
    elif command == "continuous":
        run_continuous_analysis()
    elif command == "help":
        show_help()
    else:
        print(f"Неизвестная команда: {command}")
        show_help()
        sys.exit(1)