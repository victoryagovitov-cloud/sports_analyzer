#!/usr/bin/env python3
"""
Контроллер ТОЛЬКО для scores24.live (по промпту)
"""

import logging
from typing import List, Dict
from enhanced_real_controller import EnhancedRealDataController
from multi_source_controller import MatchData
from moscow_time import filter_live_matches_by_time

logger = logging.getLogger(__name__)

class Scores24OnlyController:
    """
    Контроллер, который берет данные ТОЛЬКО с scores24.live
    Полностью соответствует промпту пользователя
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        # Используем только scores24 контроллер
        self.scores24_controller = EnhancedRealDataController()
        
    def get_live_matches(self, sport_type: str) -> List[MatchData]:
        """
        Получает live-матчи ТОЛЬКО с scores24.live
        Источники данных: ТОЛЬКО scores24.live (по промпту)
        """
        self.logger.info(f"🔍 Получение live-матчей ТОЛЬКО с scores24.live для {sport_type}")
        
        try:
            # Получаем данные ТОЛЬКО с scores24.live
            matches = self.scores24_controller.get_live_matches('scores24', sport_type)
            self.logger.info(f"📊 Scores24.live: найдено {len(matches)} live-матчей для {sport_type}")
            
            if not matches:
                self.logger.warning(f"❌ Нет live-матчей на scores24.live для {sport_type}")
                return []
            
            # Фильтруем завершившиеся матчи
            active_matches = filter_live_matches_by_time(matches, sport_type)
            
            if len(active_matches) < len(matches):
                excluded_count = len(matches) - len(active_matches)
                self.logger.info(f"🏁 Исключено {excluded_count} завершившихся матчей")
            
            # Сортируем по приоритету (топ-лиги в приоритете)
            prioritized_matches = self._prioritize_by_league(active_matches, sport_type)
            
            self.logger.info(f"✅ Итого актуальных матчей с scores24.live: {len(prioritized_matches)}")
            return prioritized_matches
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения данных с scores24.live: {e}")
            return []
    
    def _prioritize_by_league(self, matches: List[MatchData], sport_type: str) -> List[MatchData]:
        """
        Приоритизирует матчи по качеству лиги (по промпту)
        """
        def get_league_priority(match):
            league = getattr(match, 'league', '').lower()
            
            if sport_type == 'football':
                # Топ-лиги футбола (высший приоритет)
                top_leagues = {
                    'premier league': 100, 'champions league': 100, 'la liga': 95,
                    'serie a': 95, 'bundesliga': 95, 'ligue 1': 90, 'europa league': 85,
                    'eredivisie': 80, 'primeira liga': 75, 'championship': 70
                }
                
                for league_name, priority in top_leagues.items():
                    if league_name in league:
                        return priority
                
                # Средние лиги
                if any(keyword in league for keyword in ['первая лига', 'второй дивизион', 'лига 2']):
                    return 30
                
                return 50  # Базовый приоритет
                
            elif sport_type == 'tennis':
                # Топ-турниры тенниса
                top_tournaments = {
                    'grand slam': 100, 'atp masters': 95, 'wta 1000': 95,
                    'atp 500': 85, 'wta 500': 85, 'atp 250': 75, 'wta 250': 75
                }
                
                for tournament, priority in top_tournaments.items():
                    if tournament in league:
                        return priority
                
                return 50
                
            elif sport_type == 'handball':
                # Топ-лиги гандбола
                if any(keyword in league for keyword in ['champions league', 'ehf', 'bundesliga']):
                    return 90
                
                return 50
            
            return 50
        
        # Сортируем по приоритету лиги
        sorted_matches = sorted(matches, key=get_league_priority, reverse=True)
        
        # Логируем приоритизацию
        if sorted_matches:
            top_match = sorted_matches[0]
            priority = get_league_priority(top_match)
            self.logger.info(f"🏆 Топ-приоритет: {top_match.team1} vs {top_match.team2} ({top_match.league}) - приоритет {priority}")
        
        return sorted_matches
    
    def get_match_details(self, match_url: str) -> Dict:
        """
        Получает детальную информацию о матче со всех вкладок
        (по промпту: основная, prediction, trends, h2h, odds)
        """
        # Заглушка для будущей реализации глубокого анализа
        return {
            'predictions': {},
            'trends': {},
            'h2h': {},
            'odds': {},
            'statistics': {}
        }

# Глобальный экземпляр
scores24_only_controller = Scores24OnlyController()