"""
Telegram Bot для отправки AI-рекомендаций в канал
"""

import logging
import requests
import json
from typing import Optional, Dict, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class TelegramBot:
    """Telegram Bot для отправки рекомендаций в канал"""
    
    def __init__(self, bot_token: str, channel_id: str):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """
        Отправляет сообщение в канал
        """
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.channel_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True
            }
            
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get("ok"):
                self.logger.info("Сообщение успешно отправлено в канал")
                return True
            else:
                self.logger.error(f"Ошибка отправки: {result.get('description')}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка сети при отправке сообщения: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при отправке сообщения: {e}")
            return False
    
    def send_photo(self, photo_path: str, caption: str = "", parse_mode: str = "HTML") -> bool:
        """
        Отправляет фото в канал
        """
        try:
            url = f"{self.base_url}/sendPhoto"
            
            with open(photo_path, 'rb') as photo_file:
                files = {"photo": photo_file}
                data = {
                    "chat_id": self.channel_id,
                    "caption": caption,
                    "parse_mode": parse_mode
                }
                
                response = requests.post(url, files=files, data=data, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                if result.get("ok"):
                    self.logger.info("Фото успешно отправлено в канал")
                    return True
                else:
                    self.logger.error(f"Ошибка отправки фото: {result.get('description')}")
                    return False
                    
        except FileNotFoundError:
            self.logger.error(f"Файл фото не найден: {photo_path}")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка сети при отправке фото: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при отправке фото: {e}")
            return False
    
    def get_bot_info(self) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о боте
        """
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("ok"):
                return result.get("result")
            else:
                self.logger.error(f"Ошибка получения информации о боте: {result.get('description')}")
                return None
                
        except Exception as e:
            self.logger.error(f"Ошибка при получении информации о боте: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Тестирует соединение с ботом
        """
        try:
            bot_info = self.get_bot_info()
            if bot_info:
                self.logger.info(f"Бот подключен: @{bot_info.get('username')} ({bot_info.get('first_name')})")
                return True
            else:
                self.logger.error("Не удалось получить информацию о боте")
                return False
        except Exception as e:
            self.logger.error(f"Ошибка тестирования соединения: {e}")
            return False

class TelegramChannelManager:
    """Менеджер для работы с Telegram каналом"""
    
    def __init__(self, bot_token: str, channel_username: str):
        self.bot_token = bot_token
        self.channel_username = channel_username
        self.bot = TelegramBot(bot_token, channel_username)
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def send_ai_report(self, report_html: str) -> bool:
        """
        Отправляет AI-отчет в канал
        """
        try:
            # Очищаем HTML теги для отправки
            clean_text = self._clean_html_for_telegram(report_html)
            
            # Отправляем сообщение
            success = self.bot.send_message(clean_text)
            
            if success:
                self.logger.info("AI-отчет успешно отправлен в канал")
            else:
                self.logger.error("Не удалось отправить AI-отчет в канал")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Ошибка при отправке AI-отчета: {e}")
            return False
    
    def send_test_message(self) -> bool:
        """
        Отправляет тестовое сообщение в канал
        """
        test_message = """
🤖 <b>TrueLiveBet AI - Тест подключения</b>

✅ Бот успешно подключен к каналу!
⏰ Время: <i>{}</i>

🚀 Система готова к отправке AI-рекомендаций!

💎 <b>TrueLiveBet AI – Умные ставки с искусственным интеллектом!</b>
        """.format(datetime.now().strftime("%H:%M МСК, %d.%m.%Y"))
        
        return self.bot.send_message(test_message)
    
    def _clean_html_for_telegram(self, html_text: str) -> str:
        """
        Очищает HTML для корректного отображения в Telegram
        """
        # Telegram поддерживает ограниченный набор HTML тегов
        # Оставляем только поддерживаемые теги
        import re
        
        # Удаляем неподдерживаемые теги
        clean_text = re.sub(r'<br\s*/?>', '\n', html_text)
        clean_text = re.sub(r'<div[^>]*>', '\n', clean_text)
        clean_text = re.sub(r'</div>', '', clean_text)
        clean_text = re.sub(r'<span[^>]*>', '', clean_text)
        clean_text = re.sub(r'</span>', '', clean_text)
        
        # Очищаем лишние переносы строк
        clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)
        clean_text = clean_text.strip()
        
        return clean_text

# Конфигурация для вашего канала
TELEGRAM_CONFIG = {
    'bot_token': '7824400107:AAGZqPdS0E0N3HsYpD8TW9m8c-bapFd-RHk',
    'channel_username': '@truelivebet'  # или используйте ID канала
}

def test_telegram_connection():
    """Тестирует подключение к Telegram"""
    logger = logging.getLogger(__name__)
    
    try:
        manager = TelegramChannelManager(
            TELEGRAM_CONFIG['bot_token'],
            TELEGRAM_CONFIG['channel_username']
        )
        
        # Тестируем соединение
        if manager.bot.test_connection():
            logger.info("✅ Соединение с Telegram ботом установлено")
            
            # Отправляем тестовое сообщение
            if manager.send_test_message():
                logger.info("✅ Тестовое сообщение отправлено в канал")
                return True
            else:
                logger.error("❌ Не удалось отправить тестовое сообщение")
                return False
        else:
            logger.error("❌ Не удалось установить соединение с ботом")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании Telegram: {e}")
        return False

if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Тестируем подключение
    test_telegram_connection()