#!/usr/bin/env python3
"""
Модуль для работы с московским временем
"""

from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

# Московская временная зона (UTC+3)
MOSCOW_TZ = timezone(timedelta(hours=3))

def get_moscow_time() -> datetime:
    """Получает текущее московское время"""
    return datetime.now(MOSCOW_TZ)

def format_moscow_time_for_telegram() -> str:
    """Форматирует московское время для Telegram отчетов"""
    moscow_time = get_moscow_time()
    return moscow_time.strftime("%H:%M МСК, %d.%m.%Y")

def format_moscow_time_for_logs() -> str:
    """Форматирует московское время для логов"""
    moscow_time = get_moscow_time()
    return moscow_time.strftime("%Y-%m-%d %H:%M:%S МСК")

def format_moscow_time_for_filename() -> str:
    """Форматирует московское время для имен файлов"""
    moscow_time = get_moscow_time()
    return moscow_time.strftime("%Y%m%d_%H%M%S")

def is_match_still_live(match_minute: str, max_duration_minutes: int = 90) -> bool:
    """
    Проверяет, идет ли еще матч (не завершился ли)
    
    Args:
        match_minute: Минута матча (например, "67'", "75′")
        max_duration_minutes: Максимальная продолжительность матча
    
    Returns:
        bool: True если матч еще идет, False если завершился
    """
    try:
        # Извлекаем число из строки минуты
        minute_clean = match_minute.replace("'", "").replace("′", "").replace("'", "")
        if not minute_clean.isdigit():
            return True  # Если не можем определить - считаем что идет
        
        minute = int(minute_clean)
        
        # Проверяем, не превышает ли время максимальную продолжительность
        if minute > max_duration_minutes + 5:  # +5 минут на добавленное время
            logger.warning(f"🏁 Матч на {minute} минуте завершен (макс: {max_duration_minutes}+5)")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка проверки времени матча: {e}")
        return True  # При ошибке считаем что матч идет

def filter_live_matches_by_time(matches, sport_type: str = 'football'):
    """
    Фильтрует матчи, исключая завершившиеся
    
    Args:
        matches: Список матчей
        sport_type: Тип спорта для определения максимальной продолжительности
    
    Returns:
        Список активных матчей
    """
    # Максимальная продолжительность для разных видов спорта
    max_durations = {
        'football': 90,      # 90 минут + добавленное время
        'tennis': 999,       # Теннис может длиться очень долго
        'table_tennis': 999, # Настольный теннис тоже
        'handball': 60       # 60 минут + добавленное время
    }
    
    max_duration = max_durations.get(sport_type, 90)
    active_matches = []
    
    for match in matches:
        minute_str = getattr(match, 'minute', '0')
        
        if is_match_still_live(minute_str, max_duration):
            active_matches.append(match)
        else:
            logger.info(f"🏁 Исключаем завершившийся матч: {match.team1} vs {match.team2} ({minute_str})")
    
    if len(active_matches) < len(matches):
        logger.info(f"📊 Отфильтровано {len(matches) - len(active_matches)} завершившихся матчей")
    
    return active_matches

def log_moscow_time(message: str):
    """Логирует сообщение с московским временем"""
    moscow_time_str = format_moscow_time_for_logs()
    logger.info(f"[{moscow_time_str}] {message}")

def get_time_until_next_analysis(interval_minutes: int = 45) -> str:
    """Рассчитывает время до следующего анализа"""
    try:
        moscow_time = get_moscow_time()
        current_minute = moscow_time.minute
        
        # Рассчитываем следующий интервал
        minutes_until_next = interval_minutes - (current_minute % interval_minutes)
        if minutes_until_next == interval_minutes:
            minutes_until_next = 0
        
        next_analysis_time = moscow_time + timedelta(minutes=minutes_until_next)
        return next_analysis_time.strftime("%H:%M МСК")
        
    except Exception:
        return "в ближайшее время"