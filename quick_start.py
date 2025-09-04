#!/usr/bin/env python3
"""
Быстрый запуск AI-системы с Telegram
"""

import sys
import subprocess
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_menu():
    """Выводит меню выбора"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🤖 TrueLiveBet AI - Быстрый запуск 🤖                                     ║
║                                                                              ║
║  Выберите режим работы:                                                      ║
║                                                                              ║
║  1. 🚀 Демонстрация (с отправкой в Telegram)                                ║
║  2. 🔍 Одиночный анализ (с отправкой в Telegram)                            ║
║  3. 🔄 Непрерывная работа (24/7)                                             ║
║  4. 🧪 Тест Telegram подключения                                             ║
║  5. ❌ Выход                                                                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

def run_demo():
    """Запуск демонстрации"""
    logger.info("🚀 Запуск демонстрации с Telegram...")
    try:
        subprocess.run([sys.executable, "telegram_ai_demo.py"], check=True)
        logger.info("✅ Демонстрация завершена успешно")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Ошибка при запуске демонстрации: {e}")
    except FileNotFoundError:
        logger.error("❌ Файл telegram_ai_demo.py не найден")

def run_single():
    """Запуск одиночного анализа"""
    logger.info("🔍 Запуск одиночного анализа...")
    try:
        subprocess.run([sys.executable, "start_production.py", "single"], check=True)
        logger.info("✅ Анализ завершен успешно")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Ошибка при анализе: {e}")
    except FileNotFoundError:
        logger.error("❌ Файл start_production.py не найден")

def run_continuous():
    """Запуск непрерывной работы"""
    logger.info("🔄 Запуск непрерывной работы...")
    logger.info("⚠️  Для остановки нажмите Ctrl+C")
    try:
        subprocess.run([sys.executable, "start_production.py", "continuous"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Ошибка при непрерывной работе: {e}")
    except KeyboardInterrupt:
        logger.info("🛑 Остановка по запросу пользователя")
    except FileNotFoundError:
        logger.error("❌ Файл start_production.py не найден")

def test_telegram():
    """Тест Telegram подключения"""
    logger.info("🧪 Тестирование Telegram подключения...")
    try:
        subprocess.run([sys.executable, "test_telegram.py"], check=True)
        logger.info("✅ Тест Telegram завершен")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Ошибка при тестировании Telegram: {e}")
    except FileNotFoundError:
        logger.error("❌ Файл test_telegram.py не найден")

def main():
    """Главная функция"""
    while True:
        print_menu()
        
        try:
            choice = input("Введите номер (1-5): ").strip()
            
            if choice == "1":
                run_demo()
            elif choice == "2":
                run_single()
            elif choice == "3":
                run_continuous()
            elif choice == "4":
                test_telegram()
            elif choice == "5":
                logger.info("👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
                continue
                
        except KeyboardInterrupt:
            logger.info("\n👋 До свидания!")
            break
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка: {e}")
        
        # Пауза перед следующим выбором
        if choice in ["1", "2", "4"]:
            input("\nНажмите Enter для продолжения...")

if __name__ == "__main__":
    main()