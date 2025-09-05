#!/usr/bin/env python3
"""
Анализатор с проверкой по внешним источникам через OpenAI
Использует базу знаний GPT о командах, лигах, игроках
"""

import json
import logging
import time
from typing import List, Dict, Any, Optional
from openai import OpenAI
from multi_source_controller import MatchData

logger = logging.getLogger(__name__)

class ExternalKnowledgeAnalyzer:
    """
    Анализатор, использующий знания OpenAI о спорте
    """
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = "gpt-4o-mini"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 2.0
        
    def analyze_with_external_knowledge(self, matches: List[MatchData], sport_type: str) -> List[MatchData]:
        """
        Анализ матчей с использованием внешних знаний OpenAI
        """
        if not matches:
            return []
        
        self.logger.info(f"🌐 Анализ с внешними знаниями: {len(matches)} матчей {sport_type}")
        
        recommendations = []
        
        # Анализируем каждый матч с расширенной проверкой
        for match in matches[:3]:  # Максимум 3 матча
            try:
                recommendation = self._analyze_match_with_knowledge(match, sport_type)
                if recommendation:
                    recommendations.append(recommendation)
                    
                time.sleep(1)  # Пауза между анализами
                
            except Exception as e:
                self.logger.error(f"Ошибка анализа с внешними знаниями: {e}")
                continue
        
        self.logger.info(f"🌐 Найдено {len(recommendations)} рекомендаций с внешней проверкой")
        return recommendations
    
    def _analyze_match_with_knowledge(self, match: MatchData, sport_type: str) -> Optional[MatchData]:
        """Анализ матча с использованием внешних знаний"""
        try:
            # Создаем промпт с запросом внешних знаний
            knowledge_prompt = self._create_external_knowledge_prompt(match, sport_type)
            
            # Вызываем OpenAI
            response = self._call_openai_with_rate_limit(knowledge_prompt)
            
            # Обрабатываем ответ
            recommendation = self._process_knowledge_response(response, match, sport_type)
            
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа с знаниями: {e}")
            return None
    
    def _create_external_knowledge_prompt(self, match: MatchData, sport_type: str) -> str:
        """Создает промпт с запросом внешних знаний"""
        
        base_info = f"""
        Матч: {match.team1} vs {match.team2}
        Счет: {match.score}
        Минута: {getattr(match, 'minute', '')}
        Лига: {getattr(match, 'league', '')}
        """
        
        if sport_type == 'football':
            return f"""Ты - эксперт по футболу с доступом к обширной базе знаний.

МАТЧ НА SCORES24.LIVE:
{base_info}

ЗАДАЧА: Используй свои знания о командах, лигах и футболе для ДОПОЛНИТЕЛЬНОЙ проверки.

ПРОВЕРЬ ПО СВОИМ ЗНАНИЯМ:
1. 🏆 КОМАНДЫ:
   - Какой уровень этих команд?
   - Кто обычно сильнее исторически?
   - Есть ли известные звездные игроки?
   - Финансовое положение клубов

2. 🏟️ ЛИГА/ТУРНИР:
   - Какой уровень этой лиги?
   - Насколько предсказуемы результаты?
   - Есть ли особенности (плей-офф, вылет)?

3. 📊 ТЕКУЩИЙ СЕЗОН:
   - Какая форма команд в этом сезоне?
   - Позиции в таблице (если знаешь)
   - Мотивация команд

4. 🎯 КОНТЕКСТ МАТЧА:
   - Домашняя/выездная игра
   - Важность матча
   - Травмы ключевых игроков (если знаешь)

КРИТЕРИИ ДЛЯ РЕКОМЕНДАЦИИ:
- Время: 25-75 минута ✓
- Ведущая команда должна быть ЯВНЫМ фаворитом по твоим знаниям
- Минимум 75% уверенности

ОТВЕТ JSON:
{{
    "external_analysis": {{
        "team_levels": "Анализ уровня команд",
        "league_quality": "Анализ лиги", 
        "historical_advantage": "Кто сильнее исторически",
        "current_form": "Текущая форма команд"
    }},
    "recommendation": "П1/П2/НЕТ",
    "confidence": 0.78,
    "reasoning": "Краткое обоснование с учетом внешних знаний (15-20 слов)"
}}

Если твои знания противоречат данным scores24 - откажись от рекомендации."""

        elif sport_type == 'tennis':
            return f"""Ты - эксперт по теннису с обширными знаниями об игроках.

МАТЧ НА SCORES24.LIVE:
{base_info}

ПРОВЕРЬ ПО СВОИМ ЗНАНИЯМ:
1. 🎾 ИГРОКИ:
   - Рейтинг ATP/WTA этих игроков
   - Кто сильнее исторически
   - Стиль игры и сильные стороны
   - Текущая форма в сезоне

2. 🏆 ТУРНИР:
   - Уровень турнира
   - Покрытие корта (если знаешь)
   - Призовой фонд

3. 📊 СТАТИСТИКА:
   - Личные встречи (H2H)
   - Статистика на разных покрытиях
   - Форма в последних турнирах

ОТВЕТ JSON:
{{
    "player_analysis": "Анализ игроков",
    "h2h_knowledge": "История встреч",
    "recommendation": "Победа [Игрок]/НЕТ",
    "confidence": 0.75,
    "reasoning": "Краткое обоснование с учетом знаний об игроках"
}}"""

        elif sport_type == 'table_tennis':
            return f"""Ты - эксперт по настольному теннису.

МАТЧ НА SCORES24.LIVE:
{base_info}

ПРОВЕРЬ ПО ЗНАНИЯМ:
- Уровень игроков в мировом рейтинге
- Стиль игры (атакующий/защитный)
- Опыт на международных турнирах

ОТВЕТ JSON:
{{
    "player_levels": "Анализ уровня игроков",
    "recommendation": "Победа [Игрок]/НЕТ", 
    "confidence": 0.75,
    "reasoning": "Краткое обоснование"
}}"""

        elif sport_type == 'handball':
            return f"""Ты - эксперт по гандболу.

МАТЧ НА SCORES24.LIVE:
{base_info}

ПРОВЕРЬ ПО ЗНАНИЯМ:
- Уровень команд в европейском гандболе
- Стиль игры и тактика
- Опыт в международных турнирах

ОТВЕТ JSON:
{{
    "team_analysis": "Анализ команд",
    "recommendation": "П1/П2/НЕТ",
    "confidence": 0.75,
    "reasoning": "Краткое обоснование"
}}"""
        
        return base_info
    
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
                    {
                        "role": "system", 
                        "content": "Ты эксперт по спорту с обширными знаниями о командах, игроках, лигах и турнирах. Используй свои знания для дополнительной проверки данных."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=400,  # Больше токенов для внешнего анализа
                temperature=0.2,
                timeout=30
            )
            
            self.last_request_time = time.time()
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Ошибка OpenAI запроса с внешними знаниями: {e}")
            raise e
    
    def _process_knowledge_response(self, response: str, match: MatchData, sport_type: str) -> Optional[MatchData]:
        """Обрабатывает ответ с внешними знаниями"""
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
            if confidence < 0.75:  # Минимальная уверенность с внешними знаниями
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
                source='external_knowledge'
            )
            
            recommendation.probability = confidence * 100
            recommendation.recommendation_type = 'win'
            recommendation.recommendation_value = recommendation_value
            
            # Объединяем обоснование с внешними знаниями
            base_reasoning = analysis.get('reasoning', '')
            external_info = self._extract_external_info(analysis, sport_type)
            
            if external_info:
                recommendation.justification = f"{base_reasoning} {external_info}"
            else:
                recommendation.justification = base_reasoning
            
            return recommendation
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Ошибка парсинга JSON с внешними знаниями: {e}")
            self.logger.error(f"Ответ: {response}")
            return None
        except Exception as e:
            self.logger.error(f"Ошибка обработки внешних знаний: {e}")
            return None
    
    def _extract_external_info(self, analysis: Dict, sport_type: str) -> str:
        """Извлекает информацию из внешних знаний"""
        try:
            if sport_type == 'football':
                external = analysis.get('external_analysis', {})
                team_levels = external.get('team_levels', '')
                historical = external.get('historical_advantage', '')
                
                if team_levels or historical:
                    return f"(Внешние данные: {team_levels or historical})"
                    
            elif sport_type == 'tennis':
                player_analysis = analysis.get('player_analysis', '')
                h2h = analysis.get('h2h_knowledge', '')
                
                if player_analysis or h2h:
                    return f"(Знания об игроках: {player_analysis or h2h})"
            
            return ""
            
        except Exception:
            return ""

# Глобальный экземпляр
external_knowledge_analyzer = None

def get_external_knowledge_analyzer(api_key: str):
    global external_knowledge_analyzer
    if external_knowledge_analyzer is None:
        external_knowledge_analyzer = ExternalKnowledgeAnalyzer(api_key)
    return external_knowledge_analyzer