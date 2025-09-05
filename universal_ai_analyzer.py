"""
Универсальный AI анализатор с поддержкой нескольких провайдеров
Работает с Claude API, OpenAI, и эвристическими методами
"""
import os
import logging
import json
from typing import List, Dict, Any, Optional
from dataclasses import asdict
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

logger = logging.getLogger(__name__)

class UniversalAIAnalyzer:
    """
    Универсальный анализатор с поддержкой нескольких AI провайдеров
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.active_provider = None
        self.providers = {}
        
        # Инициализируем доступных провайдеров
        self._init_providers()
        
    def _init_providers(self):
        """Инициализируем доступных AI провайдеров"""
        
        # 1. Пробуем Claude API
        try:
            claude_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('CLAUDE_API_KEY')
            if claude_key:
                import anthropic
                client = anthropic.Anthropic(api_key=claude_key)
                # Тестируем подключение
                response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "test"}]
                )
                self.providers['claude'] = client
                self.active_provider = 'claude'
                self.logger.info("✅ Claude API активен")
        except Exception as e:
            self.logger.warning(f"⚠️  Claude API недоступен: {e}")
        
        # 2. Пробуем OpenAI API
        try:
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                # Тестируем подключение
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=10
                )
                self.providers['openai'] = client
                if not self.active_provider:
                    self.active_provider = 'openai'
                self.logger.info("✅ OpenAI API активен")
        except Exception as e:
            self.logger.warning(f"⚠️  OpenAI API недоступен: {e}")
        
        # 3. Всегда доступен эвристический анализатор
        self.providers['heuristic'] = True
        if not self.active_provider:
            self.active_provider = 'heuristic'
            self.logger.info("✅ Эвристический анализатор активен")
        
        self.logger.info(f"🎯 Активный провайдер: {self.active_provider}")
        self.logger.info(f"📊 Доступные провайдеры: {list(self.providers.keys())}")
    
    def test_connection(self) -> Dict[str, bool]:
        """Тестирует подключение ко всем провайдерам"""
        results = {}
        
        for provider in self.providers:
            try:
                if provider == 'claude' and 'claude' in self.providers:
                    response = self.providers['claude'].messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=20,
                        messages=[{"role": "user", "content": "Привет! Система работает?"}]
                    )
                    results[provider] = True
                    
                elif provider == 'openai' and 'openai' in self.providers:
                    response = self.providers['openai'].chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": "Привет! Система работает?"}],
                        max_tokens=20
                    )
                    results[provider] = True
                    
                elif provider == 'heuristic':
                    results[provider] = True
                    
            except Exception as e:
                results[provider] = False
                self.logger.error(f"❌ Ошибка тестирования {provider}: {e}")
        
        return results
    
    def analyze_matches(self, matches: List[Dict[str, Any]], sport_type: str) -> List[Dict[str, Any]]:
        """Анализирует матчи используя лучший доступный провайдер"""
        
        if not matches:
            self.logger.warning("Нет матчей для анализа")
            return []
        
        # Выбираем метод анализа в зависимости от активного провайдера
        if self.active_provider == 'claude':
            return self._analyze_with_claude(matches, sport_type)
        elif self.active_provider == 'openai':
            return self._analyze_with_openai(matches, sport_type)
        else:
            return self._analyze_with_heuristics(matches, sport_type)
    
    def _analyze_with_claude(self, matches: List[Dict[str, Any]], sport_type: str) -> List[Dict[str, Any]]:
        """Анализ с использованием Claude API"""
        try:
            matches_data = json.dumps(matches, ensure_ascii=False, indent=2)
            prompt = self._get_analysis_prompt(sport_type, matches_data)
            
            response = self.providers['claude'].messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1500,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            analysis_text = response.content[0].text
            analyzed_matches = self._parse_ai_response(analysis_text, matches, 'claude')
            
            self.logger.info(f"✅ Claude проанализировал {len(analyzed_matches)} матчей по {sport_type}")
            return analyzed_matches
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка анализа Claude: {e}")
            return self._analyze_with_heuristics(matches, sport_type)
    
    def _analyze_with_openai(self, matches: List[Dict[str, Any]], sport_type: str) -> List[Dict[str, Any]]:
        """Анализ с использованием OpenAI API"""
        try:
            matches_data = json.dumps(matches, ensure_ascii=False, indent=2)
            prompt = self._get_analysis_prompt(sport_type, matches_data)
            
            response = self.providers['openai'].chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.1
            )
            
            analysis_text = response.choices[0].message.content
            analyzed_matches = self._parse_ai_response(analysis_text, matches, 'openai')
            
            self.logger.info(f"✅ OpenAI проанализировал {len(analyzed_matches)} матчей по {sport_type}")
            return analyzed_matches
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка анализа OpenAI: {e}")
            return self._analyze_with_heuristics(matches, sport_type)
    
    def _analyze_with_heuristics(self, matches: List[Dict[str, Any]], sport_type: str) -> List[Dict[str, Any]]:
        """Эвристический анализ без AI API"""
        analyzed_matches = []
        
        for match in matches:
            match_copy = match.copy()
            
            # Простые эвристические правила
            recommendation = "ПРОПУСК"
            confidence = 0
            reasoning = "Эвристический анализ"
            
            try:
                # Получаем данные матча
                score = match.get('score', '0:0')
                minute = match.get('minute', 0)
                team1 = match.get('team1', '')
                team2 = match.get('team2', '')
                
                if sport_type == 'football':
                    # Простые правила для футбола
                    if 25 <= minute <= 75:  # Временное окно
                        score_parts = score.split(':')
                        if len(score_parts) == 2:
                            score1, score2 = int(score_parts[0]), int(score_parts[1])
                            goal_diff = abs(score1 - score2)
                            
                            if goal_diff >= 2:  # Разница в 2+ гола
                                recommendation = "СТАВКА"
                                confidence = 7
                                reasoning = f"Разница в счете {goal_diff} гола на {minute} минуте"
                
                elif sport_type == 'tennis':
                    # Простые правила для тенниса
                    if score and ':' in score:
                        # Анализируем счет в теннисе
                        recommendation = "СТАВКА"
                        confidence = 6
                        reasoning = "Теннисный матч в процессе"
                
                elif sport_type == 'handball':
                    # Простые правила для гандбола
                    if minute >= 30:  # Вторая половина
                        score_parts = score.split(':')
                        if len(score_parts) == 2:
                            score1, score2 = int(score_parts[0]), int(score_parts[1])
                            goal_diff = abs(score1 - score2)
                            
                            if goal_diff >= 4:  # Разница в 4+ гола
                                recommendation = "СТАВКА"
                                confidence = 8
                                reasoning = f"Разница в счете {goal_diff} голов во второй половине"
                
            except Exception as e:
                self.logger.warning(f"Ошибка эвристического анализа: {e}")
            
            match_copy.update({
                'ai_recommendation': recommendation,
                'ai_bet_type': 'Победа фаворита' if recommendation == 'СТАВКА' else '',
                'ai_confidence': confidence,
                'ai_reasoning': reasoning,
                'analyzed_by': 'heuristic'
            })
            
            analyzed_matches.append(match_copy)
        
        self.logger.info(f"✅ Эвристический анализ завершен: {len(analyzed_matches)} матчей")
        return analyzed_matches
    
    def _get_analysis_prompt(self, sport_type: str, matches_data: str) -> str:
        """Генерирует промпт для AI анализа"""
        base_prompt = """Ты - эксперт по анализу live-ставок. Проанализируй матчи и определи выгодные ставки.

КРИТЕРИИ:"""
        
        if sport_type == 'football':
            criteria = """
ФУТБОЛ:
- Время: 25-75 минута
- Разница в счете: минимум 2 гола
- Коэффициент: до 2.20
- Ставим на победу лидирующей команды
"""
        elif sport_type == 'tennis':
            criteria = """
ТЕННИС:
- Анализируем текущий счет
- Форму игроков
- Коэффициент: до 1.70
- Ставим на победу фаворита
"""
        elif sport_type == 'handball':
            criteria = """
ГАНДБОЛ:
- Время: после 30 минуты
- Разница: минимум 4 гола
- Коэффициент: до 1.45
- Ставим на победу лидера
"""
        else:
            criteria = "Анализируй по общим принципам"
        
        return f"""{base_prompt}{criteria}

ФОРМАТ ОТВЕТА (JSON):
{{"match_id": "ID", "recommendation": "СТАВКА/ПРОПУСК", "confidence": 1-10, "reasoning": "обоснование"}}

МАТЧИ:
{matches_data}"""
    
    def _parse_ai_response(self, response_text: str, original_matches: List[Dict[str, Any]], provider: str) -> List[Dict[str, Any]]:
        """Парсит ответ AI и добавляет рекомендации"""
        analyzed_matches = []
        
        try:
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
            
            for match in original_matches:
                match_copy = match.copy()
                match_id = str(match.get('id', ''))
                
                if match_id in recommendations:
                    rec = recommendations[match_id]
                    match_copy.update({
                        'ai_recommendation': rec.get('recommendation', 'ПРОПУСК'),
                        'ai_bet_type': 'Победа фаворита' if rec.get('recommendation') == 'СТАВКА' else '',
                        'ai_confidence': rec.get('confidence', 0),
                        'ai_reasoning': rec.get('reasoning', ''),
                        'analyzed_by': provider
                    })
                else:
                    match_copy.update({
                        'ai_recommendation': 'ПРОПУСК',
                        'ai_bet_type': '',
                        'ai_confidence': 0,
                        'ai_reasoning': 'Не соответствует критериям',
                        'analyzed_by': provider
                    })
                
                analyzed_matches.append(match_copy)
            
            return analyzed_matches
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка парсинга ответа {provider}: {e}")
            # Возвращаем с эвристическим анализом
            return self._analyze_with_heuristics(original_matches, "general")


# Глобальный экземпляр анализатора
universal_analyzer = None

def get_universal_analyzer() -> UniversalAIAnalyzer:
    """Возвращает глобальный экземпляр универсального анализатора"""
    global universal_analyzer
    if universal_analyzer is None:
        universal_analyzer = UniversalAIAnalyzer()
    return universal_analyzer


if __name__ == "__main__":
    # Тест анализатора
    print("🧪 Тестирование универсального AI анализатора...")
    
    try:
        analyzer = get_universal_analyzer()
        
        # Тест подключения
        results = analyzer.test_connection()
        print("📊 Результаты тестирования провайдеров:")
        for provider, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {provider}: {'работает' if status else 'недоступен'}")
        
        # Тест анализа
        test_matches = [
            {
                'id': 'test1',
                'team1': 'Барселона',
                'team2': 'Реал Мадрид',
                'score': '2:0',
                'minute': 45,
                'sport': 'football'
            },
            {
                'id': 'test2', 
                'team1': 'Джокович',
                'team2': 'Федерер',
                'score': '6:4 2:1',
                'minute': 0,
                'sport': 'tennis'
            }
        ]
        
        results = analyzer.analyze_matches(test_matches, 'football')
        print(f"\n✅ Тест анализа: {len(results)} матчей обработано")
        
        for match in results:
            print(f"  📈 {match.get('team1')} vs {match.get('team2')}: {match.get('ai_recommendation')}")
            print(f"     Уверенность: {match.get('ai_confidence')}/10")
            print(f"     Обоснование: {match.get('ai_reasoning')}")
            print(f"     Анализатор: {match.get('analyzed_by')}")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")