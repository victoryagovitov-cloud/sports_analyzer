#!/usr/bin/env python3
"""
Анализатор, полностью соответствующий промпту пользователя
"""

import json
import logging
import time
from typing import List, Dict, Any, Optional
from openai import OpenAI
from multi_source_controller import MatchData
from moscow_time import format_moscow_time_for_telegram

logger = logging.getLogger(__name__)

class PromptCompliantAnalyzer:
    """
    Анализатор, строго следующий промпту пользователя
    """
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = "gpt-4o-mini"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 2.0
        
    def analyze_football_matches(self, matches: List[MatchData]) -> List[MatchData]:
        """
        Анализ футбольных матчей строго по промпту
        """
        self.logger.info(f"⚽ Анализ футбола по промпту: {len(matches)} матчей")
        
        # Первичный фильтр: не ничейный счет, 25-75 минута
        filtered_matches = self._football_primary_filter(matches)
        self.logger.info(f"После первичного фильтра: {len(filtered_matches)} матчей")
        
        if not filtered_matches:
            return []
        
        recommendations = []
        
        # Анализируем каждый матч по критериям промпта
        for match in filtered_matches[:5]:  # Максимум 5 матчей
            try:
                recommendation = self._analyze_football_match_by_prompt(match)
                if recommendation:
                    recommendations.append(recommendation)
            except Exception as e:
                self.logger.error(f"Ошибка анализа {match.team1} vs {match.team2}: {e}")
        
        return recommendations
    
    def _football_primary_filter(self, matches: List[MatchData]) -> List[MatchData]:
        """Первичный фильтр для футбола: не ничейный счет, 25-75 минута"""
        filtered = []
        
        for match in matches:
            try:
                if ':' not in match.score:
                    continue
                
                home_score, away_score = map(int, match.score.split(':'))
                minute_str = getattr(match, 'minute', '0')
                minute = int(minute_str.replace("'", "").replace("′", "")) if minute_str.replace("'", "").replace("′", "").isdigit() else 0
                
                # Критерии по промпту
                if home_score == away_score:  # Ничейный счет - исключаем
                    continue
                if minute < 25 or minute > 75:  # Вне временного окна
                    continue
                
                filtered.append(match)
                
            except Exception:
                continue
        
        return filtered
    
    def _analyze_football_match_by_prompt(self, match: MatchData) -> Optional[MatchData]:
        """
        Анализ футбольного матча строго по критериям промпта
        """
        try:
            # Создаем промпт для глубокого анализа
            analysis_prompt = f"""
            Ты эксперт по спортивным ставкам. Проанализируй футбольный матч по строгим критериям.
            
            МАТЧ: {match.team1} vs {match.team2}
            СЧЕТ: {match.score}
            МИНУТА: {match.minute}
            ЛИГА: {match.league}
            
            КРИТЕРИИ ОТБОРА (ВСЕ ДОЛЖНЫ БЫТЬ ВЫПОЛНЕНЫ):
            1. Разница в таблице ≥ 5 позиций
            2. Форма ведущей команды: ≥ 3 победы в последних 5 играх
            3. H2H: ≥ 3 победы из 5 встреч
            4. xG ≥ 1.5 у фаворита (если доступно)
            5. Коэффициент ≤ 2.20
            
            Проанализируй матч и дай ОЧЕНЬ краткое обоснование (максимум 15-20 слов).
            Тон: профессиональный, уверенный, без эмоций.
            
            ОТВЕТ В JSON:
            {{
                "meets_criteria": true/false,
                "recommendation": "П1/П2",
                "confidence": 0.85,
                "coefficient": 1.65,
                "reasoning": "Краткое профессиональное обоснование с ключевыми статистическими показателями"
            }}
            
            Если матч НЕ соответствует критериям, верни "meets_criteria": false.
            """
            
            # Вызываем OpenAI для анализа
            response = self._call_openai_with_rate_limit(analysis_prompt)
            
            # Обрабатываем ответ
            recommendation = self._process_football_analysis(response, match)
            
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа футбольного матча: {e}")
            return None
    
    def _call_openai_with_rate_limit(self, prompt: str) -> str:
        """Вызов OpenAI с соблюдением лимитов"""
        # Rate limiting
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты профессиональный аналитик спортивных ставок."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,  # Короткие ответы по промпту
                temperature=0.3,
                timeout=30
            )
            
            self.last_request_time = time.time()
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Ошибка OpenAI запроса: {e}")
            raise e
    
    def _process_football_analysis(self, response: str, match: MatchData) -> Optional[MatchData]:
        """Обрабатывает ответ анализа футбольного матча"""
        try:
            # Очищаем ответ
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            # Парсим JSON
            analysis = json.loads(response)
            
            # Проверяем, соответствует ли матч критериям
            if not analysis.get('meets_criteria', False):
                return None
            
            confidence = analysis.get('confidence', 0)
            if confidence < 0.75:  # Минимальная уверенность
                return None
            
            # Создаем рекомендацию
            recommendation = MatchData(
                sport='football',
                team1=match.team1,
                team2=match.team2,
                score=match.score,
                minute=getattr(match, 'minute', ''),
                league=getattr(match, 'league', ''),
                link=getattr(match, 'link', ''),
                source='scores24_only'
            )
            
            recommendation.probability = confidence * 100
            recommendation.recommendation_type = 'win'
            recommendation.recommendation_value = analysis.get('recommendation', 'П1')
            recommendation.justification = analysis.get('reasoning', 'Анализ по промпту')
            
            # Добавляем коэффициент из анализа
            coefficient = analysis.get('coefficient', 1.50)
            recommendation.odds = {'main': coefficient}
            
            return recommendation
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Ошибка парсинга JSON: {e}")
            self.logger.error(f"Ответ: {response}")
            return None
        except Exception as e:
            self.logger.error(f"Ошибка обработки анализа: {e}")
            return None
    
    def analyze_tennis_matches(self, matches: List[MatchData]) -> List[MatchData]:
        """Анализ теннисных матчей по промпту"""
        # Аналогично футболу, но с критериями для тенниса
        return []  # Пока заглушка
    
    def analyze_handball_matches(self, matches: List[MatchData]) -> List[MatchData]:
        """Анализ гандбольных матчей по промпту"""
        # Аналогично футболу, но с критериями для гандбола + тоталы
        return []  # Пока заглушка

# Глобальный экземпляр
prompt_compliant_analyzer = None

def get_prompt_analyzer(api_key: str):
    global prompt_compliant_analyzer
    if prompt_compliant_analyzer is None:
        prompt_compliant_analyzer = PromptCompliantAnalyzer(api_key)
    return prompt_compliant_analyzer