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
    'cycle_interval_minutes': 45,  # Обновлено по новому промпту
    'fuzzy_match_threshold': 70,  # Минимальный процент совпадения для fuzzy matching
    'favorite_probability_threshold': 80,  # Минимальная вероятность победы фаворита
    'handball_goal_difference': 5,  # Минимальная разница в голаx для гандбола
    'handball_analysis_minute_start': 10,  # Начало анализа тоталов (минута)
    'handball_analysis_minute_end': 45,  # Конец анализа тоталов (минута)
    'handball_total_margin': 4,  # Отступ для расчета тоталов
    # Настройки таймаутов для предотвращения зависания
    'http_timeout_seconds': 30,  # Таймаут для HTTP-запросов
    'analysis_timeout_seconds': 300,  # Максимальное время анализа одного цикла (5 минут)
    'max_retries': 3,  # Максимальное количество повторных попыток
    'retry_delay_seconds': 5,  # Задержка между повторными попытками
    'watchdog_interval_seconds': 60,  # Интервал проверки watchdog (1 минута)
    'max_memory_usage_percent': 80,  # Максимальное использование памяти (%)
    # AI анализаторы (возврат к OpenAI GPT)
    'use_cursor_claude': False,  # Отключаем экспериментальный Claude
    'use_openai_gpt': True,      # Возвращаем OpenAI как основной анализатор
    'openai_model': 'gpt-4o-mini',  # Модель GPT для использования
    'openai_max_tokens': 2000,  # Максимальное количество токенов
    'openai_temperature': 0.1,  # Температура для более консистентных результатов
    
    # Новые критерии анализа по улучшенному промпту
    'football_time_window': (25, 75),  # Временное окно для футбола (25-75 минута)
    'football_table_position_diff': 5,  # Минимальная разница в таблице
    'football_form_wins_required': 3,  # Минимум побед в последних 5 играх
    'football_h2h_wins_required': 3,   # Минимум побед в личных встречах
    'football_max_coefficient': 2.20,  # Максимальный коэффициент
    
    'tennis_rating_diff': 20,          # Минимальная разница в рейтинге
    'tennis_form_wins_required': 4,    # Минимум побед в последних 5 матчах
    'tennis_h2h_wins_required': 3,     # Минимум побед в H2H
    'tennis_first_serve_min': 65,      # Минимальный процент первых подач
    'tennis_max_coefficient': 1.70,    # Максимальный коэффициент
    
    'handball_goal_diff_min': 4,       # Минимальная разница в голах
    'handball_second_half_start': 30,  # Начало второй половины
    'handball_table_position_diff': 5, # Минимальная разница в таблице
    'handball_avg_goals_min': 30,      # Минимальная средняя результативность
    'handball_max_coefficient': 1.45   # Максимальный коэффициент
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