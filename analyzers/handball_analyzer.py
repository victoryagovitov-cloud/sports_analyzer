"""
Модуль анализа гандбольных матчей
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from browser_controller import BrowserController, MatchData
from fuzzy_matcher import FuzzyMatcher
from config import BETBOOM_URLS, SCORES24_URLS, ANALYSIS_SETTINGS


@dataclass
class HandballRecommendation:
    """Рекомендация по гандбольному матчу"""
    team1: str
    team2: str
    score: str
    minute: str
    bet_type: str
    coefficient: float
    justification: str
    predicted_total: Optional[int] = None
    recommendation_type: Optional[str] = None


class HandballAnalyzer:
    """Анализатор гандбольных матчей"""
    
    def __init__(self, browser_controller: BrowserController, fuzzy_matcher: FuzzyMatcher):
        self.browser = browser_controller
        self.fuzzy_matcher = fuzzy_matcher
        self.threshold = ANALYSIS_SETTINGS['favorite_probability_threshold']
        self.goal_difference = ANALYSIS_SETTINGS['handball_goal_difference']
        self.minute_start = ANALYSIS_SETTINGS['handball_analysis_minute_start']
        self.minute_end = ANALYSIS_SETTINGS['handball_analysis_minute_end']
        self.total_margin = ANALYSIS_SETTINGS['handball_total_margin']
    
    def analyze_handball_matches(self) -> List[HandballRecommendation]:
        """
        Анализ гандбольных матчей
        
        Returns:
            List[HandballRecommendation]: Список рекомендаций
        """
        recommendations = []
        
        try:
            # Переходим на страницу гандбола Betboom
            if not self.browser.navigate_to_page(BETBOOM_URLS['handball']):
                print("Ошибка перехода на страницу гандбола Betboom")
                return recommendations
            
            # Получаем матчи с Betboom
            betboom_matches = self.browser.find_matches('handball')
            print(f"Найдено {len(betboom_matches)} гандбольных матчей на Betboom")
            
            # Переходим на Scores24 для анализа статистики
            if not self.browser.navigate_to_page(SCORES24_URLS['handball']):
                print("Ошибка перехода на страницу гандбола Scores24")
                return recommendations
            
            # Получаем матчи с Scores24
            scores24_matches = self.browser.get_scores24_matches('handball')
            print(f"Найдено {len(scores24_matches)} гандбольных матчей на Scores24")
            
            # Анализируем каждый матч
            for match in betboom_matches:
                # Анализ прямых побед
                win_recommendation = self._analyze_win_match(match, scores24_matches)
                if win_recommendation:
                    recommendations.append(win_recommendation)
                
                # Анализ тоталов (только во 2-м тайме)
                total_recommendation = self._analyze_total_match(match, scores24_matches)
                if total_recommendation:
                    recommendations.append(total_recommendation)
            
        except Exception as e:
            print(f"Ошибка анализа гандбольных матчей: {e}")
        
        return recommendations
    
    def _analyze_win_match(self, betboom_match: MatchData, scores24_matches: List[Dict]) -> Optional[HandballRecommendation]:
        """
        Анализ матча на прямую победу
        
        Args:
            betboom_match (MatchData): Матч с Betboom
            scores24_matches (List[Dict]): Матчи с Scores24
            
        Returns:
            Optional[HandballRecommendation]: Рекомендация или None
        """
        try:
            # Проверяем разрыв в голаx
            if not self.fuzzy_matcher.is_handball_goal_difference(betboom_match.score, self.goal_difference):
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
            probability = self._analyze_handball_statistics(betboom_match, scores24_match)
            if probability < self.threshold:
                print(f"Низкая вероятность победы фаворита: {probability}%")
                return None
            
            # Определяем, кто ведет в счете
            leading_team = self._get_leading_team(betboom_match)
            if not leading_team:
                return None
            
            # Создаем обоснование
            justification = self._create_handball_justification(scores24_match, probability)
            
            # Определяем тип ставки
            bet_type = "П1" if leading_team == 1 else "П2"
            
            return HandballRecommendation(
                team1=betboom_match.team1,
                team2=betboom_match.team2,
                score=betboom_match.score,
                minute=betboom_match.minute,
                bet_type=bet_type,
                coefficient=betboom_match.coefficient,
                justification=justification,
                recommendation_type="win"
            )
            
        except Exception as e:
            print(f"Ошибка анализа матча на победу {betboom_match.team1} - {betboom_match.team2}: {e}")
            return None
    
    def _analyze_total_match(self, betboom_match: MatchData, scores24_matches: List[Dict]) -> Optional[HandballRecommendation]:
        """
        Анализ матча на тотал
        
        Args:
            betboom_match (MatchData): Матч с Betboom
            scores24_matches (List[Dict]): Матчи с Scores24
            
        Returns:
            Optional[HandballRecommendation]: Рекомендация или None
        """
        try:
            # Проверяем, что матч во 2-м тайме
            minute = self._extract_minute(betboom_match.minute)
            if not (self.minute_start <= minute <= self.minute_end):
                return None
            
            # Проверяем, что ставка не заблокирована
            if betboom_match.is_locked:
                return None
            
            # Рассчитываем тотал
            total_data = self.browser.calculate_handball_total(betboom_match.score, betboom_match.minute)
            if not total_data:
                return None
            
            # Создаем обоснование для тотала
            justification = self._create_total_justification(total_data)
            
            return HandballRecommendation(
                team1=betboom_match.team1,
                team2=betboom_match.team2,
                score=betboom_match.score,
                minute=betboom_match.minute,
                bet_type=total_data['recommendation'],
                coefficient=1.0,  # Коэффициент для тотала нужно получать отдельно
                justification=justification,
                predicted_total=total_data['predicted_total'],
                recommendation_type="total"
            )
            
        except Exception as e:
            print(f"Ошибка анализа тотала матча {betboom_match.team1} - {betboom_match.team2}: {e}")
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
            # Сопоставляем команды
            team1_match, confidence1 = self.fuzzy_matcher.match_teams(
                betboom_match.team1, 
                [scores24_match['team1']]
            )
            team2_match, confidence2 = self.fuzzy_matcher.match_teams(
                betboom_match.team2, 
                [scores24_match['team2']]
            )
            
            if team1_match and team2_match and confidence1 >= 70 and confidence2 >= 70:
                return scores24_match
        
        return None
    
    def _analyze_handball_statistics(self, betboom_match: MatchData, scores24_match: Dict) -> float:
        """
        Анализ гандбольной статистики
        
        Args:
            betboom_match (MatchData): Матч с Betboom
            scores24_match (Dict): Статистика с Scores24
            
        Returns:
            float: Вероятность победы фаворита
        """
        try:
            stats = scores24_match.get('statistics', {})
            
            # Анализируем форму команд
            form_team1 = stats.get('form_team1', '')
            form_team2 = stats.get('form_team2', '')
            
            # Анализируем позиции в таблице
            position_team1 = stats.get('position_team1', 10)
            position_team2 = stats.get('position_team2', 10)
            
            # Анализируем среднюю результативность
            avg_goals_team1 = stats.get('avg_goals_team1', 25)
            avg_goals_team2 = stats.get('avg_goals_team2', 25)
            
            # Определяем, кто ведет в счете
            leading_team = self._get_leading_team(betboom_match)
            if not leading_team:
                return 0
            
            # Рассчитываем вероятность на основе статистики
            probability = 50  # Базовая вероятность
            
            if leading_team == 1:
                # Команда 1 ведет
                if position_team1 < position_team2:
                    probability += 15  # Лучшая позиция в таблице
                
                if self._analyze_form(form_team1) > self._analyze_form(form_team2):
                    probability += 10  # Лучшая форма
                
                if avg_goals_team1 > avg_goals_team2:
                    probability += 5  # Лучшая результативность
                    
            else:
                # Команда 2 ведет
                if position_team2 < position_team1:
                    probability += 15
                
                if self._analyze_form(form_team2) > self._analyze_form(form_team1):
                    probability += 10
                
                if avg_goals_team2 > avg_goals_team1:
                    probability += 5
            
            # Учитываем разницу в счете
            goal_diff = self._get_goal_difference(betboom_match.score)
            if goal_diff >= 8:
                probability += 15  # Очень большой разрыв
            elif goal_diff >= 5:
                probability += 10  # Большой разрыв
            
            return min(probability, 95)  # Максимум 95%
            
        except Exception as e:
            print(f"Ошибка анализа статистики: {e}")
            return 0
    
    def _get_leading_team(self, match: MatchData) -> Optional[int]:
        """
        Определение команды, которая ведет в счете
        
        Args:
            match (MatchData): Данные матча
            
        Returns:
            Optional[int]: 1, 2 или None
        """
        try:
            if ':' not in match.score:
                return None
            
            home_goals, away_goals = match.score.split(':')
            home_goals = int(home_goals.strip())
            away_goals = int(away_goals.strip())
            
            if home_goals > away_goals:
                return 1
            elif away_goals > home_goals:
                return 2
            else:
                return None
                
        except (ValueError, AttributeError):
            return None
    
    def _get_goal_difference(self, score: str) -> int:
        """
        Получение разницы в голаx
        
        Args:
            score (str): Счет матча
            
        Returns:
            int: Разница в голаx
        """
        try:
            if ':' not in score:
                return 0
            
            home_goals, away_goals = score.split(':')
            home_goals = int(home_goals.strip())
            away_goals = int(away_goals.strip())
            
            return abs(home_goals - away_goals)
            
        except (ValueError, AttributeError):
            return 0
    
    def _extract_minute(self, minute_str: str) -> int:
        """
        Извлечение минуты из строки
        
        Args:
            minute_str (str): Строка с минутой (например, "45'")
            
        Returns:
            int: Минута матча
        """
        try:
            return int(minute_str.replace("'", "").strip())
        except (ValueError, AttributeError):
            return 0
    
    def _analyze_form(self, form: str) -> float:
        """
        Анализ формы команды
        
        Args:
            form (str): Форма команды (например, "WWLWW")
            
        Returns:
            float: Оценка формы (0-1)
        """
        if not form:
            return 0.5
        
        wins = form.count('W')
        draws = form.count('D')
        losses = form.count('L')
        total = len(form)
        
        if total == 0:
            return 0.5
        
        return (wins * 1.0 + draws * 0.5) / total
    
    def _create_handball_justification(self, scores24_match: Dict, probability: float) -> str:
        """
        Создание обоснования для гандбольной рекомендации на победу
        
        Args:
            scores24_match (Dict): Статистика матча
            probability (float): Вероятность победы
            
        Returns:
            str: Обоснование
        """
        stats = scores24_match.get('statistics', {})
        
        parts = []
        
        # Форма команд
        form_team1 = stats.get('form_team1', '')
        form_team2 = stats.get('form_team2', '')
        if form_team1 and form_team2:
            parts.append(f"форма: {form_team1} vs {form_team2}")
        
        # Позиции в таблице
        position_team1 = stats.get('position_team1')
        position_team2 = stats.get('position_team2')
        if position_team1 and position_team2:
            parts.append(f"позиции: {position_team1} vs {position_team2}")
        
        # Средняя результативность
        avg_goals_team1 = stats.get('avg_goals_team1')
        avg_goals_team2 = stats.get('avg_goals_team2')
        if avg_goals_team1 and avg_goals_team2:
            parts.append(f"средняя результативность: {avg_goals_team1} vs {avg_goals_team2}")
        
        # Вероятность
        parts.append(f"вероятность: {probability:.0f}%")
        
        return ", ".join(parts)
    
    def _create_total_justification(self, total_data: Dict) -> str:
        """
        Создание обоснования для рекомендации по тоталу
        
        Args:
            total_data (Dict): Данные расчета тотала
            
        Returns:
            str: Обоснование
        """
        parts = []
        
        # Прогнозный тотал
        if total_data.get('predicted_total'):
            parts.append(f"прогнозный тотал: {total_data['predicted_total']} голов")
        
        # Темп игры
        tempo = total_data.get('tempo', '')
        if tempo:
            total_goals = total_data.get('total_goals', 0)
            played_minutes = total_data.get('played_minutes', 0)
            parts.append(f"основание: {tempo} темп игры ({total_goals} голов за {played_minutes} минут)")
        
        return ", ".join(parts)