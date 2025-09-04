"""
AI-анализатор для обработки матчей с помощью Claude AI
"""
import logging
import json
from typing import List, Dict, Any
from dataclasses import asdict
from multi_source_controller import MatchData
import config

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """AI-анализатор для обработки матчей с помощью Claude"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def analyze_matches_with_ai(self, matches: List[MatchData], sport_type: str) -> List[MatchData]:
        """
        Анализирует матчи с помощью AI и возвращает рекомендации
        """
        if not matches:
            return []
            
        self.logger.info(f"AI-анализ {len(matches)} матчей для {sport_type}")
        
        # Группируем матчи по типам для более эффективного анализа
        recommendations = []
        
        for match in matches:
            try:
                ai_recommendation = self._get_ai_recommendation(match, sport_type)
                if ai_recommendation:
                    recommendations.append(ai_recommendation)
            except Exception as e:
                self.logger.error(f"Ошибка AI-анализа для матча {match.team1} - {match.team2}: {e}")
                continue
                
        # Ограничиваем количество рекомендаций (максимум 5 на вид спорта)
        recommendations = sorted(recommendations, key=lambda x: x.probability, reverse=True)[:5]
        
        self.logger.info(f"AI сгенерировал {len(recommendations)} рекомендаций для {sport_type}")
        return recommendations
    
    def _get_ai_recommendation(self, match: MatchData, sport_type: str) -> MatchData:
        """
        Получает AI-рекомендацию для конкретного матча
        """
        # Подготавливаем данные для AI-анализа
        match_context = self._prepare_match_context(match, sport_type)
        
        # Генерируем AI-рекомендацию на основе контекста
        ai_analysis = self._generate_ai_analysis(match_context, sport_type)
        
        # Применяем AI-рекомендацию к матчу
        if ai_analysis and ai_analysis.get('recommendation'):
            return self._apply_ai_recommendation(match, ai_analysis)
        
        return None
    
    def _prepare_match_context(self, match: MatchData, sport_type: str) -> Dict[str, Any]:
        """
        Подготавливает контекст матча для AI-анализа
        """
        context = {
            'sport_type': sport_type,
            'team1': match.team1,
            'team2': match.team2,
            'score': match.score,
            'minute': match.minute,
            'league': match.league,
            'source': match.source,
            'url': match.url
        }
        
        # Добавляем специфичную для спорта информацию
        if sport_type == 'football':
            context.update(self._get_football_context(match))
        elif sport_type == 'tennis':
            context.update(self._get_tennis_context(match))
        elif sport_type == 'table_tennis':
            context.update(self._get_table_tennis_context(match))
        elif sport_type == 'handball':
            context.update(self._get_handball_context(match))
            
        return context
    
    def _get_football_context(self, match: MatchData) -> Dict[str, Any]:
        """Контекст для футбола"""
        context = {
            'analysis_type': 'football_live',
            'score_analysis': self._analyze_football_score(match.score),
            'minute_analysis': self._analyze_minute(match.minute, 'football')
        }
        return context
    
    def _get_tennis_context(self, match: MatchData) -> Dict[str, Any]:
        """Контекст для тенниса"""
        context = {
            'analysis_type': 'tennis_live',
            'score_analysis': self._analyze_tennis_score(match.score),
            'set_analysis': self._analyze_tennis_sets(match.score)
        }
        return context
    
    def _get_table_tennis_context(self, match: MatchData) -> Dict[str, Any]:
        """Контекст для настольного тенниса"""
        context = {
            'analysis_type': 'table_tennis_live',
            'score_analysis': self._analyze_table_tennis_score(match.score),
            'set_analysis': self._analyze_table_tennis_sets(match.score)
        }
        return context
    
    def _get_handball_context(self, match: MatchData) -> Dict[str, Any]:
        """Контекст для гандбола"""
        context = {
            'analysis_type': 'handball_live',
            'score_analysis': self._analyze_handball_score(match.score),
            'minute_analysis': self._analyze_minute(match.minute, 'handball'),
            'total_analysis': self._analyze_handball_total(match)
        }
        return context
    
    def _analyze_football_score(self, score: str) -> Dict[str, Any]:
        """Анализ счета в футболе"""
        if not score or ':' not in score:
            return {'is_draw': False, 'leader': None, 'advantage': 0}
            
        try:
            home, away = map(int, score.split(':'))
            is_draw = home == away
            leader = 'home' if home > away else 'away' if away > home else None
            advantage = abs(home - away)
            
            return {
                'is_draw': is_draw,
                'leader': leader,
                'advantage': advantage,
                'home_score': home,
                'away_score': away
            }
        except:
            return {'is_draw': False, 'leader': None, 'advantage': 0}
    
    def _analyze_tennis_score(self, score: str) -> Dict[str, Any]:
        """Анализ счета в теннисе"""
        if not score:
            return {'sets_lead': 0, 'games_lead': 0, 'leader': None}
        
        try:
            # Проверяем формат "1:1" (счет по сетам)
            if ':' in score and not any('-' in s for s in score.split()):
                sets = score.strip().split(':')
                if len(sets) == 2:
                    home_sets = int(sets[0])
                    away_sets = int(sets[1])
                    sets_lead = abs(home_sets - away_sets)
                    leader = 'home' if home_sets > away_sets else 'away' if away_sets > home_sets else None
                    
                    return {
                        'sets_lead': sets_lead,
                        'games_lead': 0,  # Не анализируем геймы для формата "1:1"
                        'leader': leader,
                        'raw_score': score
                    }
            
            # Обычный формат "6-4 6-2"
            sets = score.split(' ')
            sets_lead = 0
            games_lead = 0
            leader = None
            
            if len(sets) >= 1:
                first_set = sets[0]
                if '-' in first_set:
                    home_games, away_games = map(int, first_set.split('-'))
                    games_lead = abs(home_games - away_games)
                    leader = 'home' if home_games > away_games else 'away' if away_games > home_games else None
            
            return {
                'sets_lead': sets_lead,
                'games_lead': games_lead,
                'leader': leader,
                'raw_score': score
            }
        except Exception as e:
            logger.warning(f"Ошибка анализа счета тенниса '{score}': {e}")
            return {'sets_lead': 0, 'games_lead': 0, 'leader': None, 'raw_score': score}
    
    def _analyze_table_tennis_score(self, score: str) -> Dict[str, Any]:
        """Анализ счета в настольном теннисе"""
        return self._analyze_tennis_score(score)  # Аналогично теннису
    
    def _analyze_handball_score(self, score: str) -> Dict[str, Any]:
        """Анализ счета в гандболе"""
        if not score or ':' not in score:
            return {'is_draw': False, 'leader': None, 'advantage': 0}
            
        try:
            home, away = map(int, score.split(':'))
            is_draw = home == away
            leader = 'home' if home > away else 'away' if away > home else None
            advantage = abs(home - away)
            total_goals = home + away
            
            return {
                'is_draw': is_draw,
                'leader': leader,
                'advantage': advantage,
                'home_score': home,
                'away_score': away,
                'total_goals': total_goals
            }
        except:
            return {'is_draw': False, 'leader': None, 'advantage': 0}
    
    def _analyze_tennis_sets(self, score: str) -> Dict[str, Any]:
        """Анализ сетов в теннисе"""
        if not score:
            return {'sets_won': {'home': 0, 'away': 0}, 'current_set': 1}
            
        sets = score.split(' ')
        home_sets = 0
        away_sets = 0
        
        for set_score in sets:
            if '-' in set_score:
                try:
                    home_games, away_games = map(int, set_score.split('-'))
                    if home_games > away_games:
                        home_sets += 1
                    elif away_games > home_games:
                        away_sets += 1
                except:
                    continue
        
        return {
            'sets_won': {'home': home_sets, 'away': away_sets},
            'current_set': home_sets + away_sets + 1
        }
    
    def _analyze_table_tennis_sets(self, score: str) -> Dict[str, Any]:
        """Анализ сетов в настольном теннисе"""
        return self._analyze_tennis_sets(score)
    
    def _analyze_minute(self, minute: str, sport_type: str) -> Dict[str, Any]:
        """Анализ минуты матча"""
        if not minute:
            return {'minute': 0, 'phase': 'unknown'}
            
        try:
            minute_num = int(minute.replace("'", "").replace("мин", "").strip())
            
            if sport_type == 'football':
                if minute_num <= 15:
                    phase = 'early'
                elif minute_num <= 30:
                    phase = 'first_half'
                elif minute_num <= 45:
                    phase = 'late_first_half'
                elif minute_num <= 60:
                    phase = 'early_second_half'
                elif minute_num <= 75:
                    phase = 'second_half'
                else:
                    phase = 'late_game'
            elif sport_type == 'handball':
                if minute_num <= 15:
                    phase = 'early'
                elif minute_num <= 30:
                    phase = 'first_half'
                elif minute_num <= 45:
                    phase = 'second_half'
                else:
                    phase = 'late_game'
            else:
                phase = 'unknown'
                
            return {
                'minute': minute_num,
                'phase': phase
            }
        except:
            return {'minute': 0, 'phase': 'unknown'}
    
    def _analyze_handball_total(self, match: MatchData) -> Dict[str, Any]:
        """Анализ тотала в гандболе"""
        score_analysis = self._analyze_handball_score(match.score)
        minute_analysis = self._analyze_minute(match.minute, 'handball')
        
        if score_analysis.get('total_goals') and minute_analysis.get('minute'):
            total_goals = score_analysis['total_goals']
            played_minutes = minute_analysis['minute']
            
            if played_minutes > 0:
                predicted_total = (total_goals / played_minutes) * 60
                predicted_total = int(predicted_total) + (1 if predicted_total % 1 > 0 else 0)
                
                tempo = 'fast' if total_goals > played_minutes else 'slow' if total_goals < played_minutes else 'neutral'
                
                return {
                    'predicted_total': predicted_total,
                    'tempo': tempo,
                    'total_under': predicted_total + 4,
                    'total_over': predicted_total - 4,
                    'goals_per_minute': total_goals / played_minutes
                }
        
        return {'predicted_total': 0, 'tempo': 'unknown'}
    
    def _generate_ai_analysis(self, context: Dict[str, Any], sport_type: str) -> Dict[str, Any]:
        """
        Генерирует AI-анализ на основе контекста матча
        В реальной реализации здесь будет вызов Claude API
        """
        # Пока используем эвристический анализ, но структура готова для Claude API
        return self._heuristic_analysis(context, sport_type)
    
    def _heuristic_analysis(self, context: Dict[str, Any], sport_type: str) -> Dict[str, Any]:
        """
        Эвристический анализ (временная замена для Claude API)
        """
        analysis = {
            'confidence': 0.0,
            'recommendation': None,
            'reasoning': '',
            'probability': 0.0,
            'coefficient': 1.0
        }
        
        if sport_type == 'football':
            analysis = self._analyze_football_heuristic(context)
        elif sport_type == 'tennis':
            analysis = self._analyze_tennis_heuristic(context)
        elif sport_type == 'table_tennis':
            analysis = self._analyze_table_tennis_heuristic(context)
        elif sport_type == 'handball':
            analysis = self._analyze_handball_heuristic(context)
        
        return analysis
    
    def _analyze_football_heuristic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Улучшенный эвристический анализ футбола с AI-логикой"""
        score_analysis = context.get('score_analysis', {})
        minute_analysis = context.get('minute_analysis', {})
        
        if not score_analysis.get('is_draw') and score_analysis.get('advantage', 0) > 0:
            leader = score_analysis.get('leader')
            advantage = score_analysis.get('advantage', 0)
            minute = minute_analysis.get('minute', 0)
            phase = minute_analysis.get('phase', 'unknown')
            
            # AI-анализ: учитываем множество факторов
            base_confidence = 0.3
            
            # Фактор 1: Преимущество в счете (чем больше, тем лучше)
            advantage_factor = min(0.4, advantage * 0.08)
            
            # Фактор 2: Время матча (чем позже, тем стабильнее результат)
            time_factor = 0.0
            if phase == 'late_first_half':
                time_factor = 0.1
            elif phase == 'early_second_half':
                time_factor = 0.15
            elif phase == 'second_half':
                time_factor = 0.2
            elif phase == 'late_game':
                time_factor = 0.25
            
            # Фактор 3: Размер преимущества относительно времени
            if minute > 0:
                goals_per_minute = advantage / minute
                if goals_per_minute > 0.05:  # Более 1 гола за 20 минут
                    time_factor += 0.1
            
            # Фактор 4: Критический момент (последние 15 минут)
            if minute > 75:
                time_factor += 0.15
            
            # Фактор 5: Большое преимущество (3+ гола)
            if advantage >= 3:
                advantage_factor += 0.2
            
            # Фактор 6: Лига (определяем по названию команд)
            league_factor = self._analyze_league_quality(context)
            
            # Итоговая уверенность
            confidence = min(0.95, base_confidence + advantage_factor + time_factor + league_factor)
            
            # Минимальный порог для рекомендации
            min_confidence = 0.65 if advantage >= 2 else 0.75
            
            if confidence > min_confidence:
                recommendation_type = 'win'
                recommendation_value = 'П1' if leader == 'home' else 'П2'
                
                # Переводим названия команд
                team1_rus = self._translate_team_name(context['team1'])
                team2_rus = self._translate_team_name(context['team2'])
                leading_team = team1_rus if leader == 'home' else team2_rus
                
                # Умное обоснование
                reasoning_parts = []
                reasoning_parts.append(f"Команда {leading_team} ведет {context['score']}")
                
                if minute > 0:
                    reasoning_parts.append(f"на {minute} минуте")
                
                if advantage >= 3:
                    reasoning_parts.append("с подавляющим преимуществом")
                elif advantage >= 2:
                    reasoning_parts.append("с солидным преимуществом")
                
                if phase == 'late_game':
                    reasoning_parts.append("в концовке матча")
                elif phase == 'second_half':
                    reasoning_parts.append("во втором тайме")
                
                if league_factor > 0.1:
                    reasoning_parts.append("в качественной лиге")
                
                reasoning = ", ".join(reasoning_parts) + "."
                
                # Динамический коэффициент
                coefficient = 1.2 + (1 - confidence) * 0.8
                
                return {
                    'confidence': confidence,
                    'recommendation': {
                        'type': recommendation_type,
                        'value': recommendation_value,
                        'reasoning': reasoning
                    },
                    'reasoning': reasoning,
                    'probability': confidence * 100,
                    'coefficient': coefficient
                }
        
        return {'confidence': 0.0, 'recommendation': None, 'reasoning': '', 'probability': 0.0, 'coefficient': 1.0}
    
    def _analyze_league_quality(self, context: Dict[str, Any]) -> float:
        """Анализ качества лиги по названиям команд"""
        team1 = context.get('team1', '').lower()
        team2 = context.get('team2', '').lower()
        league = context.get('league', '').lower()
        
        # Ключевые слова для определения качества лиги
        high_quality_keywords = [
            'premier', 'champions', 'europa', 'uefa', 'fifa', 'world cup',
            'euro', 'bundesliga', 'serie a', 'la liga', 'ligue 1', 'epl',
            'real madrid', 'barcelona', 'manchester', 'liverpool', 'chelsea',
            'arsenal', 'tottenham', 'bayern', 'juventus', 'milan', 'inter'
        ]
        
        medium_quality_keywords = [
            'championship', 'serie b', '2. bundesliga', 'segunda', 'ligue 2',
            'europa league', 'conference', 'copa', 'fa cup', 'dfb pokal'
        ]
        
        # Проверяем названия команд и лиги
        text_to_check = f"{team1} {team2} {league}"
        
        for keyword in high_quality_keywords:
            if keyword in text_to_check:
                return 0.15  # Бонус за качественную лигу
        
        for keyword in medium_quality_keywords:
            if keyword in text_to_check:
                return 0.05  # Небольшой бонус за среднюю лигу
        
        return 0.0  # Нет бонуса
    
    def _translate_player_name(self, name: str) -> str:
        """Переводит имя игрока на русский язык"""
        translations = {
            'djokovic': 'Новак Джокович',
            'nadal': 'Рафаэль Надаль', 
            'federer': 'Роджер Федерер',
            'murray': 'Энди Мюррей',
            'medvedev': 'Даниил Медведев',
            'tsitsipas': 'Стефанос Циципас',
            'zverev': 'Александр Зверев',
            'rublev': 'Андрей Рублев',
            'sinner': 'Янник Синнер',
            'alcaraz': 'Карлос Алькарас',
            'serena': 'Серена Уильямс',
            'venus': 'Винус Уильямс',
            'sharapova': 'Мария Шарапова',
            'azarenka': 'Виктория Азаренко',
            'halep': 'Симона Халеп',
            'kerber': 'Анжелика Кербер',
            'osaka': 'Наоми Осака',
            'swiatek': 'Ига Свёнтек',
            'sabalenka': 'Арина Соболенко',
            'gauff': 'Кори Гауф'
        }
        
        name_lower = name.lower()
        for eng_name, rus_name in translations.items():
            if eng_name in name_lower:
                return rus_name
        return name  # Возвращаем оригинальное имя, если перевод не найден
    
    def _translate_team_name(self, name: str) -> str:
        """Переводит название команды на русский язык"""
        translations = {
            'manchester city': 'Манчестер Сити',
            'manchester united': 'Манчестер Юнайтед',
            'liverpool': 'Ливерпуль',
            'chelsea': 'Челси',
            'arsenal': 'Арсенал',
            'tottenham': 'Тоттенхэм',
            'real madrid': 'Реал Мадрид',
            'barcelona': 'Барселона',
            'atletico madrid': 'Атлетико Мадрид',
            'bayern munich': 'Бавария',
            'borussia dortmund': 'Боруссия Дортмунд',
            'juventus': 'Ювентус',
            'milan': 'Милан',
            'inter': 'Интер',
            'napoli': 'Наполи',
            'psg': 'ПСЖ',
            'monaco': 'Монако',
            'lyon': 'Лион',
            'marseille': 'Марсель',
            'norway': 'Норвегия',
            'denmark': 'Дания',
            'germany': 'Германия',
            'france': 'Франция',
            'spain': 'Испания',
            'italy': 'Италия',
            'england': 'Англия',
            'brazil': 'Бразилия',
            'argentina': 'Аргентина'
        }
        
        name_lower = name.lower()
        for eng_name, rus_name in translations.items():
            if eng_name in name_lower:
                return rus_name
        return name  # Возвращаем оригинальное название, если перевод не найден
    
    def _analyze_tennis_heuristic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Улучшенный эвристический анализ тенниса с AI-логикой"""
        score_analysis = context.get('score_analysis', {})
        set_analysis = context.get('set_analysis', {})
        
        sets_won = set_analysis.get('sets_won', {'home': 0, 'away': 0})
        games_lead = score_analysis.get('games_lead', 0)
        leader = score_analysis.get('leader')
        current_set = set_analysis.get('current_set', 1)
        
        # Отладочная информация
        logger.debug(f"Теннис анализ: {context['team1']} vs {context['team2']}, счет: {context['score']}, лидер: {leader}, преимущество в геймах: {games_lead}, сетов: {sets_won}")
        
        # AI-анализ тенниса
        base_confidence = 0.3
        confidence = 0.0
        
        # Базовый бонус за любое преимущество
        if leader:
            confidence = base_confidence + 0.2  # Увеличиваем базовый бонус
        
        # Фактор 1: Преимущество по сетам (самый важный)
        sets_advantage = abs(sets_won['home'] - sets_won['away'])
        if sets_advantage >= 1:
            confidence = base_confidence + 0.4 + (sets_advantage * 0.15)
            
            # Бонус за доминирование
            if sets_advantage >= 2:
                confidence += 0.2
        
        # Фактор 2: Большое преимущество в геймах текущего сета
        elif games_lead >= 2:  # Снижен порог
            confidence = base_confidence + 0.2 + (games_lead * 0.05)
            
            # Дополнительный бонус за очень большое преимущество
            if games_lead >= 4:
                confidence += 0.15
            elif games_lead >= 3:
                confidence += 0.1
        
        # Фактор 3: Небольшое преимущество в геймах
        elif games_lead >= 1:
            confidence = base_confidence + 0.1 + (games_lead * 0.04)
        
        # Фактор 4: Качество турнира (определяем по названиям игроков)
        tournament_factor = self._analyze_tennis_tournament_quality(context)
        confidence += tournament_factor
        
        # Фактор 5: Бонус за известных игроков
        player1 = context.get('team1', '').lower()
        player2 = context.get('team2', '').lower()
        known_players = ['djokovic', 'nadal', 'federer', 'murray', 'medvedev', 'tsitsipas', 'zverev', 'rublev', 'sinner', 'alcaraz']
        if any(player in player1 or player in player2 for player in known_players):
            confidence += 0.1
        
        # Фактор 5: Стадия матча (чем больше сетов сыграно, тем стабильнее)
        if current_set >= 2:  # Второй сет и далее
            confidence += 0.05
        
        # Минимальный порог для рекомендации (оптимизированный)
        min_confidence = 0.4
        
        if confidence > min_confidence and leader:
            recommendation_type = 'win'
            player_name = self._translate_player_name(context['team1'] if leader == 'home' else context['team2'])
            recommendation_value = f"Победа {player_name}"
            
            # Умное обоснование
            reasoning_parts = []
            reasoning_parts.append(f"Игрок {player_name} ведет {context['score']}")
            
            if sets_advantage >= 1:
                reasoning_parts.append(f"по сетам ({sets_advantage} сет впереди)")
            elif games_lead >= 3:
                reasoning_parts.append(f"с большим преимуществом в геймах ({games_lead})")
            elif games_lead >= 2:
                reasoning_parts.append(f"с преимуществом в геймах ({games_lead})")
            
            if tournament_factor > 0.1:
                reasoning_parts.append("в престижном турнире")
            
            reasoning = ", ".join(reasoning_parts) + "."
            
            # Динамический коэффициент
            coefficient = 1.2 + (1 - confidence) * 0.8
            
            return {
                'confidence': confidence,
                'recommendation': {
                    'type': recommendation_type,
                    'value': recommendation_value,
                    'reasoning': reasoning
                },
                'reasoning': reasoning,
                'probability': confidence * 100,
                'coefficient': coefficient
            }
        
        return {'confidence': 0.0, 'recommendation': None, 'reasoning': '', 'probability': 0.0, 'coefficient': 1.0}
    
    def _analyze_tennis_tournament_quality(self, context: Dict[str, Any]) -> float:
        """Анализ качества теннисного турнира"""
        team1 = context.get('team1', '').lower()
        team2 = context.get('team2', '').lower()
        league = context.get('league', '').lower()
        
        # Ключевые слова для престижных турниров
        high_quality_keywords = [
            'wimbledon', 'roland garros', 'us open', 'australian open',
            'atp', 'wta', 'masters', 'grand slam', 'davis cup', 'federation cup',
            'djokovic', 'nadal', 'federer', 'murray', 'serena', 'venus',
            'sharapova', 'azarenka', 'halep', 'kerber', 'osaka'
        ]
        
        medium_quality_keywords = [
            'challenger', 'itf', 'futures', 'qualifying', 'qualification',
            'round of 16', 'quarterfinal', 'semifinal', 'final'
        ]
        
        text_to_check = f"{team1} {team2} {league}"
        
        for keyword in high_quality_keywords:
            if keyword in text_to_check:
                return 0.2  # Бонус за престижный турнир
        
        for keyword in medium_quality_keywords:
            if keyword in text_to_check:
                return 0.05  # Небольшой бонус
        
        return 0.0
    
    def _analyze_table_tennis_heuristic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Эвристический анализ настольного тенниса"""
        return self._analyze_tennis_heuristic(context)  # Аналогично теннису
    
    def _analyze_handball_heuristic(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Улучшенный эвристический анализ гандбола"""
        score_analysis = context.get('score_analysis', {})
        minute_analysis = context.get('minute_analysis', {})
        total_analysis = context.get('total_analysis', {})
        
        # Анализ прямых побед (значительно снижен порог)
        if not score_analysis.get('is_draw') and score_analysis.get('advantage', 0) >= 2:
            leader = score_analysis.get('leader')
            advantage = score_analysis.get('advantage', 0)
            minute = minute_analysis.get('minute', 0)
            
            confidence = min(0.9, 0.3 + (advantage * 0.08) + (minute * 0.003))
            
            if confidence > 0.45:  # Значительно снижен порог
                recommendation_type = 'win'
                team_name = self._translate_team_name(context['team1'] if leader == 'home' else context['team2'])
                recommendation_value = 'П1' if leader == 'home' else 'П2'
                reasoning = f"Команда {team_name} ведет {context['score']} с преимуществом {advantage} голов"
                
                return {
                    'confidence': confidence,
                    'recommendation': {
                        'type': recommendation_type,
                        'value': recommendation_value,
                        'reasoning': reasoning
                    },
                    'reasoning': reasoning,
                    'probability': confidence * 100,
                    'coefficient': 1.3 + (1 - confidence) * 0.7
                }
        
        # Анализ тоталов (расширен диапазон)
        minute = minute_analysis.get('minute', 0)
        if 5 <= minute <= 50 and total_analysis.get('predicted_total', 0) > 0:
            tempo = total_analysis.get('tempo', 'unknown')
            predicted_total = total_analysis.get('predicted_total', 0)
            
            if tempo in ['fast', 'slow']:
                confidence = 0.6  # Значительно снижен порог
                recommendation_type = 'total'
                
                if tempo == 'fast':
                    recommendation_value = f"ТБ {total_analysis.get('total_over', 0)}"
                    reasoning = f"Высокий темп игры ({total_analysis.get('goals_per_minute', 0):.1f} голов/мин), прогнозный тотал: {predicted_total}"
                else:  # slow
                    recommendation_value = f"ТМ {total_analysis.get('total_under', 0)}"
                    reasoning = f"Низкий темп игры ({total_analysis.get('goals_per_minute', 0):.1f} голов/мин), прогнозный тотал: {predicted_total}"
                
                return {
                    'confidence': confidence,
                    'recommendation': {
                        'type': recommendation_type,
                        'value': recommendation_value,
                        'reasoning': reasoning
                    },
                    'reasoning': reasoning,
                    'probability': confidence * 100,
                    'coefficient': 1.5
                }
        
        return {'confidence': 0.0, 'recommendation': None, 'reasoning': '', 'probability': 0.0, 'coefficient': 1.0}
    
    def _apply_ai_recommendation(self, match: MatchData, ai_analysis: Dict[str, Any]) -> MatchData:
        """
        Применяет AI-рекомендацию к матчу
        """
        recommendation = ai_analysis.get('recommendation', {})
        
        if recommendation:
            match.recommendation_type = recommendation.get('type', '')
            match.recommendation_value = recommendation.get('value', '')
            match.justification = recommendation.get('reasoning', '')
            match.probability = ai_analysis.get('probability', 0.0)
            match.coefficient = ai_analysis.get('coefficient', 1.0)
        
        return match