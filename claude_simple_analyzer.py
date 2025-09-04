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
        """Простая эвристика для определения, стоит ли рекомендовать матч"""
        # Анализируем счет
        if ':' in match.score:
            try:
                home_score, away_score = map(int, match.score.split(':'))
                difference = abs(home_score - away_score)
                
                # Рекомендуем если есть преимущество
                if difference >= 1:
                    return True
            except:
                pass
        
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