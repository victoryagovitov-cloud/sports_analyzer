"""
Модуль для fuzzy matching названий команд и игроков
"""

from fuzzywuzzy import fuzz, process
import re


class FuzzyMatcher:
    """Класс для сопоставления названий команд/игроков между сайтами"""
    
    def __init__(self, threshold=70):
        self.threshold = threshold
    
    def normalize_name(self, name):
        """Нормализация названия для лучшего сопоставления"""
        if not name:
            return ""
        
        # Приводим к нижнему регистру
        normalized = name.lower().strip()
        
        # Убираем лишние пробелы
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Убираем общие слова и аббревиатуры
        common_words = [
            'fc', 'фк', 'club', 'клуб', 'team', 'команда',
            'united', 'юнайтед', 'city', 'сити', 'town', 'таун',
            'athletic', 'атлетико', 'sporting', 'спортинг',
            'real', 'реал', 'royal', 'роял', 'cf', 'кф'
        ]
        
        for word in common_words:
            normalized = normalized.replace(word, '')
        
        # Убираем знаки препинания
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        return normalized.strip()
    
    def extract_abbreviation(self, name):
        """Извлечение аббревиатуры из названия"""
        if not name:
            return ""
        
        # Ищем аббревиатуры в скобках
        abbr_match = re.search(r'\(([^)]+)\)', name)
        if abbr_match:
            return abbr_match.group(1).strip()
        
        # Создаем аббревиатуру из первых букв слов
        words = name.split()
        if len(words) >= 2:
            return ''.join([word[0].upper() for word in words if word])
        
        return ""
    
    def match_teams(self, betboom_team, scores24_teams):
        """
        Сопоставление команд между Betboom и Scores24
        
        Args:
            betboom_team (str): Название команды с Betboom
            scores24_teams (list): Список команд с Scores24
            
        Returns:
            tuple: (matched_team, confidence) или (None, 0)
        """
        if not betboom_team or not scores24_teams:
            return None, 0
        
        # Нормализуем название с Betboom
        normalized_betboom = self.normalize_name(betboom_team)
        
        # Создаем список для поиска
        search_list = []
        for team in scores24_teams:
            normalized_team = self.normalize_name(team)
            abbr_team = self.extract_abbreviation(team)
            
            search_list.append((team, normalized_team))
            if abbr_team and abbr_team != normalized_team:
                search_list.append((team, abbr_team))
        
        # Ищем лучшее совпадение
        best_match = process.extractOne(
            normalized_betboom,
            [item[1] for item in search_list],
            scorer=fuzz.ratio
        )
        
        if best_match and best_match[1] >= self.threshold:
            # Находим оригинальное название команды
            for original, normalized in search_list:
                if normalized == best_match[0]:
                    return original, best_match[1]
        
        return None, 0
    
    def match_players(self, betboom_player, scores24_players):
        """
        Сопоставление игроков между Betboom и Scores24
        
        Args:
            betboom_player (str): Имя игрока с Betboom
            scores24_players (list): Список игроков с Scores24
            
        Returns:
            tuple: (matched_player, confidence) или (None, 0)
        """
        if not betboom_player or not scores24_players:
            return None, 0
        
        # Нормализуем имя с Betboom
        normalized_betboom = self.normalize_name(betboom_player)
        
        # Создаем список для поиска
        search_list = []
        for player in scores24_players:
            normalized_player = self.normalize_name(player)
            
            # Пробуем разные варианты имени
            search_list.append((player, normalized_player))
            
            # Пробуем только фамилию
            parts = normalized_player.split()
            if len(parts) > 1:
                search_list.append((player, parts[-1]))  # Фамилия
            
            # Пробуем только имя
            if len(parts) > 1:
                search_list.append((player, parts[0]))  # Имя
        
        # Ищем лучшее совпадение
        best_match = process.extractOne(
            normalized_betboom,
            [item[1] for item in search_list],
            scorer=fuzz.ratio
        )
        
        if best_match and best_match[1] >= self.threshold:
            # Находим оригинальное имя игрока
            for original, normalized in search_list:
                if normalized == best_match[0]:
                    return original, best_match[1]
        
        return None, 0
    
    def is_non_draw_score(self, score):
        """Проверка, что счет не ничейный"""
        if not score or ':' not in score:
            return False
        
        try:
            home, away = score.split(':')
            return int(home.strip()) != int(away.strip())
        except (ValueError, AttributeError):
            return False
    
    def is_tennis_first_set_lead(self, score):
        """Проверка, что в теннисе ведет первый сет или большой разрыв"""
        if not score:
            return False
        
        # Проверяем формат "1-0" или "2-0" по сетам
        if '-' in score:
            try:
                sets = score.split('-')
                if len(sets) >= 2:
                    first_set = sets[0].strip()
                    second_set = sets[1].strip()
                    
                    # Проверяем, что первый сет выигран
                    if first_set.isdigit() and second_set.isdigit():
                        return int(first_set) > int(second_set)
            except (ValueError, IndexError):
                pass
        
        return False
    
    def is_table_tennis_lead(self, score):
        """Проверка, что в настольном теннисе ведет 1:0 или 2:0"""
        if not score:
            return False
        
        # Проверяем формат "1:0" или "2:0" по сетам
        if ':' in score:
            try:
                sets = score.split(':')
                if len(sets) >= 2:
                    first_set = sets[0].strip()
                    second_set = sets[1].strip()
                    
                    if first_set.isdigit() and second_set.isdigit():
                        first = int(first_set)
                        second = int(second_set)
                        return (first == 1 and second == 0) or (first == 2 and second == 0)
            except (ValueError, IndexError):
                pass
        
        return False
    
    def is_handball_goal_difference(self, score, min_difference=5):
        """Проверка разницы в голаx для гандбола"""
        if not score or ':' not in score:
            return False
        
        try:
            home, away = score.split(':')
            home_goals = int(home.strip())
            away_goals = int(away.strip())
            return abs(home_goals - away_goals) >= min_difference
        except (ValueError, AttributeError):
            return False