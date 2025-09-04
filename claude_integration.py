"""
Интеграция с Claude API для продвинутого AI-анализа
"""

import logging
from typing import List, Dict, Any
from multi_source_controller import MatchData
import json

logger = logging.getLogger(__name__)

class ClaudeIntegration:
    """Интеграция с Claude API для AI-анализа"""
    
    def __init__(self, api_key: str = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.api_key = api_key or "YOUR_CLAUDE_API_KEY"
        # В реальной реализации здесь будет инициализация Claude API клиента
        
    def analyze_matches_with_claude(self, matches: List[MatchData], sport_type: str) -> List[MatchData]:
        """
        Анализирует матчи с помощью Claude API
        """
        if not matches:
            return []
            
        self.logger.info(f"Claude API анализ {len(matches)} матчей для {sport_type}")
        
        # Подготавливаем контекст для Claude
        context = self._prepare_claude_context(matches, sport_type)
        
        # Генерируем промпт для Claude
        prompt = self._generate_claude_prompt(context, sport_type)
        
        # В реальной реализации здесь будет вызов Claude API
        # claude_response = self._call_claude_api(prompt)
        
        # Пока возвращаем пустой список (заглушка)
        self.logger.warning("Claude API не настроен, используйте эвристический анализ")
        return []
    
    def _prepare_claude_context(self, matches: List[MatchData], sport_type: str) -> Dict[str, Any]:
        """Подготавливает контекст для Claude API"""
        context = {
            'sport_type': sport_type,
            'matches_count': len(matches),
            'matches': []
        }
        
        for match in matches:
            match_data = {
                'team1': match.team1,
                'team2': match.team2,
                'score': match.score,
                'minute': match.minute,
                'league': match.league,
                'source': match.source,
                'url': match.url
            }
            context['matches'].append(match_data)
        
        return context
    
    def _generate_claude_prompt(self, context: Dict[str, Any], sport_type: str) -> str:
        """Генерирует промпт для Claude API"""
        
        sport_instructions = {
            'football': """
            Проанализируй футбольные матчи и найди те, где команда с преимуществом в счете является объективным фаворитом.
            Учитывай:
            - Преимущество в счете (чем больше, тем лучше)
            - Время матча (чем позже, тем стабильнее)
            - Качество лиги (определи по названиям команд)
            - Размер преимущества относительно времени
            - Критические моменты матча
            """,
            'tennis': """
            Проанализируй теннисные матчи и найди те, где игрок с преимуществом является объективным фаворитом.
            Учитывай:
            - Преимущество по сетам (самый важный фактор)
            - Преимущество в геймах текущего сета
            - Качество турнира (ATP, WTA, Grand Slam, Challenger)
            - Стадию матча (третий сет и далее более стабильны)
            - Известность игроков
            """,
            'handball': """
            Проанализируй гандбольные матчи для двух типов ставок:
            1. Прямые победы: команда с преимуществом ≥5 голов
            2. Тоталы: матчи во втором тайме (10-45 минута)
            Учитывай:
            - Размер преимущества в счете
            - Время матча для тоталов
            - Темп игры (голы в минуту)
            - Прогнозный тотал для рекомендаций
            """
        }
        
        instruction = sport_instructions.get(sport_type, "Проанализируй матчи и найди перспективные ставки.")
        
        prompt = f"""
        Ты эксперт по live-ставкам на спорт. {instruction}
        
        Данные матчей:
        {json.dumps(context, ensure_ascii=False, indent=2)}
        
        Для каждого подходящего матча верни JSON с полями:
        - team1, team2: названия команд
        - score: счет
        - recommendation_type: 'win' или 'total'
        - recommendation_value: 'П1', 'П2', 'ТБ X', 'ТМ Y'
        - confidence: уверенность от 0.0 до 1.0
        - coefficient: коэффициент от 1.0 до 2.0
        - reasoning: подробное обоснование на русском языке
        
        Верни только JSON массив рекомендаций, без дополнительного текста.
        """
        
        return prompt
    
    def _call_claude_api(self, prompt: str) -> str:
        """
        Вызывает Claude API (заглушка для реальной реализации)
        """
        # В реальной реализации здесь будет:
        # 1. Инициализация Claude API клиента
        # 2. Отправка промпта
        # 3. Получение ответа
        # 4. Обработка ошибок
        
        self.logger.warning("Claude API вызов не реализован")
        return ""
    
    def parse_claude_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Парсит ответ от Claude API
        """
        try:
            # Пытаемся извлечь JSON из ответа
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                self.logger.error("Не удалось найти JSON в ответе Claude")
                return []
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Ошибка парсинга JSON от Claude: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Ошибка обработки ответа Claude: {e}")
            return []

# Пример использования
if __name__ == "__main__":
    # Демонстрация интеграции с Claude
    claude = ClaudeIntegration()
    
    # Создаем тестовые данные
    test_matches = [
        MatchData(
            team1="Real Madrid",
            team2="Barcelona",
            score="2:0",
            minute="75",
            coefficient=1.5,
            is_locked=False,
            sport_type="football",
            league="La Liga",
            url="https://example.com/match1"
        )
    ]
    
    # Генерируем промпт для Claude
    context = claude._prepare_claude_context(test_matches, "football")
    prompt = claude._generate_claude_prompt(context, "football")
    
    print("Промпт для Claude API:")
    print(prompt)