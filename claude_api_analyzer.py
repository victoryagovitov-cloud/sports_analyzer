"""
Анализатор матчей с использованием Claude API от Anthropic
"""
import os
import logging
import json
from typing import List, Dict, Any, Optional
from dataclasses import asdict
import anthropic
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

logger = logging.getLogger(__name__)

class ClaudeAPIAnalyzer:
    """
    Анализатор матчей с использованием официального Claude API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Получаем API ключ из параметров или переменных окружения
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY') or os.getenv('CLAUDE_API_KEY')
        
        if not self.api_key:
            raise ValueError("Claude API ключ не найден. Установите ANTHROPIC_API_KEY или CLAUDE_API_KEY")
        
        # Инициализируем клиент Claude
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.model = "claude-3-haiku-20240307"  # Быстрая и экономичная модель
            self.logger.info("✅ Claude API клиент инициализирован успешно")
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации Claude API: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Тестирует подключение к Claude API
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=50,
                messages=[{
                    "role": "user",
                    "content": "Привет! Ответь кратко: система работает?"
                }]
            )
            
            if response and response.content:
                self.logger.info(f"✅ Claude API тест успешен: {response.content[0].text}")
                return True
            else:
                self.logger.error("❌ Claude API вернул пустой ответ")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка тестирования Claude API: {e}")
            return False
    
    def analyze_matches(self, matches: List[Dict[str, Any]], sport_type: str) -> List[Dict[str, Any]]:
        """
        Анализирует матчи с использованием Claude API
        """
        if not matches:
            self.logger.warning("Нет матчей для анализа")
            return []
        
        try:
            # Формируем промпт для Claude
            matches_data = json.dumps(matches, ensure_ascii=False, indent=2)
            
            prompt = self._get_analysis_prompt(sport_type, matches_data)
            
            # Отправляем запрос к Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.1,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            if not response or not response.content:
                self.logger.error("❌ Claude API вернул пустой ответ")
                return []
            
            # Извлекаем текст ответа
            analysis_text = response.content[0].text
            
            # Парсим результат анализа
            analyzed_matches = self._parse_claude_response(analysis_text, matches)
            
            self.logger.info(f"✅ Claude проанализировал {len(analyzed_matches)} матчей по {sport_type}")
            return analyzed_matches
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка анализа Claude API: {e}")
            return matches  # Возвращаем исходные матчи без анализа
    
    def _get_analysis_prompt(self, sport_type: str, matches_data: str) -> str:
        """
        Генерирует промпт для анализа матчей
        """
        base_prompt = """Ты - эксперт по анализу live-ставок. Проанализируй предоставленные матчи и определи самые выгодные ставки.

КРИТЕРИИ АНАЛИЗА:
"""
        
        if sport_type == 'football':
            criteria = """
ФУТБОЛ:
- Время матча: 25-75 минута (не анализируем начало и конец)
- Разница в турнирной таблице: минимум 5 позиций
- Форма команд: у фаворита минимум 3 победы в последних 5 играх
- Личные встречи: фаворит выигрывал минимум 3 из последних 5 H2H
- Коэффициент: максимум 2.20
- Ставим на победу фаворита (1X2)
"""
        elif sport_type == 'tennis':
            criteria = """
ТЕННИС:
- Разница в рейтинге: минимум 20 позиций
- Форма: у фаворита минимум 4 победы в последних 5 матчах
- H2H: фаворит выигрывал минимум 3 из последних 5 встреч
- Первая подача: у фаворита минимум 65%
- Коэффициент: максимум 1.70
- Ставим на победу фаворита
"""
        elif sport_type == 'handball':
            criteria = """
ГАНДБОЛ:
- Разница в счете: минимум 4 гола в пользу фаворита
- Время: вторая половина матча (после 30 минуты)
- Турнирная таблица: разница минимум 5 позиций
- Средняя результативность: минимум 30 голов за матч
- Коэффициент: максимум 1.45
- Ставим на победу фаворита
"""
        else:
            criteria = "Анализируй по общим принципам: фаворит, форма, статистика, коэффициенты."
        
        return f"""{base_prompt}{criteria}

ФОРМАТ ОТВЕТА:
Для каждого подходящего матча верни JSON:
{{
    "match_id": "ID матча",
    "recommendation": "СТАВКА/ПРОПУСК",
    "bet_type": "тип ставки",
    "confidence": число от 1 до 10,
    "reasoning": "краткое обоснование"
}}

ДАННЫЕ МАТЧЕЙ:
{matches_data}

Анализируй только те матчи, которые полностью соответствуют критериям. Если матч не подходит - пропускай его."""
    
    def _parse_claude_response(self, response_text: str, original_matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Парсит ответ Claude и добавляет рекомендации к исходным матчам
        """
        analyzed_matches = []
        
        try:
            # Пытаемся найти JSON блоки в ответе
            import re
            json_blocks = re.findall(r'\{[^}]*\}', response_text, re.DOTALL)
            
            recommendations = {}
            for block in json_blocks:
                try:
                    rec = json.loads(block)
                    if 'match_id' in rec:
                        recommendations[rec['match_id']] = rec
                except json.JSONDecodeError:
                    continue
            
            # Добавляем рекомендации к исходным матчам
            for match in original_matches:
                match_copy = match.copy()
                match_id = str(match.get('id', ''))
                
                if match_id in recommendations:
                    rec = recommendations[match_id]
                    match_copy.update({
                        'ai_recommendation': rec.get('recommendation', 'ПРОПУСК'),
                        'ai_bet_type': rec.get('bet_type', ''),
                        'ai_confidence': rec.get('confidence', 0),
                        'ai_reasoning': rec.get('reasoning', ''),
                        'analyzed_by': 'claude-api'
                    })
                else:
                    # Если нет рекомендации - пропускаем
                    match_copy.update({
                        'ai_recommendation': 'ПРОПУСК',
                        'ai_bet_type': '',
                        'ai_confidence': 0,
                        'ai_reasoning': 'Не соответствует критериям анализа',
                        'analyzed_by': 'claude-api'
                    })
                
                analyzed_matches.append(match_copy)
            
            return analyzed_matches
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка парсинга ответа Claude: {e}")
            # Возвращаем исходные матчи с отметкой об ошибке
            for match in original_matches:
                match_copy = match.copy()
                match_copy.update({
                    'ai_recommendation': 'ОШИБКА',
                    'ai_bet_type': '',
                    'ai_confidence': 0,
                    'ai_reasoning': 'Ошибка анализа Claude API',
                    'analyzed_by': 'claude-api'
                })
                analyzed_matches.append(match_copy)
            
            return analyzed_matches


# Глобальный экземпляр анализатора
claude_api_analyzer = None

def get_claude_api_analyzer(api_key: Optional[str] = None) -> ClaudeAPIAnalyzer:
    """
    Возвращает глобальный экземпляр анализатора Claude API
    """
    global claude_api_analyzer
    if claude_api_analyzer is None:
        claude_api_analyzer = ClaudeAPIAnalyzer(api_key)
    return claude_api_analyzer


if __name__ == "__main__":
    # Тест анализатора
    print("🧪 Тестирование Claude API анализатора...")
    
    try:
        analyzer = get_claude_api_analyzer()
        
        # Тест подключения
        if analyzer.test_connection():
            print("✅ Подключение к Claude API работает!")
        else:
            print("❌ Проблемы с подключением к Claude API")
            
        # Тест анализа
        test_matches = [
            {
                'id': 'test1',
                'team1': 'Манчестер Сити',
                'team2': 'Уотфорд',
                'score': '2:0',
                'minute': 45,
                'sport': 'football'
            }
        ]
        
        results = analyzer.analyze_matches(test_matches, 'football')
        print(f"✅ Тест анализа: {len(results)} матчей обработано")
        
        if results:
            print(f"Результат: {results[0].get('ai_recommendation', 'Нет рекомендации')}")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")