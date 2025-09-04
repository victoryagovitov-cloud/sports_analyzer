import json
import logging
from typing import List, Dict, Any
from multi_source_controller import MatchData

logger = logging.getLogger(__name__)

class ClaudeCursorAnalyzer:
    """
    Анализатор матчей с использованием Claude через Cursor API
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__name__)
    
    def analyze_matches_with_claude(self, matches: List[MatchData], sport_type: str) -> List[MatchData]:
        """
        Анализирует матчи с помощью Claude через Cursor
        """
        if not matches:
            return []
        
        self.logger.info(f"Claude анализ {len(matches)} матчей для {sport_type}")
        
        # Подготавливаем данные для Claude
        matches_data = self._prepare_matches_for_claude(matches, sport_type)
        
        # Создаем промпт для Claude
        prompt = self._create_claude_prompt(matches_data, sport_type)
        
        # Здесь будет вызов Claude через Cursor API
        # Пока используем заглушку, которая будет заменена реальным вызовом
        claude_analysis = self._call_claude_api(prompt)
        
        # Обрабатываем ответ Claude
        recommendations = self._process_claude_response(claude_analysis, matches)
        
        self.logger.info(f"Claude сгенерировал {len(recommendations)} рекомендаций для {sport_type}")
        return recommendations
    
    def _prepare_matches_for_claude(self, matches: List[MatchData], sport_type: str) -> List[Dict[str, Any]]:
        """Подготавливает данные матчей для отправки в Claude"""
        matches_data = []
        
        for match in matches:
            match_info = {
                'teams': f"{match.team1} vs {match.team2}",
                'score': match.score,
                'minute': match.minute,
                'league': match.league,
                'sport_type': sport_type,
                'url': match.url
            }
            matches_data.append(match_info)
        
        return matches_data
    
    def _create_claude_prompt(self, matches_data: List[Dict[str, Any]], sport_type: str) -> str:
        """Создает промпт для Claude"""
        
        sport_rules = {
            'football': """
            Анализируй футбольные матчи по следующим критериям:
            1. Найди матчи с не ничейным счетом (1:0, 2:1, 0:1, etc.)
            2. Определи, является ли команда, ведущая в счете, объективным фаворитом
            3. Учитывай: время матча, разницу в счете, качество лиги
            4. Рекомендуй только если вероятность победы фаворита >80%
            5. Формат ответа: JSON с полями: team1, team2, score, recommendation, confidence, reasoning
            """,
            'tennis': """
            Анализируй теннисные матчи по следующим критериям:
            1. Найди матчи со счетом 1-0 по сетам или разрывом ≥4 геймов в первом сете
            2. Определи, является ли игрок, ведущий в счете, объективным фаворитом
            3. Учитывай: форму игроков, рейтинг, качество турнира
            4. Рекомендуй только если вероятность победы фаворита >80%
            5. Формат ответа: JSON с полями: team1, team2, score, recommendation, confidence, reasoning
            """,
            'table_tennis': """
            Анализируй матчи настольного тенниса по следующим критериям:
            1. Найди матчи со счетом 1-0 или 2-0 по сетам
            2. Определи, является ли игрок, ведущий в счете, объективным фаворитом
            3. Учитывай: форму игроков, рейтинг, качество турнира
            4. Рекомендуй только если вероятность победы фаворита >80%
            5. Формат ответа: JSON с полями: team1, team2, score, recommendation, confidence, reasoning
            """,
            'handball': """
            Анализируй гандбольные матчи по следующим критериям:
            1. Найди матчи, где одна команда ведет с разрывом ≥5 голов
            2. Определи, является ли команда, ведущая в счете, объективным фаворитом
            3. Учитывай: форму команд, позицию в таблице, среднюю результативность
            4. Рекомендуй только если вероятность победы фаворита >80%
            5. Формат ответа: JSON с полями: team1, team2, score, recommendation, confidence, reasoning
            """
        }
        
        rules = sport_rules.get(sport_type, sport_rules['football'])
        
        prompt = f"""
        Ты - эксперт по анализу live-ставок. {rules}
        
        Проанализируй следующие матчи и дай рекомендации:
        
        {json.dumps(matches_data, ensure_ascii=False, indent=2)}
        
        Верни только JSON массив с рекомендациями. Если нет подходящих матчей, верни пустой массив [].
        """
        
        return prompt
    
    def _call_claude_api(self, prompt: str) -> str:
        """
        Вызывает Claude API через Cursor
        """
        try:
            # Используем встроенные возможности Cursor для вызова Claude
            # Это будет работать в среде Cursor с подпиской Pro+
            
            # Создаем запрос к Claude через Cursor API
            import subprocess
            import tempfile
            import os
            
            # Создаем временный файл с промптом
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                temp_file = f.name
            
            try:
                # Вызываем Claude через Cursor CLI (если доступен)
                result = subprocess.run([
                    'cursor', 'claude', 'analyze', temp_file
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    return result.stdout
                else:
                    self.logger.warning(f"Claude API error: {result.stderr}")
                    return "[]"
                    
            except Exception as e:
                self.logger.warning(f"Claude API недоступен: {e}")
                # Fallback: используем эвристический анализ
                return self._fallback_heuristic_analysis(prompt)
            finally:
                # Удаляем временный файл
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    
        except Exception as e:
            self.logger.error(f"Ошибка вызова Claude API: {e}")
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
        # Копируем оригинальный матч
        recommendation = MatchData(
            team1=original_match.team1,
            team2=original_match.team2,
            score=original_match.score,
            minute=original_match.minute,
            coefficient=original_match.coefficient,
            is_locked=original_match.is_locked,
            sport_type=original_match.sport_type,
            league=original_match.league,
            url=original_match.url,
            source=original_match.source
        )
        
        # Добавляем данные от Claude
        recommendation.probability = claude_rec.get('confidence', 0) * 100
        recommendation.recommendation_type = 'win'
        recommendation.recommendation_value = claude_rec.get('recommendation', '')
        recommendation.justification = claude_rec.get('reasoning', '')
        
        return recommendation