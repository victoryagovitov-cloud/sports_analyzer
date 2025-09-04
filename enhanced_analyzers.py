"""
Улучшенные анализаторы для работы с мульти-источниковым контроллером
"""

import logging
from typing import Optional
from multi_source_controller import MatchData
from fuzzy_matcher import FuzzyMatcher

logger = logging.getLogger(__name__)

class EnhancedFootballAnalyzer:
    def __init__(self):
        self.fuzzy_matcher = FuzzyMatcher()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze_match(self, match: MatchData) -> Optional[MatchData]:
        """Анализ футбольного матча"""
        try:
            # Проверяем, что это не ничейный счет
            if ':' not in match.score:
                return None
            
            home_score, away_score = map(int, match.score.split(':'))
            
            # Пропускаем ничейные счета
            if home_score == away_score:
                return None
            
            # Определяем, кто ведет
            if home_score > away_score:
                leading_team = match.team1
                trailing_team = match.team2
                is_home_leading = True
            else:
                leading_team = match.team2
                trailing_team = match.team1
                is_home_leading = False
            
            # Простой анализ: считаем, что команда с большим счетом - фаворит
            # В реальной системе здесь был бы анализ статистики
            probability = 0.85  # Фиксированная вероятность для демонстрации
            
            if probability > 0.8:
                recommendation_value = "П1" if is_home_leading else "П2"
                justification = f"Команда {leading_team} ведет {match.score} на {match.minute} минуте"
                
                match.probability = probability
                match.recommendation_type = "win"
                match.recommendation_value = recommendation_value
                match.justification = justification
                
                self.logger.info(f"Рекомендация для {match.team1} - {match.team2}: {recommendation_value}")
                return match
            
        except Exception as e:
            self.logger.error(f"Ошибка при анализе матча {match.team1} - {match.team2}: {e}")
        
        return None

class EnhancedTennisAnalyzer:
    def __init__(self):
        self.fuzzy_matcher = FuzzyMatcher()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze_match(self, match: MatchData) -> Optional[MatchData]:
        """Анализ теннисного матча"""
        try:
            # Проверяем формат счета
            if ':' not in match.score:
                return None
            
            home_score, away_score = match.score.split(':')
            
            # Простой анализ: если одна из сторон ведет 1-0 или больше
            try:
                home_sets = int(home_score)
                away_sets = int(away_score)
            except ValueError:
                return None
            
            if home_sets == away_sets:
                return None
            
            if home_sets > away_sets:
                leading_player = match.team1
                trailing_player = match.team2
                is_home_leading = True
            else:
                leading_player = match.team2
                trailing_player = match.team1
                is_home_leading = False
            
            # Простой анализ: считаем, что игрок с большим счетом - фаворит
            probability = 0.85  # Фиксированная вероятность для демонстрации
            
            if probability > 0.8:
                recommendation_value = f"Победа {leading_player}"
                justification = f"Игрок {leading_player} ведет {match.score} по сетам"
                
                match.probability = probability
                match.recommendation_type = "win"
                match.recommendation_value = recommendation_value
                match.justification = justification
                
                self.logger.info(f"Рекомендация для {match.team1} - {match.team2}: {recommendation_value}")
                return match
            
        except Exception as e:
            self.logger.error(f"Ошибка при анализе матча {match.team1} - {match.team2}: {e}")
        
        return None

class EnhancedTableTennisAnalyzer:
    def __init__(self):
        self.fuzzy_matcher = FuzzyMatcher()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze_match(self, match: MatchData) -> Optional[MatchData]:
        """Анализ матча по настольному теннису"""
        try:
            # Проверяем формат счета
            if ':' not in match.score:
                return None
            
            home_score, away_score = match.score.split(':')
            
            # Простой анализ: если одна из сторон ведет 1-0 или 2-0
            try:
                home_sets = int(home_score)
                away_sets = int(away_score)
            except ValueError:
                return None
            
            if home_sets == away_sets:
                return None
            
            if home_sets > away_sets:
                leading_player = match.team1
                trailing_player = match.team2
                is_home_leading = True
            else:
                leading_player = match.team2
                trailing_player = match.team1
                is_home_leading = False
            
            # Простой анализ: считаем, что игрок с большим счетом - фаворит
            probability = 0.85  # Фиксированная вероятность для демонстрации
            
            if probability > 0.8:
                recommendation_value = f"Победа {leading_player}"
                justification = f"Игрок {leading_player} ведет {match.score} по сетам"
                
                match.probability = probability
                match.recommendation_type = "win"
                match.recommendation_value = recommendation_value
                match.justification = justification
                
                self.logger.info(f"Рекомендация для {match.team1} - {match.team2}: {recommendation_value}")
                return match
            
        except Exception as e:
            self.logger.error(f"Ошибка при анализе матча {match.team1} - {match.team2}: {e}")
        
        return None

class EnhancedHandballAnalyzer:
    def __init__(self):
        self.fuzzy_matcher = FuzzyMatcher()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze_match(self, match: MatchData) -> Optional[MatchData]:
        """Анализ гандбольного матча"""
        try:
            # Проверяем формат счета
            if ':' not in match.score:
                return None
            
            home_score, away_score = map(int, match.score.split(':'))
            
            # Пропускаем ничейные счета
            if home_score == away_score:
                return None
            
            # Проверяем разрыв в счете (должен быть >= 5 голов)
            score_diff = abs(home_score - away_score)
            if score_diff < 5:
                return None
            
            if home_score > away_score:
                leading_team = match.team1
                trailing_team = match.team2
                is_home_leading = True
            else:
                leading_team = match.team2
                trailing_team = match.team1
                is_home_leading = False
            
            # Простой анализ: считаем, что команда с большим счетом - фаворит
            probability = 0.85  # Фиксированная вероятность для демонстрации
            
            if probability > 0.8:
                recommendation_value = "П1" if is_home_leading else "П2"
                justification = f"Команда {leading_team} ведет {match.score} с разрывом {score_diff} голов"
                
                match.probability = probability
                match.recommendation_type = "win"
                match.recommendation_value = recommendation_value
                match.justification = justification
                
                self.logger.info(f"Рекомендация для {match.team1} - {match.team2}: {recommendation_value}")
                return match
            
        except Exception as e:
            self.logger.error(f"Ошибка при анализе матча {match.team1} - {match.team2}: {e}")
        
        return None