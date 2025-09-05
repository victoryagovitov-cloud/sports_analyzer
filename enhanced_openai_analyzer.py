#!/usr/bin/env python3
"""
Улучшенный OpenAI анализатор с новой логикой анализа
"""

import json
import logging
import time
from typing import List, Dict, Any
from openai import OpenAI
from multi_source_controller import MatchData

logger = logging.getLogger(__name__)

class EnhancedOpenAIAnalyzer:
    """
    Улучшенный анализатор матчей с глубоким анализом и новыми критериями
    """
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = "gpt-4o-mini"
        
        # Rate limiting настройки
        self.last_request_time = 0
        self.min_request_interval = 2.0  # 2 секунды между запросами
        self.max_retries = 3
        
    def analyze_matches_with_enhanced_gpt(self, matches: List[MatchData], sport_type: str) -> List[MatchData]:
        """
        Улучшенный анализ матчей с глубокой проверкой критериев
        """
        if not matches:
            return []
        
        self.logger.info(f"🤖 Улучшенный GPT анализ {len(matches)} матчей для {sport_type}")
        
        # Предфильтрация с новыми критериями
        filtered_matches = self._enhanced_prefilter(matches, sport_type)
        self.logger.info(f"После улучшенной предфильтрации: {len(filtered_matches)} подходящих матчей")
        
        if not filtered_matches:
            return []
        
        # Анализируем только лучшие матчи
        max_matches = 3
        matches_to_analyze = filtered_matches[:max_matches]
        
        recommendations = []
        
        # Анализируем каждый матч отдельно для более точного анализа
        for match in matches_to_analyze:
            try:
                recommendation = self._analyze_single_match_enhanced(match, sport_type)
                if recommendation:
                    recommendations.append(recommendation)
            except Exception as e:
                self.logger.error(f"Ошибка анализа матча {match.team1} vs {match.team2}: {e}")
                continue
        
        self.logger.info(f"✅ Улучшенный анализ сгенерировал {len(recommendations)} рекомендаций для {sport_type}")
        return recommendations
    
    def _enhanced_prefilter(self, matches: List[MatchData], sport_type: str) -> List[MatchData]:
        """Улучшенная предфильтрация с новыми критериями"""
        filtered = []
        
        for match in matches:
            if sport_type == 'football':
                if self._is_football_match_enhanced_worthy(match):
                    filtered.append(match)
            elif sport_type == 'tennis':
                if self._is_tennis_match_enhanced_worthy(match):
                    filtered.append(match)
            elif sport_type == 'table_tennis':
                if self._is_table_tennis_match_enhanced_worthy(match):
                    filtered.append(match)
            elif sport_type == 'handball':
                if self._is_handball_match_enhanced_worthy(match):
                    filtered.append(match)
        
        return filtered
    
    def _is_football_match_enhanced_worthy(self, match: MatchData) -> bool:
        """Проверка футбольного матча по новым критериям"""
        try:
            if ':' not in match.score:
                return False
            
            home_score, away_score = map(int, match.score.split(':'))
            minute_str = getattr(match, 'minute', '0')
            minute = int(minute_str.replace("'", "").replace("′", "")) if minute_str.replace("'", "").replace("′", "").isdigit() else 0
            
            # Новые критерии: 25-75 минута, не ничейный счет
            if home_score == away_score:  # Ничья
                return False
            if minute < 25 or minute > 75:  # Вне временного окна
                return False
            
            return True
            
        except Exception:
            return False
    
    def _is_tennis_match_enhanced_worthy(self, match: MatchData) -> bool:
        """Проверка теннисного матча по критериям промпта"""
        try:
            score = match.score
            minute = getattr(match, 'minute', '')
            
            # По промпту: "Ведущий выиграл первый сет или разрыв ≥ 3 гейма"
            
            # Проверяем разные форматы счета
            if '-' in score and score.count('-') == 1:
                # Формат "1-0", "2-1" - преимущество по сетам
                try:
                    sets1, sets2 = map(int, score.split('-'))
                    if sets1 != sets2:  # Есть преимущество по сетам
                        return True
                except ValueError:
                    pass
            
            # Проверяем формат с геймами в скобках "1-0 (6-4, 3-2)"
            if '(' in score and ')' in score:
                return True  # Детальный счет = анализируем
            
            # Проверяем статус матча по минуте
            if minute and any(keyword in minute.lower() for keyword in ['сет', 'set', 'партия']):
                # Если указан номер сета - анализируем
                return True
            
            # Если счет "0:0" и идет первый сет - НЕ анализируем (нет преимущества)
            if score == "0:0" and "1-й сет" in minute:
                return False
                
            return False  # Остальные не анализируем
            
        except Exception:
            return False  # При ошибке не анализируем
    
    def _is_table_tennis_match_enhanced_worthy(self, match: MatchData) -> bool:
        """Проверка настольного тенниса по критериям промпта"""
        try:
            score = match.score
            
            # По промпту: "Ведущий 1:0 или 2:0 по сетам"
            
            if ':' in score:
                try:
                    sets1, sets2 = map(int, score.split(':'))
                    # Ищем преимущество 1:0 или 2:0 (в любую сторону)
                    return (sets1 == 1 and sets2 == 0) or (sets1 == 2 and sets2 == 0) or \
                           (sets1 == 0 and sets2 == 1) or (sets1 == 0 and sets2 == 2)
                except ValueError:
                    pass
            
            # Проверяем формат с дефисом "1-0", "2-0"  
            if '-' in score and score.count('-') == 1:
                try:
                    sets1, sets2 = map(int, score.split('-'))
                    return (sets1 == 1 and sets2 == 0) or (sets1 == 2 and sets2 == 0) or \
                           (sets1 == 0 and sets2 == 1) or (sets1 == 0 and sets2 == 2)
                except ValueError:
                    pass
            
            return False
            
        except Exception:
            return False
    
    def _is_handball_match_enhanced_worthy(self, match: MatchData) -> bool:
        """Проверка гандбольного матча по новым критериям"""
        try:
            if ':' not in match.score:
                return False
            
            home_score, away_score = map(int, match.score.split(':'))
            minute_str = getattr(match, 'minute', '0')
            minute = int(minute_str.replace("'", "").replace("′", "")) if minute_str.replace("'", "").replace("′", "").isdigit() else 0
            
            # Ведущий ≥4 мяча, вторая половина (>30 мин)
            goal_diff = abs(home_score - away_score)
            return goal_diff >= 4 and minute > 30
            
        except Exception:
            return False
    
    def _analyze_single_match_enhanced(self, match: MatchData, sport_type: str) -> MatchData:
        """Улучшенный анализ одного матча"""
        try:
            # Создаем специализированный промпт для конкретного матча
            prompt = self._create_enhanced_match_prompt(match, sport_type)
            
            # Вызываем GPT
            gpt_response = self._call_openai_gpt_enhanced(prompt)
            
            # Обрабатываем ответ
            analysis_result = self._process_single_match_response(gpt_response, match, sport_type)
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Ошибка улучшенного анализа матча: {e}")
            return None
    
    def _create_enhanced_match_prompt(self, match: MatchData, sport_type: str) -> str:
        """Создает улучшенный промпт для анализа конкретного матча"""
        
        base_match_info = f"""
        Матч: {match.team1} vs {match.team2}
        Счет: {match.score}
        Минута: {match.minute}
        Лига: {match.league}
        """
        
        if sport_type == 'football':
            criteria_prompt = f"""
            Ты - профессиональный аналитик футбольных ставок с 15+ летним опытом.
            
            АНАЛИЗИРУЕМЫЙ МАТЧ:
            {base_match_info}
            
            НОВЫЕ СТРОГИЕ КРИТЕРИИ ДЛЯ ФУТБОЛА:
            1. Время матча: 25-75 минута (оптимальное окно для анализа)
            2. Счет: НЕ ничейный (кто-то должен вести)
            3. Анализ фаворитизма: ОБЯЗАТЕЛЬНО определи явного фаворита
            
            КРИТЕРИИ ФАВОРИТА (нужно минимум 3 из 5):
            ✅ Разница в таблице ≥ 5 позиций
            ✅ Форма: ≥ 3 победы в последних 5 играх  
            ✅ H2H: ≥ 3 победы из 5 встреч
            ✅ xG ≥ 1.5 у фаворита (если доступно)
            ✅ Коэффициент ≤ 2.20
            
            ДОПОЛНИТЕЛЬНЫЕ ФАКТОРЫ:
            - Качество лиги (топ-лиги более надежны)
            - Домашнее преимущество
            - Мотивация команд (борьба за титул/против вылета)
            - Травмы ключевых игроков
            - Тактические особенности
            
            ЗАДАЧА: Проанализируй этот матч и определи:
            1. Является ли ведущая команда явным фаворитом?
            2. Какова вероятность её победы (честная оценка)?
            3. Стоит ли рекомендовать ставку?
            
            ОБОСНОВАНИЕ: Пиши КРАТКО (максимум 15-20 слов), только суть.
            
            Верни JSON:
            {{
                "is_favorite": true/false,
                "confidence": 0.82,
                "recommendation": "П1/П2/НЕТ",
                "reasoning": "Краткое обоснование (15-20 слов максимум)"
            }}
            """
            
        elif sport_type == 'tennis':
            criteria_prompt = f"""
            Ты - профессиональный аналитик теннисных ставок.
            
            АНАЛИЗИРУЕМЫЙ МАТЧ:
            {base_match_info}
            
            КРИТЕРИИ ДЛЯ ТЕННИСА:
            1. Преимущество: Ведущий выиграл первый сет ИЛИ разрыв ≥ 3 гейма
            2. Анализ фаворитизма по критериям:
            
            КРИТЕРИИ ФАВОРИТА (нужно минимум 3 из 5):
            ✅ Разница в рейтинге ≥ 20 позиций
            ✅ Форма: ≥ 4 победы в последних 5 матчах
            ✅ H2H: ≥ 3 победы из 5 встреч  
            ✅ Первые подачи ≥ 65%
            ✅ Коэффициент ≤ 1.70
            
            ОБОСНОВАНИЕ: Максимум 15-20 слов, только суть.
            
            Верни JSON: {{"is_favorite": true/false, "confidence": 0.80, "recommendation": "Победа игрока/НЕТ", "reasoning": "Краткое обоснование"}}
            """
            
        elif sport_type == 'handball':
            criteria_prompt = f"""
            Ты - профессиональный аналитик гандбольных ставок.
            
            АНАЛИЗИРУЕМЫЙ МАТЧ:
            {base_match_info}
            
            КРИТЕРИИ ДЛЯ ГАНДБОЛА:
            1. Преимущество: Ведущий ≥ 4 мяча, вторая половина
            2. Анализ фаворитизма + расчет тоталов
            
            КРИТЕРИИ ФАВОРИТА:
            ✅ Разница в таблице ≥ 5 позиций
            ✅ Форма: ≥ 4 победы в последних 5 играх
            ✅ H2H: ≥ 4 победы из 5 встреч
            ✅ Средняя результативность ≥ 30 мячей
            ✅ Коэффициент ≤ 1.45
            
            РАСЧЕТ ТОТАЛОВ:
            Формула: ОКРУГЛВВЕРХ((Голы1 + Голы2) / (30 + Минута_Второй_Половины) * 60)
            - Голы > минуты → ТБ [Значение - 4]
            - Голы < минуты → ТМ [Значение + 3]
            
            ОБОСНОВАНИЕ: Максимум 15-20 слов, только суть.
            
            Верни JSON: {{"is_favorite": true/false, "confidence": 0.80, "recommendation": "П1/П2/НЕТ", "reasoning": "Краткое обоснование"}}
            """
        
        else:
            criteria_prompt = base_match_info
        
        return criteria_prompt
    
    def _call_openai_gpt_enhanced(self, prompt: str) -> str:
        """Улучшенный вызов OpenAI GPT API"""
        # Соблюдаем rate limiting
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system", 
                            "content": "Ты профессиональный аналитик спортивных ставок. Анализируй честно и профессионально. Отвечай только в JSON формате."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    max_tokens=800,  # Достаточно для детального анализа одного матча
                    temperature=0.2,
                    timeout=30
                )
                
                self.last_request_time = time.time()
                return response.choices[0].message.content
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    sleep_time = (attempt + 1) * 3
                    self.logger.warning(f"⚠️  Попытка {attempt + 1} неудачна, ожидание {sleep_time}с: {e}")
                    time.sleep(sleep_time)
                else:
                    raise e
    
    def _process_single_match_response(self, gpt_response: str, match: MatchData, sport_type: str) -> MatchData:
        """Обрабатывает ответ GPT для одного матча"""
        try:
            # Очищаем ответ
            gpt_response = gpt_response.strip()
            if gpt_response.startswith('```json'):
                gpt_response = gpt_response[7:]
            if gpt_response.endswith('```'):
                gpt_response = gpt_response[:-3]
            gpt_response = gpt_response.strip()
            
            # Парсим JSON
            analysis = json.loads(gpt_response)
            
            # Проверяем, рекомендуется ли ставка
            if not analysis.get('is_favorite', False):
                return None
            
            recommendation_value = analysis.get('recommendation', 'НЕТ')
            if recommendation_value == 'НЕТ':
                return None
            
            confidence = analysis.get('confidence', 0)
            if confidence < 0.75:  # Минимум 75% уверенности
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
                source=getattr(match, 'source', 'enhanced_gpt')
            )
            
            recommendation.probability = confidence * 100
            recommendation.recommendation_type = 'win'
            recommendation.recommendation_value = recommendation_value
            recommendation.justification = analysis.get('reasoning', 'GPT анализ')
            
            return recommendation
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Ошибка парсинга JSON ответа: {e}")
            self.logger.error(f"Ответ GPT: {gpt_response}")
            return None
        except Exception as e:
            self.logger.error(f"Ошибка обработки ответа: {e}")
            return None
    
    def calculate_totals_enhanced(self, match: MatchData) -> Dict:
        """Расчет тоталов по новой формуле"""
        try:
            if ':' not in match.score:
                return {}
            
            home_score, away_score = map(int, match.score.split(':'))
            minute_str = getattr(match, 'minute', '0')
            minute = int(minute_str.replace("'", "").replace("′", "")) if minute_str.replace("'", "").replace("′", "").isdigit() else 0
            
            total_goals = home_score + away_score
            
            # Новая формула: ОКРУГЛВВЕРХ((Голы1 + Голы2) / (30 + Минута_Второй_Половины) * 60)
            if minute > 45:  # Вторая половина
                second_half_minute = minute - 45
                predicted_total = ((total_goals) / (30 + second_half_minute)) * 60
                predicted_total = int(predicted_total) + (1 if predicted_total % 1 > 0 else 0)
                
                # Рекомендации по тоталам
                if total_goals > minute:  # Быстрый темп
                    recommendation = f"ТБ {predicted_total - 4}"
                    tempo = "БЫСТРЫЙ"
                else:  # Медленный темп
                    recommendation = f"ТМ {predicted_total + 3}"
                    tempo = "МЕДЛЕННЫЙ"
                
                return {
                    'predicted_total': predicted_total,
                    'recommendation': recommendation,
                    'tempo': tempo,
                    'current_goals': total_goals,
                    'minute': minute
                }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Ошибка расчета тоталов: {e}")
            return {}
    
    def generate_enhanced_reasoning(self, match: MatchData, sport_type: str, additional_stats: Dict = None) -> str:
        """Генерирует улучшенное обоснование с помощью GPT"""
        try:
            stats_text = ""
            if additional_stats:
                stats_text = f"Дополнительная статистика: {additional_stats}"
            
            reasoning_prompt = f"""
            Создай краткое (2-3 предложения), профессиональное обоснование для ставки.
            
            Матч: {match.team1} vs {match.team2} ({match.score}, {match.minute}')
            Лига: {match.league}
            Рекомендация: {match.recommendation_value}
            {stats_text}
            
            Требования:
            - Тон: профессиональный, уверенный, без эмоций
            - Длина: 2-3 предложения
            - Упомяни ключевые факторы: счет, время, статистику
            - Объясни, почему это хорошая ставка
            
            Верни только текст обоснования без JSON.
            """
            
            response = self._call_openai_gpt_enhanced(reasoning_prompt)
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации обоснования: {e}")
            return f"Анализ матча {match.team1} vs {match.team2}: ведущая команда имеет преимущество в счете {match.score} на {match.minute} минуте."

    def test_enhanced_connection(self) -> bool:
        """Тестирует улучшенное подключение к OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Тест улучшенной системы анализа"}],
                max_tokens=20,
                timeout=10
            )
            self.logger.info("✅ Улучшенный OpenAI анализатор готов к работе")
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка подключения улучшенного анализатора: {e}")
            return False