import json
import logging
from typing import List, Dict, Any
from multi_source_controller import MatchData

logger = logging.getLogger(__name__)

class ClaudeSimpleAnalyzer:
    """
    Простой анализатор матчей с использованием Claude через Cursor
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze_matches_with_claude(self, matches: List[MatchData], sport_type: str) -> List[MatchData]:
        """
        Анализирует матчи с помощью Claude
        """
        if not matches:
            return []
        
        self.logger.info(f"Claude анализ {len(matches)} матчей для {sport_type}")
        
        # Ограничиваем количество матчей для анализа (Claude имеет лимиты)
        max_matches = 10
        matches_to_analyze = matches[:max_matches]
        
        # Создаем промпт для Claude
        prompt = self._create_analysis_prompt(matches_to_analyze, sport_type)
        
        # Здесь будет вызов Claude
        # Пока используем заглушку
        claude_response = self._simulate_claude_analysis(prompt, matches_to_analyze)
        
        self.logger.info(f"Claude сгенерировал {len(claude_response)} рекомендаций для {sport_type}")
        return claude_response
    
    def _create_analysis_prompt(self, matches: List[MatchData], sport_type: str) -> str:
        """Создает промпт для анализа матчей"""
        
        # Подготавливаем данные матчей
        matches_text = ""
        for i, match in enumerate(matches, 1):
            matches_text += f"{i}. {match.team1} vs {match.team2}\n"
            matches_text += f"   Счет: {match.score}\n"
            matches_text += f"   Минута: {match.minute}\n"
            matches_text += f"   Лига: {match.league}\n\n"
        
        # Правила анализа в зависимости от вида спорта
        rules = {
            'football': """
            Анализируй футбольные матчи:
            1. Найди матчи с не ничейным счетом (1:0, 2:1, 0:1, etc.)
            2. Определи, является ли команда, ведущая в счете, объективным фаворитом
            3. Учитывай: время матча, разницу в счете, качество лиги
            4. Рекомендуй только если вероятность победы фаворита >80%
            """,
            'tennis': """
            Анализируй теннисные матчи:
            1. Найди матчи со счетом 1-0 по сетам или разрывом ≥4 геймов в первом сете
            2. Определи, является ли игрок, ведущий в счете, объективным фаворитом
            3. Учитывай: форму игроков, рейтинг, качество турнира
            4. Рекомендуй только если вероятность победы фаворита >80%
            """,
            'table_tennis': """
            Анализируй матчи настольного тенниса:
            1. Найди матчи со счетом 1-0 или 2-0 по сетам
            2. Определи, является ли игрок, ведущий в счете, объективным фаворитом
            3. Учитывай: форму игроков, рейтинг, качество турнира
            4. Рекомендуй только если вероятность победы фаворита >80%
            """,
            'handball': """
            Анализируй гандбольные матчи:
            1. Найди матчи, где одна команда ведет с разрывом ≥5 голов
            2. Определи, является ли команда, ведущая в счете, объективным фаворитом
            3. Учитывай: форму команд, позицию в таблице, среднюю результативность
            4. Рекомендуй только если вероятность победы фаворита >80%
            """
        }
        
        sport_rules = rules.get(sport_type, rules['football'])
        
        prompt = f"""
        Ты - эксперт по анализу live-ставок. {sport_rules}
        
        Проанализируй следующие матчи и дай рекомендации:
        
        {matches_text}
        
        Верни только JSON массив с рекомендациями в формате:
        [
            {{
                "team1": "Название команды 1",
                "team2": "Название команды 2", 
                "score": "Счет",
                "recommendation": "П1/П2/Победа игрок",
                "confidence": 0.85,
                "reasoning": "Обоснование рекомендации"
            }}
        ]
        
        Если нет подходящих матчей, верни пустой массив [].
        """
        
        return prompt
    
    def _simulate_claude_analysis(self, prompt: str, matches: List[MatchData]) -> List[MatchData]:
        """
        Симуляция анализа Claude
        В реальной версии здесь будет вызов Claude API
        """
        # Пока используем простую эвристику как заглушку
        recommendations = []
        
        for match in matches:
            # Простая эвристика для демонстрации
            if self._should_recommend_match(match):
                recommendation = self._create_recommendation(match)
                recommendations.append(recommendation)
        
        return recommendations
    
    def _should_recommend_match(self, match: MatchData) -> bool:
        """Проверяет, соответствует ли матч правилам системы для рекомендации"""
        
        if match.sport_type == 'football':
            # Футбол: не ничейный счет
            if ':' in match.score:
                try:
                    home_score, away_score = map(int, match.score.split(':'))
                    return home_score != away_score  # Не ничья
                except:
                    pass
                    
        elif match.sport_type == 'tennis':
            # Теннис: счет 1-0 по сетам ИЛИ разрыв ≥4 геймов в первом сете
            return self._is_tennis_advantage(match.score)
            
        elif match.sport_type == 'table_tennis':
            # Настольный теннис: счет 1-0 или 2-0 по сетам
            return self._is_table_tennis_advantage(match.score)
            
        elif match.sport_type == 'handball':
            # Гандбол: разрыв ≥5 голов
            if ':' in match.score:
                try:
                    home_score, away_score = map(int, match.score.split(':'))
                    difference = abs(home_score - away_score)
                    return difference >= 5
                except:
                    pass
        
        return False
    
    def _is_tennis_advantage(self, score: str) -> bool:
        """Проверяет преимущество в теннисе: 1-0 по сетам ИЛИ ≥4 геймов в первом сете"""
        if not score:
            return False
            
        try:
            # Проверяем формат "1:1" (счет по сетам)
            if ':' in score and not any('-' in s for s in score.split()):
                sets = score.strip().split(':')
                if len(sets) == 2:
                    home_sets = int(sets[0])
                    away_sets = int(sets[1])
                    # Преимущество 1-0 по сетам
                    return abs(home_sets - away_sets) == 1 and (home_sets == 1 or away_sets == 1)
            
            # Обычный формат "6-4 3-2" - проверяем геймы в первом сете
            sets = score.split(' ')
            if len(sets) >= 1:
                first_set = sets[0]
                if '-' in first_set:
                    home_games, away_games = map(int, first_set.split('-'))
                    games_lead = abs(home_games - away_games)
                    # Разрыв ≥4 геймов в первом сете
                    return games_lead >= 4
                    
        except Exception as e:
            self.logger.warning(f"Ошибка анализа счета тенниса '{score}': {e}")
            
        return False
    
    def _is_table_tennis_advantage(self, score: str) -> bool:
        """Проверяет преимущество в настольном теннисе: 1-0 или 2-0 по сетам"""
        if not score:
            return False
            
        try:
            # Проверяем формат "1:1" (счет по сетам)
            if ':' in score and not any('-' in s for s in score.split()):
                sets = score.strip().split(':')
                if len(sets) == 2:
                    home_sets = int(sets[0])
                    away_sets = int(sets[1])
                    # Преимущество 1-0 или 2-0 по сетам
                    return (home_sets == 1 and away_sets == 0) or (home_sets == 2 and away_sets == 0) or \
                           (away_sets == 1 and home_sets == 0) or (away_sets == 2 and home_sets == 0)
            
            # Обычный формат "11-9 11-7" - считаем выигранные сеты
            sets = score.split(' ')
            home_sets_won = 0
            away_sets_won = 0
            
            for set_score in sets:
                if '-' in set_score:
                    home_games, away_games = map(int, set_score.split('-'))
                    if home_games > away_games:
                        home_sets_won += 1
                    elif away_games > home_games:
                        away_sets_won += 1
            
            # Преимущество 1-0 или 2-0 по сетам
            return (home_sets_won == 1 and away_sets_won == 0) or (home_sets_won == 2 and away_sets_won == 0) or \
                   (away_sets_won == 1 and home_sets_won == 0) or (away_sets_won == 2 and home_sets_won == 0)
                   
        except Exception as e:
            self.logger.warning(f"Ошибка анализа счета настольного тенниса '{score}': {e}")
            
        return False
    
    def _create_recommendation(self, match: MatchData) -> MatchData:
        """Создает рекомендацию на основе матча"""
        # Копируем матч (используем структуру из enhanced_real_controller)
        recommendation = MatchData(
            sport=match.sport_type,  # Используем sport_type как sport
            team1=match.team1,
            team2=match.team2,
            score=match.score
        )
        recommendation.minute = match.minute
        recommendation.sport_type = match.sport_type
        recommendation.league = match.league
        recommendation.url = match.url
        recommendation.source = match.source
        
        # Определяем рекомендацию
        if ':' in match.score:
            try:
                home_score, away_score = map(int, match.score.split(':'))
                if home_score > away_score:
                    recommendation.recommendation_type = 'win'
                    recommendation.recommendation_value = 'П1'
                    recommendation.justification = f"Команда {match.team1} ведет {match.score}"
                elif away_score > home_score:
                    recommendation.recommendation_type = 'win'
                    recommendation.recommendation_value = 'П2'
                    recommendation.justification = f"Команда {match.team2} ведет {match.score}"
                
                recommendation.probability = 85.0  # Фиксированная уверенность
            except:
                pass
        
        return recommendation