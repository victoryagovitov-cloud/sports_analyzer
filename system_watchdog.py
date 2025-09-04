#!/usr/bin/env python3
"""
Модуль системного мониторинга (watchdog) для предотвращения зависания
"""

import time
import threading
import logging
import psutil
from datetime import datetime, timedelta
from config import ANALYSIS_SETTINGS

logger = logging.getLogger(__name__)

class SystemWatchdog:
    """Системный watchdog для мониторинга работы приложения"""
    
    def __init__(self):
        self.is_running = False
        self.last_heartbeat = datetime.now()
        self.watchdog_thread = None
        self.max_memory_percent = ANALYSIS_SETTINGS['max_memory_usage_percent']
        self.check_interval = ANALYSIS_SETTINGS['watchdog_interval_seconds']
        
    def start(self):
        """Запуск watchdog"""
        if self.is_running:
            logger.warning("Watchdog уже запущен")
            return
            
        logger.info("🐕 Запуск системного watchdog")
        self.is_running = True
        self.last_heartbeat = datetime.now()
        
        self.watchdog_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.watchdog_thread.start()
        
    def stop(self):
        """Остановка watchdog"""
        logger.info("🛑 Остановка системного watchdog")
        self.is_running = False
        if self.watchdog_thread:
            self.watchdog_thread.join(timeout=5)
    
    def heartbeat(self):
        """Обновление heartbeat - система работает"""
        self.last_heartbeat = datetime.now()
        
    def _monitor_loop(self):
        """Основной цикл мониторинга"""
        logger.info(f"Watchdog запущен, интервал проверки: {self.check_interval} сек")
        
        while self.is_running:
            try:
                self._check_system_health()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Ошибка в watchdog: {e}")
                time.sleep(self.check_interval)
    
    def _check_system_health(self):
        """Проверка состояния системы"""
        # Проверка heartbeat
        time_since_heartbeat = datetime.now() - self.last_heartbeat
        if time_since_heartbeat > timedelta(minutes=10):
            logger.warning(f"⚠️  Нет heartbeat уже {time_since_heartbeat}")
            
        # Проверка использования памяти
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > self.max_memory_percent:
            logger.warning(f"⚠️  Высокое потребление памяти: {memory_percent}%")
            
        # Проверка использования CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            logger.warning(f"⚠️  Высокая загрузка CPU: {cpu_percent}%")
            
        # Проверка свободного места на диске
        disk_usage = psutil.disk_usage('/')
        disk_percent = (disk_usage.used / disk_usage.total) * 100
        if disk_percent > 90:
            logger.warning(f"⚠️  Мало свободного места на диске: {disk_percent}%")
            
        # Логируем состояние каждые 10 минут
        if datetime.now().minute % 10 == 0 and datetime.now().second < self.check_interval:
            logger.info(f"💚 Система работает нормально - CPU: {cpu_percent}%, RAM: {memory_percent}%, Диск: {disk_percent:.1f}%")

class AnalysisTimeoutManager:
    """Менеджер таймаутов для анализа"""
    
    def __init__(self, timeout_seconds=300):
        self.timeout_seconds = timeout_seconds
        self.start_time = None
        self.is_running = False
        
    def start_analysis(self):
        """Начало анализа"""
        self.start_time = time.time()
        self.is_running = True
        logger.info(f"⏱️  Начат анализ с таймаутом {self.timeout_seconds} сек")
        
    def check_timeout(self):
        """Проверка таймаута"""
        if not self.is_running or not self.start_time:
            return False
            
        elapsed = time.time() - self.start_time
        if elapsed > self.timeout_seconds:
            logger.error(f"⏰ ТАЙМАУТ: Анализ превысил {self.timeout_seconds} сек (прошло {elapsed:.1f} сек)")
            return True
        return False
        
    def finish_analysis(self):
        """Завершение анализа"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            logger.info(f"✅ Анализ завершен за {elapsed:.1f} сек")
        self.is_running = False
        self.start_time = None

class RetryManager:
    """Менеджер повторных попыток"""
    
    def __init__(self, max_retries=3, delay_seconds=5):
        self.max_retries = max_retries
        self.delay_seconds = delay_seconds
        
    def execute_with_retry(self, func, operation_name="операция"):
        """Выполнение функции с повторными попытками"""
        for attempt in range(self.max_retries):
            try:
                result = func()
                if attempt > 0:
                    logger.info(f"✅ {operation_name} выполнена успешно с {attempt + 1} попытки")
                return result
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"⚠️  {operation_name} неудачна (попытка {attempt + 1}/{self.max_retries}): {e}")
                    logger.info(f"⏳ Ожидание {self.delay_seconds} сек перед повтором...")
                    time.sleep(self.delay_seconds)
                else:
                    logger.error(f"❌ {operation_name} не удалась после {self.max_retries} попыток: {e}")
                    raise e

# Глобальный экземпляр watchdog
system_watchdog = SystemWatchdog()