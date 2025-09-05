#!/usr/bin/env python3
"""
Планировщик ежедневной статистики в 23:50 МСК
"""

import schedule
import logging
from datetime import datetime
from ml_tracking_system import ml_tracker
from telegram_integration import TelegramIntegration
from moscow_time import get_moscow_time

logger = logging.getLogger(__name__)

class DailyStatsScheduler:
    """Планировщик ежедневной статистики"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.telegram_integration = TelegramIntegration()
        
    def setup_daily_stats_job(self):
        """Настраивает ежедневную отправку статистики в 23:50 МСК"""
        
        # Планируем отправку каждый день в 23:50
        schedule.every().day.at("23:50").do(self.send_daily_stats)
        
        self.logger.info("📊 Запланирована ежедневная статистика в 23:50 МСК")
    
    def send_daily_stats(self):
        """Отправляет дневную статистику в Telegram"""
        try:
            moscow_time = get_moscow_time()
            self.logger.info(f"📊 Генерация дневной статистики в {moscow_time.strftime('%H:%M МСК')}")
            
            # Генерируем статистику
            stats = ml_tracker.generate_daily_stats()
            
            # Форматируем для Telegram
            stats_message = ml_tracker.format_daily_stats_for_telegram(stats)
            
            # Отправляем в канал
            success = self.telegram_integration.send_formatted_report(stats_message)
            
            if success:
                self.logger.info("✅ Дневная статистика отправлена в Telegram")
            else:
                self.logger.error("❌ Не удалось отправить дневную статистику")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Ошибка отправки дневной статистики: {e}")
            return False
    
    def check_and_run_pending_stats(self):
        """Проверяет и выполняет запланированные задачи статистики"""
        try:
            schedule.run_pending()
        except Exception as e:
            self.logger.error(f"Ошибка выполнения запланированных задач: {e}")

# Глобальный экземпляр
daily_stats_scheduler = DailyStatsScheduler()