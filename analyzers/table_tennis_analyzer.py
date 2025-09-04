"""
Модуль анализа матчей настольного тенниса
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from browser_controller import BrowserController, MatchData
from fuzzy_matcher import FuzzyMatcher
from config import BETBOOM_URLS, SCORES24_URLS, ANALYSIS_SETTINGS


@dataclass
class TableTennisRecommendation:
    """Рекомендация по матчу настольного тенниса"""
    player1: str
    player2: str
    score: str
    bet_type: str
    coefficient: float
    justification: str


class TableTennisAnalyzer:
    """Анализатор матчей настольного тенниса"""
    
    def __init__(self, browser_controller: BrowserController, fuzzy_matcher: FuzzyMatcher):
        self.browser = browser_controller
        self.fuzzy_matcher = fuzzy_matcher
        self.threshold = ANALYSIS_SETTINGS['favorite_probability_threshold']
    
    def analyze_table_tennis_matches(self) -> List[TableTennisRecommendation]:
        """
        Анализ матчей настольного тенниса
        
        Returns:
            List[TableTennisRecommendation]: Список рекомендаций
        """
        recommendations = []
        
        try:
            # Переходим на страницу настольного тенниса Betboom
            if not self.browser.navigate_to_page(BETBOOM_URLS['table_tennis']):
                print("Ошибка перехода на страницу настольного тенниса Betboom")
                return recommendations
            
            # Получаем матчи с Betboom
            betboom_matches = self.browser.find_matches('table_tennis')
            print(f"Найдено {len(betboom_matches)} матчей настольного тенниса на Betboom")
            
            # Переходим на Scores24 для анализа статистики
            if not self.browser.navigate_to_page(SCORES24_URLS['table_tennis']):
                print("Ошибка перехода на страницу настольного тенниса Scores24")
                return recommendations
            
            # Получаем матчи с Scores24
            scores24_matches = self.browser.get_scores24_matches('table_tennis')
            print(f"Найдено {len(scores24_matches)} матчей настольного тенниса на Scores24")
            
            # Анализируем каждый матч
            for match in betboom_matches:
                recommendation = self._analyze_single_match(match, scores24_matches)
                if recommendation:
                    recommendations.append(recommendation)
            
        except Exception as e:
            print(f"Ошибка анализа матчей настольного тенниса: {e}")
        
        return recommendations
    
    def _analyze_single_match(self, betboom_match: MatchData, scores24_matches: List[Dict]) -> Optional[TableTennisRecommendation]:
        """
        Анализ одного матча настольного тенниса
        
        Args:
            betboom_match (MatchData): Матч с Betboom
            scores24_matches (List[Dict]): Матчи с Scores24
            
        Returns:
            Optional[TableTennisRecommendation]: Рекомендация или None
        """
        try:
            # Проверяем, что ведет 1:0 или 2:0 по сетам
            if not self.fuzzy_matcher.is_table_tennis_lead(betboom_match.score):
                return None
            
            # Проверяем, что ставка не заблокирована
            if betboom_match.is_locked:
                return None
            
            # Ищем соответствующий матч на Scores24
            scores24_match = self._find_matching_scores24_match(betboom_match, scores24_matches)
            if not scores24_match:
                print(f"Не найден соответствующий матч на Scores24: {betboom_match.team1} - {betboom_match.team2}")
                return None
            
            # Анализируем статистику
            probability = self._analyze_table_tennis_statistics(betboom_match, scores24_match)
            if probability < self.threshold:
                print(f"Низкая вероятность победы фаворита: {probability}%")
                return None
            
            # Определяем, кто ведет в счете
            leading_player = self._get_leading_player(betboom_match)
            if not leading_player:
                return None
            
            # Создаем обоснование
            justification = self._create_table_tennis_justification(scores24_match, probability)
            
            # Определяем тип ставки
            bet_type = f"Победа {betboom_match.team1}" if leading_player == 1 else f"Победа {betboom_match.team2}"
            
            return TableTennisRecommendation(
                player1=betboom_match.team1,
                player2=betboom_match.team2,
                score=betboom_match.score,
                bet_type=bet_type,
                coefficient=betboom_match.coefficient,
                justification=justification
            )
            
        except Exception as e:
            print(f"Ошибка анализа матча {betboom_match.team1} - {betboom_match.team2}: {e}")
            return None
    
    def _find_matching_scores24_match(self, betboom_match: MatchData, scores24_matches: List[Dict]) -> Optional[Dict]:
        """
        Поиск соответствующего матча на Scores24
        
        Args:
            betboom_match (MatchData): Матч с Betboom
            scores24_matches (List[Dict]): Матчи с Scores24
            
        Returns:
            Optional[Dict]: Соответствующий матч или None
        """
        for scores24_match in scores24_matches:
            # Сопоставляем игроков
            player1_match, confidence1 = self.fuzzy_matcher.match_players(
                betboom_match.team1, 
                [scores24_match['player1']]
            )
            player2_match, confidence2 = self.fuzzy_matcher.match_players(
                betboom_match.team2, 
                [scores24_match['player2']]
            )
            
            if player1_match and player2_match and confidence1 >= 70 and confidence2 >= 70:
                return scores24_match
        
        return None
    
    def _analyze_table_tennis_statistics(self, betboom_match: MatchData, scores24_match: Dict) -> float:
        """
        Анализ статистики настольного тенниса
        
        Args:
            betboom_match (MatchData): Матч с Betboom
            scores24_match (Dict): Статистика с Scores24
            
        Returns:
            float: Вероятность победы фаворита
        """
        try:
            stats = scores24_match.get('statistics', {})
            
            # Анализируем рейтинги игроков
            rating_player1 = stats.get('rating_player1', 100)
            rating_player2 = stats.get('rating_player2', 100)
            
            # Анализируем форму игроков
            form_player1 = stats.get('form_player1', '')
            form_player2 = stats.get('form_player2', '')
            
            # Определяем, кто ведет в счете
            leading_player = self._get_leading_player(betboom_match)
            if not leading_player:
                return 0
            
            # Рассчитываем вероятность на основе статистики
            probability = 50  # Базовая вероятность
            
            if leading_player == 1:
                # Игрок 1 ведет
                if rating_player1 < rating_player2:  # Лучший рейтинг (меньше = лучше)
                    probability += 25
                
                if self._analyze_form(form_player1) > self._analyze_form(form_player2):
                    probability += 15
                    
            else:
                # Игрок 2 ведет
                if rating_player2 < rating_player1:
                    probability += 25
                
                if self._analyze_form(form_player2) > self._analyze_form(form_player1):
                    probability += 15
            
            # Учитываем разрыв в счете
            set_lead = self._get_set_lead(betboom_match.score)
            if set_lead == 2:  # 2:0
                probability += 20  # Большой разрыв
            elif set_lead == 1:  # 1:0
                probability += 10  # Небольшой разрыв
            
            return min(probability, 95)  # Максимум 95%
            
        except Exception as e:
            print(f"Ошибка анализа статистики: {e}")
            return 0
    
    def _get_leading_player(self, match: MatchData) -> Optional[int]:
        """
        Определение игрока, который ведет в счете
        
        Args:
            match (MatchData): Данные матча
            
        Returns:
            Optional[int]: 1, 2 или None
        """
        try:
            if ':' not in match.score:
                return None
            
            sets = match.score.split(':')
            if len(sets) < 2:
                return None
            
            sets_won_1 = int(sets[0].strip())
            sets_won_2 = int(sets[1].strip())
            
            if sets_won_1 > sets_won_2:
                return 1
            elif sets_won_2 > sets_won_1:
                return 2
            else:
                return None
                
        except (ValueError, AttributeError, IndexError):
            return None
    
    def _get_set_lead(self, score: str) -> int:
        """
        Получение разрыва в сетах
        
        Args:
            score (str): Счет по сетам
            
        Returns:
            int: Разрыв в сетах
        """
        try:
            if ':' not in score:
                return 0
            
            sets = score.split(':')
            if len(sets) < 2:
                return 0
            
            sets_won_1 = int(sets[0].strip())
            sets_won_2 = int(sets[1].strip())
            
            return abs(sets_won_1 - sets_won_2)
            
        except (ValueError, AttributeError, IndexError):
            return 0
    
    def _analyze_form(self, form: str) -> float:
        """
        Анализ формы игрока
        
        Args:
            form (str): Форма игрока (например, "WWLWW")
            
        Returns:
            float: Оценка формы (0-1)
        """
        if not form:
            return 0.5
        
        wins = form.count('W')
        losses = form.count('L')
        total = len(form)
        
        if total == 0:
            return 0.5
        
        return wins / total
    
    def _create_table_tennis_justification(self, scores24_match: Dict, probability: float) -> str:
        """
        Создание обоснования для рекомендации по настольному теннису
        
        Args:
            scores24_match (Dict): Статистика матча
            probability (float): Вероятность победы
            
        Returns:
            str: Обоснование
        """
        stats = scores24_match.get('statistics', {})
        
        parts = []
        
        # Рейтинги игроков
        rating_player1 = stats.get('rating_player1')
        rating_player2 = stats.get('rating_player2')
        if rating_player1 and rating_player2:
            parts.append(f"рейтинги: {rating_player1} vs {rating_player2}")
        
        # Форма игроков
        form_player1 = stats.get('form_player1', '')
        form_player2 = stats.get('form_player2', '')
        if form_player1 and form_player2:
            parts.append(f"форма: {form_player1} vs {form_player2}")
        
        # Вероятность
        parts.append(f"вероятность: {probability:.0f}%")
        
        return ", ".join(parts)