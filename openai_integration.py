#!/usr/bin/env python3
"""
OpenAI GPT интеграция для анализа live-матчей
"""

import json
import logging
from typing import List, Dict, Any
from openai import OpenAI
from multi_source_controller import MatchData

logger = logging.getLogger(__name__)

class OpenAIAnalyzer:
    """
    Анализатор матчей с использованием OpenAI GPT
    """
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = "gpt-4o-mini"  # Более экономичная модель
        
        # Rate limiting настройки
        self.last_request_time = 0
        self.min_request_interval = 1.5  # 1.5 секунды между запросами
        self.max_retries = 3
        
    def analyze_matches_with_gpt(self, matches: List[MatchData], sport_type: str) -> List[MatchData]:
        """
        Анализирует матчи с помощью OpenAI GPT
        """
        if not matches:
            return []
        
        self.logger.info(f"GPT анализ {len(matches)} матчей для {sport_type}")
        
        # Предфильтрация: оставляем только потенциально подходящие матчи
        filtered_matches = self._prefilter_matches(matches, sport_type)
        self.logger.info(f"После предфильтрации: {len(filtered_matches)} подходящих матчей")
        
        if not filtered_matches:
            self.logger.info("Нет матчей, прошедших предфильтрацию")
            return []
        
        # Ограничиваем количество матчей для экономии токенов
        max_matches = 3
        matches_to_analyze = filtered_matches[:max_matches]
        
        # Создаем детальный промпт
        prompt = self._create_detailed_analysis_prompt(matches_to_analyze, sport_type)
        
        try:
            # Вызываем OpenAI GPT
            gpt_response = self._call_openai_gpt(prompt)
            
            # Обрабатываем ответ GPT
            recommendations = self._process_gpt_response(gpt_response, matches_to_analyze, sport_type)
            
            self.logger.info(f"GPT сгенерировал {len(recommendations)} рекомендаций для {sport_type}")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Ошибка GPT анализа для {sport_type}: {e}")
            # Fallback на эвристический анализ
            return self._fallback_heuristic_analysis(matches_to_analyze, sport_type)
    
    def _create_detailed_analysis_prompt(self, matches: List[MatchData], sport_type: str) -> str:
        """Создает детальный промпт для GPT анализа"""
        
        # Подготавливаем данные матчей
        matches_text = ""
        for i, match in enumerate(matches, 1):
            matches_text += f"{i}. {match.team1} vs {match.team2}\n"
            matches_text += f"   Счет: {match.score}\n"
            matches_text += f"   Минута: {match.minute}\n"
            matches_text += f"   Лига: {match.league}\n\n"
        
        # Правила для каждого вида спорта
        rules = {
            'football': """
            СТРОГИЕ ПРАВИЛА ДЛЯ ФУТБОЛА:
            1. Найди матчи, где одна команда ведет с разрывом ≥1 гол (1:0, 2:1, 3:2, etc.)
            2. ОБЯЗАТЕЛЬНО определи, является ли ведущая команда ЯВНЫМ ФАВОРИТОМ
            3. Время матча должно быть ≥45 минут (минимум второй тайм)
            4. Рекомендуй если вероятность победы фаворита >80% (можно до 85% для особо надежных)
            
            КРИТЕРИИ ЯВНОГО ФАВОРИТА:
            - Позиция в таблице выше на ≥3 места ИЛИ разница в очках ≥10
            - Форма команд: у фаворита ≥4 победы из последних 5 матчей
            - Качество состава: играют основные игроки (не резервный состав)
            - История встреч: фаворит выиграл ≥3 из последних 5 матчей
            - Домашнее преимущество: если фаворит играет дома (+10% к вероятности)
            - Качество лиги: топ-лиги (Premier League, La Liga, Serie A, Bundesliga, Ligue 1) = более надежно
            
            ОСОБЫЕ СЛУЧАИ:
            - Если разрыв ≥2 голов - можно рекомендовать даже при меньшем фаворитизме (>80%)
            - Если время >70 минут - повышается надежность любого преимущества
            - Дерби и принципиальные матчи - повышенная осторожность
            """,
            
            'tennis': """
            СТРОГИЕ ПРАВИЛА ДЛЯ ТЕННИСА:
            1. Найди ТОЛЬКО матчи со счетом 1-0 по сетам ИЛИ разрывом ≥4 геймов в первом сете
            2. Определи, является ли игрок, ведущий в счете, объективным фаворитом
            3. Рекомендуй ТОЛЬКО если вероятность победы фаворита >80%
            
            КРИТЕРИИ ФАВОРИТА:
            - Рейтинг ATP/WTA (разница ≥ 20 позиций)
            - Форма последних 5 матчей (≥ 4 победы у ведущего игрока)
            - История личных встреч (H2H: ≥ 3 победы из 5)
            - Турнир (Grand Slam, ATP Masters более надежны)
            """,
            
            'handball': """
            СТРОГИЕ ПРАВИЛА ДЛЯ ГАНДБОЛА:
            1. Найди ТОЛЬКО матчи, где одна команда ведет с разрывом ≥5 голов
            2. Определи, является ли команда, ведущая в счете, объективным фаворитом
            3. Рекомендуй ТОЛЬКО если вероятность победы фаворита >80%
            
            КРИТЕРИИ ФАВОРИТА:
            - Позиция в таблице (разница ≥ 3 позиций)
            - Форма команд (≥ 4 победы из 5 матчей)
            - Средняя результативность команд
            """
        }
        
        sport_rules = rules.get(sport_type, rules['football'])
        
        prompt = f"""
        Ты - профессиональный эксперт по анализу live-ставок с 10+ летним опытом. 
        Твоя задача - найти ТОЛЬКО самые надежные рекомендации с высокой вероятностью успеха.
        
        {sport_rules}
        
        Проанализируй следующие live-матчи:
        
        {matches_text}
        
        Для каждого подходящего матча дай ДЕТАЛЬНОЕ обоснование, включающее:
        - Анализ текущего счета и времени матча
        - Определение фаворита (рейтинг, позиция в таблице, форма)
        - Историю личных встреч (если известна)
        - Качество турнира/лиги
        - Психологические и тактические факторы
        - Статистические показатели
        
        ВАЖНО: Будь разумно строгим в отборе. Если матч близок к критериям (например, 78% вместо 80%), рассмотри его как потенциальную рекомендацию. Лучше дать честную оценку 78%, чем вообще не дать рекомендацию.
        
        Верни результат СТРОГО в JSON формате:
        [
            {{
                "team1": "Название команды 1",
                "team2": "Название команды 2", 
                "score": "Текущий счет",
                "recommendation": "П1/П2/Победа игрока",
                "confidence": 0.87,
                "reasoning": "ДЕТАЛЬНОЕ обоснование с анализом всех факторов"
            }}
        ]
        
        Если НЕТ матчей, соответствующих строгим критериям, верни пустой массив: []
        """
        
        return prompt
    
    def _prefilter_matches(self, matches: List[MatchData], sport_type: str) -> List[MatchData]:
        """Предварительная фильтрация матчей для экономии токенов"""
        filtered = []
        
        for match in matches:
            if sport_type == 'football':
                if self._is_football_match_worth_analyzing(match):
                    filtered.append(match)
            elif sport_type == 'tennis':
                if self._is_tennis_match_worth_analyzing(match):
                    filtered.append(match)
            elif sport_type == 'handball':
                if self._is_handball_match_worth_analyzing(match):
                    filtered.append(match)
            else:
                filtered.append(match)  # Для остальных видов спорта анализируем все
        
        return filtered
    
    def _is_football_match_worth_analyzing(self, match: MatchData) -> bool:
        """Проверка, стоит ли анализировать футбольный матч"""
        try:
            if ':' not in match.score:
                return False
            
            home_score, away_score = map(int, match.score.split(':'))
            minute_str = getattr(match, 'minute', '0')
            minute = int(minute_str.replace("'", "").replace("′", "")) if minute_str.replace("'", "").replace("′", "").isdigit() else 0
            
            # Базовые критерии
            if home_score == away_score:  # Ничья
                return False
            if minute < 45:  # Слишком рано
                return False
            
            # Проверяем разрыв в счете
            goal_diff = abs(home_score - away_score)
            if goal_diff >= 2:  # Большой разрыв - всегда анализируем
                return True
            if goal_diff == 1 and minute >= 60:  # Малый разрыв только в концовке
                return True
                
            return False
            
        except Exception:
            return False  # При ошибке не анализируем
    
    def _is_tennis_match_worth_analyzing(self, match: MatchData) -> bool:
        """Проверка, стоит ли анализировать теннисный матч"""
        try:
            score = match.score
            # Ищем преимущество по сетам (например, "1-0", "2-1")
            if '-' in score and score.count('-') == 1:
                sets1, sets2 = map(int, score.split('-'))
                return sets1 != sets2  # Есть преимущество по сетам
            return True  # Если формат неясен, анализируем
        except Exception:
            return True
    
    def _is_handball_match_worth_analyzing(self, match: MatchData) -> bool:
        """Проверка, стоит ли анализировать гандбольный матч"""
        try:
            if ':' not in match.score:
                return False
            
            home_score, away_score = map(int, match.score.split(':'))
            goal_diff = abs(home_score - away_score)
            
            return goal_diff >= 3  # Анализируем только при разрыве ≥3 голов
        except Exception:
            return False
    
    def _call_openai_gpt(self, prompt: str) -> str:
        """Вызывает OpenAI GPT API с rate limiting"""
        import time
        
        # Соблюдаем rate limiting
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            self.logger.info(f"⏳ Ожидание {sleep_time:.1f}с для соблюдения rate limit")
            time.sleep(sleep_time)
        
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"📡 OpenAI запрос (попытка {attempt + 1}/{self.max_retries})")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system", 
                            "content": "Ты профессиональный эксперт по спортивным ставкам с 15+ летним опытом. Анализируй строго, но не слишком придирчиво. Отвечай только в JSON формате."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    max_tokens=1500,  # Уменьшили для экономии
                    temperature=0.2,  # Немного повысили для разнообразия
                    timeout=30
                )
                
                self.last_request_time = time.time()
                self.logger.info("✅ OpenAI запрос выполнен успешно")
                return response.choices[0].message.content
                
            except Exception as e:
                self.logger.warning(f"⚠️  Попытка {attempt + 1} неудачна: {e}")
                if attempt < self.max_retries - 1:
                    sleep_time = (attempt + 1) * 2  # Экспоненциальная задержка
                    self.logger.info(f"⏳ Ожидание {sleep_time}с перед повтором...")
                    time.sleep(sleep_time)
                else:
                    self.logger.error(f"❌ Все {self.max_retries} попытки неудачны")
                    raise e
    
    def _process_gpt_response(self, gpt_response: str, original_matches: List[MatchData], sport_type: str = 'football') -> List[MatchData]:
        """Обрабатывает ответ от GPT и создает рекомендации"""
        try:
            # Очищаем ответ от возможного мусора
            gpt_response = gpt_response.strip()
            if gpt_response.startswith('```json'):
                gpt_response = gpt_response[7:]
            if gpt_response.endswith('```'):
                gpt_response = gpt_response[:-3]
            gpt_response = gpt_response.strip()
            
            # Парсим JSON ответ от GPT
            gpt_recommendations = json.loads(gpt_response)
            
            recommendations = []
            
            for gpt_rec in gpt_recommendations:
                # Находим соответствующий оригинальный матч
                original_match = self._find_matching_match(gpt_rec, original_matches)
                
                if original_match:
                    # Создаем рекомендацию на основе ответа GPT
                    recommendation = self._create_recommendation_from_gpt(original_match, gpt_rec, sport_type)
                    recommendations.append(recommendation)
            
            return recommendations
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Ошибка парсинга JSON ответа GPT: {e}")
            self.logger.error(f"Ответ GPT: {gpt_response}")
            return []
        except Exception as e:
            self.logger.error(f"Ошибка обработки ответа GPT: {e}")
            return []
    
    def _find_matching_match(self, gpt_rec: Dict[str, Any], original_matches: List[MatchData]) -> MatchData:
        """Находит соответствующий оригинальный матч по данным от GPT"""
        for match in original_matches:
            if (match.team1 == gpt_rec.get('team1') and 
                match.team2 == gpt_rec.get('team2') and
                match.score == gpt_rec.get('score')):
                return match
        return None
    
    def _create_recommendation_from_gpt(self, original_match: MatchData, gpt_rec: Dict[str, Any], sport_type: str = 'football') -> MatchData:
        """Создает рекомендацию на основе ответа GPT"""
        # Копируем оригинальный матч
        recommendation = MatchData(
            sport=getattr(original_match, 'sport', sport_type),
            team1=original_match.team1,
            team2=original_match.team2,
            score=original_match.score,
            minute=getattr(original_match, 'minute', ''),
            league=getattr(original_match, 'league', ''),
            link=getattr(original_match, 'link', ''),
            source=getattr(original_match, 'source', '')
        )
        
        # Добавляем данные от GPT
        recommendation.probability = gpt_rec.get('confidence', 0) * 100
        recommendation.recommendation_type = 'win'
        recommendation.recommendation_value = gpt_rec.get('recommendation', '')
        recommendation.justification = gpt_rec.get('reasoning', '')
        
        return recommendation
    
    def _fallback_heuristic_analysis(self, matches: List[MatchData], sport_type: str) -> List[MatchData]:
        """Fallback эвристический анализ при проблемах с GPT"""
        self.logger.warning("Используем fallback эвристический анализ")
        
        recommendations = []
        
        for match in matches:
            if sport_type == 'football':
                rec = self._analyze_football_heuristic(match)
                if rec:
                    recommendations.append(rec)
        
        return recommendations
    
    def _analyze_football_heuristic(self, match: MatchData) -> MatchData:
        """Упрощенный анализ футбольного матча"""
        try:
            if ':' not in match.score:
                return None
                
            home_score, away_score = map(int, match.score.split(':'))
            minute_int = int(match.minute.replace("'", "").replace("′", "")) if match.minute.replace("'", "").replace("′", "").isdigit() else 0
            
            # Базовые проверки
            if home_score == away_score or minute_int < 45:
                return None
            
            # Определяем ведущую команду
            if home_score > away_score:
                leading_team = match.team1
                recommendation = 'П1'
                goal_difference = home_score - away_score
            else:
                leading_team = match.team2
                recommendation = 'П2'
                goal_difference = away_score - home_score
            
            # Простая проверка фаворитизма
            top_teams = ['Manchester City', 'Arsenal', 'Liverpool', 'Chelsea', 'Manchester United',
                        'Barcelona', 'Real Madrid', 'Atletico Madrid', 'Bayern Munich', 'Borussia Dortmund',
                        'PSG', 'Milan', 'Inter', 'Juventus', 'Napoli']
            
            is_top_team = any(top_team.lower() in leading_team.lower() for top_team in top_teams)
            
            # Логика принятия решения
            if goal_difference >= 2 or (goal_difference == 1 and is_top_team and minute_int > 60):
                confidence = min(0.85 + (goal_difference - 1) * 0.05 + (minute_int - 60) * 0.002, 0.95)
                
                # Создаем рекомендацию
                rec = MatchData(
                    sport=getattr(match, 'sport', 'football'),
                    team1=match.team1,
                    team2=match.team2,
                    score=match.score,
                    minute=getattr(match, 'minute', ''),
                    league=getattr(match, 'league', ''),
                    link=getattr(match, 'link', ''),
                    source=getattr(match, 'source', '')
                )
                
                rec.probability = confidence * 100
                rec.recommendation_type = 'win'
                rec.recommendation_value = recommendation
                rec.justification = f"Команда {leading_team} ведет {goal_difference} гол(а) на {minute_int} минуте. Уверенность: {confidence:.1%}"
                
                return rec
            
            return None
            
        except Exception as e:
            self.logger.error(f"Ошибка эвристического анализа: {e}")
            return None

    def test_connection(self) -> bool:
        """Тестирует подключение к OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=10,
                timeout=10
            )
            self.logger.info("✅ OpenAI API подключение работает")
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка подключения к OpenAI API: {e}")
            return False