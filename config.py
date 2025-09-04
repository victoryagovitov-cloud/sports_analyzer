"""
Конфигурация для анализа live-ставок
"""

# URL-адреса сайтов для HTTP-запросов
HTTP_URLS = {
    'winline': {
        'football': 'https://winline.ru/now/football/',
        'tennis': 'https://winline.ru/now/tennis/',
        'table_tennis': 'https://winline.ru/now/table-tennis/',
        'handball': 'https://winline.ru/now/handball/'
    },
    'betboom': {
        'football': 'https://betboom.ru/sport/football?type=live',
        'tennis': 'https://betboom.ru/sport/tennis?type=live',
        'table_tennis': 'https://betboom.ru/sport/table-tennis?type=live',
        'handball': 'https://betboom.ru/sport/handball?type=live'
    },
    'baltbet': {
        'football': 'https://baltbet.ru/live/football',
        'tennis': 'https://baltbet.ru/live/tennis',
        'table_tennis': 'https://baltbet.ru/live/table-tennis',
        'handball': 'https://baltbet.ru/live/handball'
    },
    'betzona': {
        'football': 'https://betzona.ru/live-futbol.html',
        'tennis': 'https://betzona.ru/live-tennis.html',
        'table_tennis': 'https://betzona.ru/live-tennis.html',  # Используем теннис, но фильтруем по типу
        'handball': 'https://betzona.ru/live-gandball.html'
    }
}

# Для обратной совместимости
BETBOOM_URLS = HTTP_URLS['betboom']
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