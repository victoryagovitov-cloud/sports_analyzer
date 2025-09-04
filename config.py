"""
Конфигурация для анализа live-ставок
"""

# URL-адреса сайтов
BETBOOM_URLS = {
    'football': 'https://betboom.ru/sport/football?type=live',
    'tennis': 'https://betboom.ru/sport/tennis?type=live',
    'table_tennis': 'https://betboom.ru/sport/table-tennis?type=live',
    'handball': 'https://betboom.ru/sport/handball?type=live'
}

SCORES24_URLS = {
    'football': 'https://scores24.live/ru/soccer?matchesFilter=live',
    'tennis': 'https://scores24.live/ru/tennis?matchesFilter=live',
    'table_tennis': 'https://scores24.live/ru/table-tennis?matchesFilter=live',
    'handball': 'https://scores24.live/ru/handball'
}

# Настройки анализа
ANALYSIS_SETTINGS = {
    'cycle_interval_minutes': 50,
    'fuzzy_match_threshold': 70,  # Минимальный процент совпадения для fuzzy matching
    'favorite_probability_threshold': 80,  # Минимальная вероятность победы фаворита
    'handball_goal_difference': 5,  # Минимальная разница в голаx для гандбола
    'handball_analysis_minute_start': 10,  # Начало анализа тоталов (минута)
    'handball_analysis_minute_end': 45,  # Конец анализа тоталов (минута)
    'handball_total_margin': 4  # Отступ для расчета тоталов
}

# Селекторы для парсинга Betboom
BETBOOM_SELECTORS = {
    'match_container': '.match-item',
    'team_names': '.team-name',
    'score': '.score',
    'minute': '.minute',
    'coefficient': '.coefficient',
    'locked': '.locked'
}

# Селекторы для парсинга Scores24
SCORES24_SELECTORS = {
    'match_container': '.match-row',
    'team_names': '.team-name',
    'score': '.score',
    'statistics': '.statistics'
}