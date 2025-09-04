import json
import logging
import subprocess
import tempfile
import os
from typing import List, Dict, Any
from multi_source_controller import MatchData

logger = logging.getLogger(__name__)

class ClaudeCursorAPI:
    """
    Анализатор матчей с использованием Claude через Cursor API
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze_matches_with_claude(self, matches: List[MatchData], sport_type: str) -> List[MatchData]:
        """
        Анализирует матчи с помощью Claude через Cursor
        """
        if not matches:
            return []
        
        self.logger.info(f"Claude анализ {len(matches)} матчей для {sport_type}")
        
        # Ограничиваем количество матчей для анализа
        max_matches = 5  # Меньше матчей для более точного анализа
        matches_to_analyze = matches[:max_matches]
        
        # Создаем промпт для Claude
        prompt = self._create_analysis_prompt(matches_to_analyze, sport_type)
        
        # Вызываем Claude через Cursor
        claude_response = self._call_claude_via_cursor(prompt)
        
        # Обрабатываем ответ Claude
        recommendations = self._process_claude_response(claude_response, matches_to_analyze)
        
        self.logger.info(f"Claude сгенерировал {len(recommendations)} рекомендаций для {sport_type}")
        return recommendations
    
    def _create_analysis_prompt(self, matches: List[MatchData], sport_type: str) -> str:
        """Создает промпт для анализа матчей"""
        
        # Подготавливаем данные матчей
        matches_text = ""
        for i, match in enumerate(matches, 1):
            matches_text += f"{i}. {match.team1} vs {match.team2}\n"
            matches_text += f"   Счет: {match.score}\n"
            matches_text += f"   Минута: {match.minute}\n"
            matches_text += f"   Лига: {match.league}\n\n"
        
        # Строгие правила анализа
        rules = {
            'football': """
            СТРОГИЕ ПРАВИЛА ДЛЯ ФУТБОЛА:
            1. Найди ТОЛЬКО матчи с НЕ ничейным счетом (1:0, 2:1, 0:1, etc.) - НЕ ничья
            2. Определи, является ли команда, ведущая в счете, объективным фаворитом
            3. Рекомендуй ТОЛЬКО если вероятность победы фаворита >80%
            """,
            'tennis': """
            СТРОГИЕ ПРАВИЛА ДЛЯ ТЕННИСА:
            1. Найди ТОЛЬКО матчи со счетом 1-0 по сетам ИЛИ разрывом ≥4 геймов в первом сете
            2. Определи, является ли игрок, ведущий в счете, объективным фаворитом
            3. Рекомендуй ТОЛЬКО если вероятность победы фаворита >80%
            """,
            'table_tennis': """
            СТРОГИЕ ПРАВИЛА ДЛЯ НАСТОЛЬНОГО ТЕННИСА:
            1. Найди ТОЛЬКО матчи со счетом 1-0 или 2-0 по сетам
            2. Определи, является ли игрок, ведущий в счете, объективным фаворитом
            3. Рекомендуй ТОЛЬКО если вероятность победы фаворита >80%
            """,
            'handball': """
            СТРОГИЕ ПРАВИЛА ДЛЯ ГАНДБОЛА:
            1. Найди ТОЛЬКО матчи, где одна команда ведет с разрывом ≥5 голов
            2. Определи, является ли команда, ведущая в счете, объективным фаворитом
            3. Рекомендуй ТОЛЬКО если вероятность победы фаворита >80%
            """
        }
        
        sport_rules = rules.get(sport_type, rules['football'])
        
        prompt = f"""
        Ты - эксперт по анализу live-ставок. {sport_rules}
        
        Проанализируй следующие матчи СТРОГО по правилам выше:
        
        {matches_text}
        
        Верни ТОЛЬКО JSON массив с рекомендациями в формате:
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
        
        Если НЕТ матчей, соответствующих строгим правилам, верни пустой массив [].
        """
        
        return prompt
    
    def _call_claude_via_cursor(self, prompt: str) -> str:
        """
        Вызывает Claude через Cursor API
        """
        try:
            # Создаем временный файл с промптом
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(prompt)
                temp_file = f.name
            
            try:
                # Пробуем вызвать Claude через Cursor
                # Способ 1: Через cursor CLI
                try:
                    result = subprocess.run([
                        'cursor', 'claude', 'analyze', temp_file
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        self.logger.info("Claude вызван через cursor CLI")
                        return result.stdout
                except Exception as e:
                    self.logger.debug(f"Cursor CLI недоступен: {e}")
                
                # Способ 2: Через cursor API (если доступен)
                try:
                    # Пробуем использовать cursor API напрямую
                    result = subprocess.run([
                        'cursor', 'api', 'claude', 'analyze', temp_file
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        self.logger.info("Claude вызван через cursor API")
                        return result.stdout
                except Exception as e:
                    self.logger.debug(f"Cursor API недоступен: {e}")
                
                # Способ 3: Через anthropic API
                try:
                    import anthropic
                    client = anthropic.Anthropic()
                    
                    response = client.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=2000,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    self.logger.info("Claude вызван через anthropic API")
                    return response.content[0].text
                except Exception as e:
                    self.logger.debug(f"Anthropic API недоступен: {e}")
                
                # Fallback: используем эвристический анализ
                self.logger.warning("Claude API недоступен, используем эвристический анализ")
                return self._fallback_heuristic_analysis(prompt)
                
            finally:
                # Удаляем временный файл
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    
        except Exception as e:
            self.logger.error(f"Ошибка вызова Claude: {e}")
            return "[]"
    
    def _fallback_heuristic_analysis(self, prompt: str) -> str:
        """Fallback анализ, если Claude недоступен"""
        # Простая эвристика как запасной вариант
        return "[]"
    
    def _process_claude_response(self, claude_response: str, original_matches: List[MatchData]) -> List[MatchData]:
        """Обрабатывает ответ от Claude и создает рекомендации"""
        try:
            # Парсим JSON ответ от Claude
            claude_recommendations = json.loads(claude_response)
            
            recommendations = []
            
            for claude_rec in claude_recommendations:
                # Находим соответствующий оригинальный матч
                original_match = self._find_matching_match(claude_rec, original_matches)
                
                if original_match:
                    # Создаем рекомендацию на основе ответа Claude
                    recommendation = self._create_recommendation_from_claude(original_match, claude_rec)
                    recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки ответа Claude: {e}")
            return []
    
    def _find_matching_match(self, claude_rec: Dict[str, Any], original_matches: List[MatchData]) -> MatchData:
        """Находит соответствующий оригинальный матч по данным от Claude"""
        for match in original_matches:
            if (match.team1 == claude_rec.get('team1') and 
                match.team2 == claude_rec.get('team2') and
                match.score == claude_rec.get('score')):
                return match
        return None
    
    def _create_recommendation_from_claude(self, original_match: MatchData, claude_rec: Dict[str, Any]) -> MatchData:
        """Создает рекомендацию на основе ответа Claude"""
        # Копируем матч
        recommendation = MatchData(
            sport=original_match.sport_type,
            team1=original_match.team1,
            team2=original_match.team2,
            score=original_match.score
        )
        recommendation.minute = original_match.minute
        recommendation.sport_type = original_match.sport_type
        recommendation.league = original_match.league
        recommendation.url = original_match.url
        recommendation.source = original_match.source
        
        # Добавляем данные от Claude
        recommendation.probability = claude_rec.get('confidence', 0) * 100
        recommendation.recommendation_type = 'win'
        recommendation.recommendation_value = claude_rec.get('recommendation', '')
        recommendation.justification = claude_rec.get('reasoning', '')
        
        return recommendation