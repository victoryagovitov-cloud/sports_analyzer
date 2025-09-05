#!/usr/bin/env python3
"""
Реалистичный анализатор тенниса и настольного тенниса
"""

import json
import logging
import time
from typing import List, Optional
from openai import OpenAI
from multi_source_controller import MatchData

logger = logging.getLogger(__name__)

class RealisticTennisAnalyzer:
    """
    Анализатор тенниса с реалистичными критериями
    """
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = "gpt-4o-mini"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 2.0
        
    def analyze_tennis_matches_realistic(self, matches: List[MatchData], sport_type: str) -> List[MatchData]:
        """
        Реалистичный анализ теннисных матчей
        """
        if not matches:
            return []
        
        self.logger.info(f"🎾 Реалистичный анализ {sport_type}: {len(matches)} матчей")
        
        recommendations = []
        
        # Анализируем каждый подходящий матч
        for match in matches[:3]:  # Максимум 3 матча
            try:
                recommendation = self._analyze_tennis_match_realistic(match, sport_type)
                if recommendation:
                    recommendations.append(recommendation)
                    
                time.sleep(1)  # Пауза между анализами
                
            except Exception as e:
                self.logger.error(f"Ошибка анализа {match.team1} vs {match.team2}: {e}")
                continue
        
        self.logger.info(f"🎾 Найдено {len(recommendations)} рекомендаций по {sport_type}")
        return recommendations
    
    def _analyze_tennis_match_realistic(self, match: MatchData, sport_type: str) -> Optional[MatchData]:
        """Реалистичный анализ теннисного матча"""
        try:
            # Создаем реалистичный промпт
            prompt = self._create_realistic_tennis_prompt(match, sport_type)
            
            # Вызываем OpenAI
            response = self._call_openai_with_rate_limit(prompt)
            
            # Обрабатываем ответ
            recommendation = self._process_tennis_response(response, match, sport_type)
            
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа теннисного матча: {e}")
            return None
    
    def _create_realistic_tennis_prompt(self, match: MatchData, sport_type: str) -> str:
        """Создает реалистичный промпт для тенниса"""
        
        base_info = f"""
        Матч: {match.team1} vs {match.team2}
        Счет: {match.score}
        Статус: {getattr(match, 'minute', '')}
        Турнир: {getattr(match, 'league', '')}
        """
        
        if sport_type == 'tennis':
            return f"""Ты - эксперт по теннисным ставкам.

{base_info}

РЕАЛИСТИЧНЫЕ КРИТЕРИИ ДЛЯ ТЕННИСА:
1. Есть ли преимущество по сетам? (1:0, 2:0, 2:1)
2. Если нет счета по сетам - есть ли другие признаки фаворитизма?
3. Качество турнира (топ-турниры более предсказуемы)

ЗАДАЧА:
Определи, стоит ли делать ставку на основе ДОСТУПНЫХ данных.
Не требуй недоступную статистику (рейтинги, H2H, форму).

Если видишь потенциал для ставки - дай рекомендацию.
Если нет явного фаворита - откажись.

            JSON: {{"recommendation": "Победа [Игрок]/НЕТ", "confidence": 0.75, "reason": "КРАТКОЕ обоснование (максимум 15-20 слов)"}}"""

        elif sport_type == 'table_tennis':
            return f"""Ты - эксперт по настольному теннису.

{base_info}

КРИТЕРИИ ДЛЯ НАСТОЛЬНОГО ТЕННИСА:
1. Преимущество 1:0 или 2:0 по сетам (по промпту)
2. Если ведет по сетам - анализируй потенциал победы

ЗАДАЧА:
Если есть преимущество 1:0 или 2:0 по сетам - рассмотри ставку на ведущего игрока.
Используй доступную информацию (счет, статус матча).

            JSON: {{"recommendation": "Победа [Игрок]/НЕТ", "confidence": 0.75, "reason": "КРАТКОЕ обоснование (максимум 15-20 слов)"}}"""
        
        return base_info
    
    def _call_openai_with_rate_limit(self, prompt: str) -> str:
        """Вызов OpenAI с rate limiting"""
        # Rate limiting
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты эксперт по теннисным ставкам. Анализируй реалистично на основе доступных данных."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.2,
                timeout=30
            )
            
            self.last_request_time = time.time()
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Ошибка OpenAI запроса: {e}")
            raise e
    
    def _process_tennis_response(self, response: str, match: MatchData, sport_type: str) -> Optional[MatchData]:
        """Обрабатывает ответ GPT для тенниса"""
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
            
            recommendation_value = analysis.get('recommendation', 'НЕТ')
            if recommendation_value == 'НЕТ':
                return None
            
            confidence = analysis.get('confidence', 0)
            if confidence < 0.70:  # Более мягкий порог для тенниса
                return None
            
            # Создаем рекомендацию
            recommendation = MatchData(
                sport=sport_type,
                team1=match.team1,
                team2=match.team2,
                score=match.score,
                minute=getattr(match, 'minute', ''),
                league=getattr(match, 'league', ''),
                link=getattr(match, 'link', ''),
                source='realistic_tennis'
            )
            
            recommendation.probability = confidence * 100
            recommendation.recommendation_type = 'win'
            recommendation.recommendation_value = recommendation_value
            recommendation.justification = analysis.get('reason', 'Реалистичный анализ')
            
            return recommendation
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Ошибка парсинга JSON: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Ошибка обработки ответа: {e}")
            return None

# Глобальный экземпляр
realistic_tennis_analyzer = None

def get_realistic_tennis_analyzer(api_key: str):
    global realistic_tennis_analyzer
    if realistic_tennis_analyzer is None:
        realistic_tennis_analyzer = RealisticTennisAnalyzer(api_key)
    return realistic_tennis_analyzer