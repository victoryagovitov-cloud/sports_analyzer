import json
import logging
import os
from typing import List, Dict, Any
from multi_source_controller import MatchData
from config import ANALYSIS_SETTINGS

# Загружаем переменные окружения из .env файла
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv не обязательна

logger = logging.getLogger(__name__)

class ClaudeFinalIntegration:
    """
    Финальная интеграция с Claude для анализа матчей
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Приоритет: Cursor Claude (бесплатно) -> OpenAI (платно) -> эвристический
        
        # Отключаем экспериментальный Claude (по запросу пользователя)
        self.use_cursor_claude = ANALYSIS_SETTINGS.get('use_cursor_claude', False)
        if self.use_cursor_claude:
            try:
                from cursor_claude_analyzer import cursor_claude_analyzer
                self.cursor_claude = cursor_claude_analyzer
                self.logger.info("🆓 БЕСПЛАТНЫЙ Claude через Cursor активирован!")
            except ImportError:
                self.use_cursor_claude = False
                self.logger.warning("⚠️  Cursor Claude анализатор не найден")
        else:
            self.logger.info("Claude через Cursor отключен в настройках")
        
        # Затем проверяем OpenAI как fallback
        if ANALYSIS_SETTINGS.get('use_openai_gpt', False):
            try:
                # Пробуем использовать улучшенный анализатор
                from enhanced_openai_analyzer import EnhancedOpenAIAnalyzer
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    self.openai_analyzer = EnhancedOpenAIAnalyzer(api_key)
                    self.use_openai = True
                    self.use_enhanced = True
                    self.logger.info("✅ Улучшенный OpenAI анализатор активирован")
                    
                    # Добавляем анализатор с внешними знаниями
                    try:
                        from external_knowledge_analyzer import get_external_knowledge_analyzer
                        self.external_analyzer = get_external_knowledge_analyzer(api_key)
                        self.use_external_knowledge = True
                        self.logger.info("🌐 Анализатор с внешними знаниями активирован")
                    except ImportError:
                        self.use_external_knowledge = False
                else:
                    self.use_openai = False
                    self.use_enhanced = False
                    self.use_external_knowledge = False
                    self.logger.warning("⚠️  OpenAI API ключ не найден, используем эвристический анализ")
            except ImportError:
                try:
                    # Fallback на обычный анализатор
                    from openai_integration import OpenAIAnalyzer
                    api_key = os.getenv('OPENAI_API_KEY')
                    if api_key:
                        self.openai_analyzer = OpenAIAnalyzer(api_key)
                        self.use_openai = True
                        self.use_enhanced = False
                        self.use_external_knowledge = False
                        self.logger.info("✅ Базовый OpenAI анализатор активирован")
                    else:
                        self.use_openai = False
                        self.use_enhanced = False
                        self.use_external_knowledge = False
                except ImportError:
                    self.use_openai = False
                    self.use_enhanced = False
                    self.use_external_knowledge = False
                    self.logger.warning("⚠️  OpenAI библиотека не найдена, используем эвристический анализ")
        else:
            self.use_openai = False
            self.use_enhanced = False
            self.use_external_knowledge = False
            self.logger.info("OpenAI отключен в настройках, используем эвристический анализ")
    
    def analyze_matches_with_claude(self, matches: List[MatchData], sport_type: str) -> List[MatchData]:
        """
        Анализирует матчи с помощью AI (OpenAI GPT или эвристический анализ)
        """
        if not matches:
            return []
        
        # Приоритет анализаторов: Claude (бесплатно) -> OpenAI (платно) -> эвристический
        
        # Сначала пробуем бесплатный Claude через Cursor
        if self.use_cursor_claude:
            try:
                self.logger.info("🆓 Используем БЕСПЛАТНЫЙ Claude через Cursor")
                return self.cursor_claude.analyze_matches_with_cursor_claude(matches, sport_type)
            except Exception as e:
                self.logger.error(f"Ошибка Cursor Claude, переключаемся на OpenAI: {e}")
        
        # Fallback на OpenAI GPT если доступен
        if self.use_openai:
            try:
                # Пробуем анализ с внешними знаниями (приоритет)
                if self.use_external_knowledge:
                    self.logger.info("🌐 Используем OpenAI с внешними знаниями")
                    external_recommendations = self.external_analyzer.analyze_with_external_knowledge(matches, sport_type)
                    if external_recommendations:
                        return external_recommendations
                    else:
                        self.logger.info("🌐 Внешние знания не дали рекомендаций, используем стандартный анализ")
                
                # Стандартный OpenAI анализ
                self.logger.info("💰 Используем стандартный OpenAI анализ")
                if self.use_enhanced:
                    return self.openai_analyzer.analyze_matches_with_enhanced_gpt(matches, sport_type)
                else:
                    return self.openai_analyzer.analyze_matches_with_gpt(matches, sport_type)
            except Exception as e:
                self.logger.error(f"Ошибка OpenAI анализа, переключаемся на эвристический: {e}")
                # Fallback на эвристический анализ
        
        # Эвристический анализ
        self.logger.info(f"Эвристический анализ {len(matches)} матчей для {sport_type}")
        
        # Ограничиваем количество матчей для анализа
        max_matches = 5
        matches_to_analyze = matches[:max_matches]
        
        # Создаем детальный промпт для анализа
        prompt = self._create_detailed_analysis_prompt(matches_to_analyze, sport_type)
        
        # Используем эвристический анализ
        heuristic_response = self._fallback_heuristic_analysis(prompt)
        
        # Обрабатываем ответ
        recommendations = self._process_claude_response(heuristic_response, matches_to_analyze)
        
        self.logger.info(f"Эвристический анализ сгенерировал {len(recommendations)} рекомендаций для {sport_type}")
        return recommendations
    
    def _create_detailed_analysis_prompt(self, matches: List[MatchData], sport_type: str) -> str:
        """Создает детальный промпт для анализа матчей"""
        
        # Подготавливаем данные матчей
        matches_text = ""
        for i, match in enumerate(matches, 1):
            matches_text += f"{i}. {match.team1} vs {match.team2}\n"
            matches_text += f"   Счет: {match.score}\n"
            matches_text += f"   Минута: {match.minute}\n"
            matches_text += f"   Лига: {match.league}\n"
            matches_text += f"   URL: {match.link}\n\n"
        
        # Детальные правила анализа
        rules = {
            'football': """
            СТРОГИЕ ПРАВИЛА ДЛЯ ФУТБОЛА:
            1. Найди матчи, где одна команда ведет с разрывом ≥1 гол (1:0, 2:1, 3:2, etc.)
            2. ОБЯЗАТЕЛЬНО определи, является ли ведущая команда ЯВНЫМ ФАВОРИТОМ
            3. Время матча должно быть ≥45 минут (минимум второй тайм)
            4. Рекомендуй ТОЛЬКО если вероятность победы фаворита >85%
            
            КРИТЕРИИ ЯВНОГО ФАВОРИТА:
            - Позиция в таблице выше на ≥3 места ИЛИ разница в очках ≥10
            - Форма команд: у фаворита ≥4 победы из последних 5 матчей
            - Качество состава: играют основные игроки (не резервный состав)
            - История встреч: фаворит выиграл ≥3 из последних 5 матчей
            - Домашнее преимущество: если фаворит играет дома (+10% к вероятности)
            - Качество лиги: топ-лиги (Premier League, La Liga, Serie A, Bundesliga, Ligue 1) = более надежно
            
            ДЛЯ КАЖДОГО МАТЧА ПРОВЕРЬ:
            - Анализ силы команд (рейтинг, позиция в таблице, стоимость состава)
            - Форма команд за последние 5-10 матчей
            - Мотивация (борьба за титул, еврокубки, против вылета)
            - Травмы ключевых игроков
            - Тактические особенности (стиль игры, результативность)
            - Время матча и психологический фактор преимущества
            
            ОСОБЫЕ СЛУЧАИ:
            - Если разрыв ≥2 голов - можно рекомендовать даже при меньшем фаворитизме (>80%)
            - Если время >70 минут - повышается надежность любого преимущества
            - Дерби и принципиальные матчи - повышенная осторожность
            - Кубковые матчи - учитывать разницу в классе команд
            """,
            'tennis': """
            СТРОГИЕ ПРАВИЛА ДЛЯ ТЕННИСА:
            1. Найди ТОЛЬКО матчи со счетом 1-0 по сетам ИЛИ разрывом ≥4 геймов в первом сете
            2. Определи, является ли игрок, ведущий в счете, объективным фаворитом
            3. Рекомендуй ТОЛЬКО если вероятность победы фаворита >80%
            
            ДЛЯ КАЖДОГО МАТЧА ПРОВЕРЬ:
            - Рейтинг ATP/WTA (разница ≥ 20 позиций)
            - Форму последних 5 матчей (≥ 4 победы у ведущего игрока)
            - Историю личных встреч (H2H: ≥ 3 победы из 5)
            - Турнир (Grand Slam, ATP 250 и т.д. — важен уровень)
            - Показатели подачи и выигранных очков на приёме
            - Психологическое преимущество после выигрыша сета
            - Статистику по сетам (процент выигранных сетов)
            """,
            'table_tennis': """
            СТРОГИЕ ПРАВИЛА ДЛЯ НАСТОЛЬНОГО ТЕННИСА:
            1. Найди ТОЛЬКО матчи со счетом 1-0 или 2-0 по сетам
            2. Определи, является ли игрок, ведущий в счете, объективным фаворитом
            3. Рекомендуй ТОЛЬКО если вероятность победы фаворита >80%
            
            ДЛЯ КАЖДОГО МАТЧА ПРОВЕРЬ:
            - Рейтинг ITTF (разница ≥ 50 позиций)
            - Форму последних 5 матчей (≥ 4 победы у ведущего игрока)
            - Историю личных встреч (H2H: ≥ 3 победы из 5)
            - Турнир (ITTF World Tour, European Championships и т.д.)
            - Показатели подачи и приема
            - Психологическое преимущество после выигрыша сета
            - Статистику по сетам (процент выигранных сетов)
            """,
            'handball': """
            СТРОГИЕ ПРАВИЛА ДЛЯ ГАНДБОЛА:
            1. Найди ТОЛЬКО матчи, где одна команда ведет с разрывом ≥5 голов
            2. Определи, является ли команда, ведущая в счете, объективным фаворитом
            3. Рекомендуй ТОЛЬКО если вероятность победы фаворита >80%
            
            ДЛЯ КАЖДОГО МАТЧА ПРОВЕРЬ:
            - Позицию в таблице (разница ≥ 3 позиций)
            - Форму последних 5 матчей (≥ 4 победы у ведущей команды)
            - Среднюю результативность команд
            - Качество лиги (высшие лиги = более стабильные результаты)
            - Время матча (чем больше времени, тем выше вероятность удержания преимущества)
            - Статистику атак и защиты
            """
        }
        
        sport_rules = rules.get(sport_type, rules['football'])
        
        prompt = f"""
        Ты - эксперт по анализу live-ставок. {sport_rules}
        
        Проанализируй следующие матчи СТРОГО по правилам выше:
        
        {matches_text}
        
        Для каждого подходящего матча дай ДЕТАЛЬНОЕ обоснование, включающее:
        - Анализ счета и времени матча
        - Сравнение рейтингов/позиций
        - Анализ формы команд/игроков
        - Историю личных встреч (если применимо)
        - Качество турнира/лиги
        - Психологические факторы
        - Статистические показатели
        
        Верни ТОЛЬКО JSON массив с рекомендациями в формате:
        [
            {{
                "team1": "Название команды 1",
                "team2": "Название команды 2", 
                "score": "Счет",
                "recommendation": "П1/П2/Победа игрок",
                "confidence": 0.85,
                "reasoning": "ДЕТАЛЬНОЕ обоснование с анализом рейтингов, формы, истории встреч, качества турнира и статистики"
            }}
        ]
        
        Если НЕТ матчей, соответствующих строгим правилам, верни пустой массив [].
        """
        
        return prompt
    
    def _call_claude_via_cursor(self, prompt: str) -> str:
        """
        Вызывает Claude через Cursor
        """
        # Пока используем эвристический анализ
        # В реальной версии здесь будет вызов Claude через Cursor API
        self.logger.info("Используем эвристический анализ (Claude API недоступен)")
        return self._fallback_heuristic_analysis(prompt)
    
    def _fallback_heuristic_analysis(self, prompt: str) -> str:
        """Fallback анализ, если Claude недоступен"""
        try:
            # Извлекаем данные матчей из промпта
            matches_data = self._extract_matches_from_prompt(prompt)
            recommendations = []
            
            for match_data in matches_data:
                # Анализируем каждый матч по упрощенным правилам
                recommendation = self._analyze_match_heuristic(match_data)
                if recommendation:
                    recommendations.append(recommendation)
            
            return json.dumps(recommendations, ensure_ascii=False)
            
        except Exception as e:
            self.logger.error(f"Ошибка в эвристическом анализе: {e}")
            return "[]"
    
    def _extract_matches_from_prompt(self, prompt: str) -> List[Dict]:
        """Извлекает данные матчей из промпта"""
        matches = []
        lines = prompt.split('\n')
        current_match = {}
        
        for line in lines:
            line = line.strip()
            if line and line[0].isdigit() and 'vs' in line:
                # Новый матч: "1. Команда1 vs Команда2"
                if current_match:
                    matches.append(current_match)
                
                # Извлекаем команды
                match_line = line.split('.', 1)[1].strip()
                if ' vs ' in match_line:
                    team1, team2 = match_line.split(' vs ', 1)
                    current_match = {'team1': team1.strip(), 'team2': team2.strip()}
                    
            elif line.startswith('Счет:'):
                current_match['score'] = line.replace('Счет:', '').strip()
            elif line.startswith('Минута:'):
                current_match['minute'] = line.replace('Минута:', '').strip()
            elif line.startswith('Лига:'):
                current_match['league'] = line.replace('Лига:', '').strip()
        
        if current_match:
            matches.append(current_match)
            
        return matches
    
    def _analyze_match_heuristic(self, match_data: Dict) -> Dict:
        """Упрощенный анализ одного матча"""
        try:
            score = match_data.get('score', '')
            minute = match_data.get('minute', '0')
            league = match_data.get('league', '')
            
            # Парсим счет
            if ':' not in score:
                return None
                
            home_score, away_score = map(int, score.split(':'))
            minute_int = int(minute.replace("'", "").replace("′", "")) if minute.replace("'", "").replace("′", "").isdigit() else 0
            
            # Проверяем базовые критерии для футбола
            if home_score == away_score:  # Ничья
                return None
                
            if minute_int < 45:  # Слишком рано
                return None
            
            # Определяем ведущую команду
            if home_score > away_score:
                leading_team = match_data['team1']
                recommendation = 'П1'
                goal_difference = home_score - away_score
            else:
                leading_team = match_data['team2'] 
                recommendation = 'П2'
                goal_difference = away_score - home_score
            
            # Оценка фаворитизма (упрощенная)
            is_favorite = self._is_favorite_heuristic(leading_team, league, goal_difference, minute_int)
            
            if not is_favorite:
                return None
            
            # Расчет уверенности
            confidence = self._calculate_confidence_heuristic(goal_difference, minute_int, league)
            
            if confidence < 0.85:  # Минимальная уверенность 85%
                return None
            
            # Генерируем обоснование
            reasoning = self._generate_reasoning_heuristic(
                match_data, goal_difference, minute_int, confidence, leading_team
            )
            
            return {
                "team1": match_data['team1'],
                "team2": match_data['team2'],
                "score": score,
                "recommendation": recommendation,
                "confidence": confidence,
                "reasoning": reasoning
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа матча {match_data}: {e}")
            return None
    
    def _is_favorite_heuristic(self, leading_team: str, league: str, goal_diff: int, minute: int) -> bool:
        """Упрощенная проверка фаворитизма"""
        # Топ-лиги (более надежные)
        top_leagues = ['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1', 
                      'Champions League', 'Europa League']
        
        is_top_league = any(top_league.lower() in league.lower() for top_league in top_leagues)
        
        # Известные топ-команды (упрощенный список)
        top_teams = ['Manchester City', 'Arsenal', 'Liverpool', 'Chelsea', 'Manchester United',
                    'Barcelona', 'Real Madrid', 'Atletico Madrid', 'Bayern Munich', 'Borussia Dortmund',
                    'PSG', 'Milan', 'Inter', 'Juventus', 'Napoli']
        
        is_top_team = any(top_team.lower() in leading_team.lower() for top_team in top_teams)
        
        # Логика определения фаворита
        if goal_diff >= 2:  # Преимущество в 2+ гола - почти всегда фаворит
            return True
            
        if goal_diff == 1:  # Преимущество в 1 гол - нужны дополнительные факторы
            factors = 0
            if is_top_team: factors += 1
            if is_top_league: factors += 1  
            if minute > 60: factors += 1
            
            return factors >= 2  # Минимум 2 фактора из 3
        
        return False
    
    def _calculate_confidence_heuristic(self, goal_diff: int, minute: int, league: str) -> float:
        """Упрощенный расчет уверенности"""
        base_confidence = 0.75
        
        # Бонус за разрыв в счете
        if goal_diff == 1:
            base_confidence += 0.05
        elif goal_diff == 2:
            base_confidence += 0.12
        elif goal_diff >= 3:
            base_confidence += 0.20
        
        # Бонус за время матча
        if minute >= 70:
            base_confidence += 0.08
        elif minute >= 60:
            base_confidence += 0.05
        elif minute >= 45:
            base_confidence += 0.02
        
        # Бонус за топ-лигу
        top_leagues = ['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1']
        if any(top_league.lower() in league.lower() for top_league in top_leagues):
            base_confidence += 0.05
        
        return min(base_confidence, 0.95)  # Максимум 95%
    
    def _generate_reasoning_heuristic(self, match_data: Dict, goal_diff: int, minute: int, 
                                    confidence: float, leading_team: str) -> str:
        """Генерирует обоснование для рекомендации"""
        reasoning_parts = []
        
        # Анализ счета
        if goal_diff == 1:
            reasoning_parts.append(f"Команда {leading_team} ведет с минимальным преимуществом 1 гол")
        elif goal_diff == 2:
            reasoning_parts.append(f"Команда {leading_team} имеет комфортное преимущество в 2 гола")
        else:
            reasoning_parts.append(f"Команда {leading_team} доминирует с преимуществом в {goal_diff} гола")
        
        # Анализ времени
        if minute >= 70:
            reasoning_parts.append(f"На {minute} минуте преимущество становится критически важным")
        elif minute >= 60:
            reasoning_parts.append(f"Время {minute}' благоприятствует удержанию результата")
        else:
            reasoning_parts.append(f"С {minute} минуты есть время для закрепления преимущества")
        
        # Анализ лиги
        league = match_data.get('league', '')
        if league:
            reasoning_parts.append(f"Матч проходит в {league}, что добавляет стабильности прогнозу")
        
        # Итоговая уверенность
        confidence_percent = int(confidence * 100)
        reasoning_parts.append(f"Общая уверенность в рекомендации: {confidence_percent}%")
        
        return ". ".join(reasoning_parts) + "."
    
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