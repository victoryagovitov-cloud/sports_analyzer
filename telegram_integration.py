"""
Интеграция Telegram с AI-системой live-анализа ставок
"""

import logging
import os
from datetime import datetime
from typing import List, Optional
from telegram_bot import TelegramChannelManager, TELEGRAM_CONFIG
from multi_source_controller import MatchData
from ai_telegram_generator import AITelegramGenerator

logger = logging.getLogger(__name__)

class TelegramIntegration:
    """Интеграция Telegram с AI-системой"""
    
    def __init__(self, bot_token: str = None, channel_username: str = None):
        self.bot_token = bot_token or TELEGRAM_CONFIG['bot_token']
        self.channel_username = channel_username or TELEGRAM_CONFIG['channel_username']
        
        self.telegram_manager = TelegramChannelManager(self.bot_token, self.channel_username)
        self.ai_generator = AITelegramGenerator()
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def send_ai_recommendations(self, recommendations: List[MatchData]) -> bool:
        """
        Отправляет AI-рекомендации в Telegram канал
        """
        try:
            if not recommendations:
                self.logger.warning("Нет рекомендаций для отправки")
                return False
            
            # Генерируем AI-отчет
            self.logger.info(f"Генерация AI-отчета для {len(recommendations)} рекомендаций...")
            ai_report = self.ai_generator.generate_ai_telegram_report(recommendations)
            
            # Отправляем в канал
            self.logger.info("Отправка AI-отчета в Telegram канал...")
            success = self.telegram_manager.send_ai_report(ai_report)
            
            if success:
                self.logger.info("✅ AI-рекомендации успешно отправлены в канал")
            else:
                self.logger.error("❌ Не удалось отправить рекомендации в канал")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Ошибка при отправке рекомендаций: {e}")
            return False
    
    def send_startup_message(self) -> bool:
        """
        Отправляет сообщение о запуске системы
        """
        startup_message = """
🚀 <b>TrueLiveBet AI запущен!</b>

🤖 Система искусственного интеллекта для анализа live-ставок активирована
⏰ Время запуска: <i>{}</i>

📊 <b>Возможности системы:</b>
• AI-анализ всех live-матчей
• Умные рекомендации с обоснованиями
• Мульти-источниковый сбор данных
• Автоматическая генерация отчетов

🎯 <b>Поддерживаемые виды спорта:</b>
⚽ Футбол | 🎾 Теннис | 🏓 Настольный теннис | 🤾 Гандбол

💎 <b>TrueLiveBet AI – Умные ставки с искусственным интеллектом!</b>
        """.format(datetime.now().strftime("%H:%M МСК, %d.%m.%Y"))
        
        return self.telegram_manager.bot.send_message(startup_message)
    
    def send_error_message(self, error_message: str) -> bool:
        """
        Отправляет сообщение об ошибке
        """
        error_text = f"""
⚠️ <b>Ошибка в системе TrueLiveBet AI</b>

❌ <b>Описание:</b> {error_message}
⏰ <b>Время:</b> <i>{datetime.now().strftime("%H:%M МСК, %d.%m.%Y")}</i>

🔧 <b>Действие:</b> Проверьте логи системы

💎 <b>TrueLiveBet AI</b>
        """
        
        return self.telegram_manager.bot.send_message(error_text)
    
    def send_no_recommendations_message(self) -> bool:
        """
        Отправляет сообщение когда нет рекомендаций
        """
        no_recs_message = """
📊 <b>TrueLiveBet AI - Анализ завершен</b>

🔍 <b>Результат:</b> Нет подходящих матчей для рекомендаций
⏰ <b>Время:</b> <i>{}</i>

💡 <b>Причина:</b> Все найденные матчи не соответствуют критериям AI-анализа

🎯 <b>Следующий анализ:</b> Через 50 минут

💎 <b>TrueLiveBet AI – Умные ставки с искусственным интеллектом!</b>
        """.format(datetime.now().strftime("%H:%M МСК, %d.%m.%Y"))
        
        return self.telegram_manager.bot.send_message(no_recs_message)
    
    def test_connection(self) -> bool:
        """
        Тестирует подключение к Telegram
        """
        try:
            self.logger.info("Тестирование подключения к Telegram...")
            
            # Тестируем бота
            if not self.telegram_manager.bot.test_connection():
                self.logger.error("Не удалось подключиться к боту")
                return False
            
            # Отправляем тестовое сообщение
            if not self.telegram_manager.send_test_message():
                self.logger.error("Не удалось отправить тестовое сообщение")
                return False
            
            self.logger.info("✅ Telegram подключение работает корректно")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при тестировании Telegram: {e}")
            return False
    
    def send_formatted_report(self, formatted_report: str) -> bool:
        """Отправляет готовый отформатированный отчет в Telegram"""
        try:
            self.logger.info("Отправка отформатированного отчета в Telegram канал...")
            success = self.telegram_manager.send_ai_report(formatted_report)
            
            if success:
                self.logger.info("✅ Отформатированный отчет успешно отправлен")
            else:
                self.logger.error("❌ Не удалось отправить отформатированный отчет")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Ошибка отправки отформатированного отчета: {e}")
            return False

def test_telegram_integration():
    """Тестирует интеграцию с Telegram"""
    logger = logging.getLogger(__name__)
    
    try:
        # Создаем интеграцию
        telegram_integration = TelegramIntegration()
        
        # Тестируем подключение
        if telegram_integration.test_connection():
            logger.info("✅ Telegram интеграция работает корректно")
            
            # Тестируем отправку сообщения о запуске
            if telegram_integration.send_startup_message():
                logger.info("✅ Сообщение о запуске отправлено")
            else:
                logger.error("❌ Не удалось отправить сообщение о запуске")
                
        else:
            logger.error("❌ Telegram интеграция не работает")
            
    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании интеграции: {e}")

if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Тестируем интеграцию
    test_telegram_integration()