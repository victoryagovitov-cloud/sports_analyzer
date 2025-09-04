import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import List
from dataclasses import dataclass, field
import config
from betzona_controller import BetzonaController
from enhanced_real_controller import EnhancedRealDataController

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

@dataclass
class MatchData:
    sport: str
    team1: str
    team2: str
    score: str
    minute: str = ""
    league: str = ""
    odds: dict = field(default_factory=dict)
    link: str = ""
    probability: float = 0.0  # Вероятность победы фаворита
    recommendation_type: str = ""  # 'win' or 'total'
    recommendation_value: str = ""  # 'П1', 'ТБ X', 'ТМ Y'
    justification: str = ""  # Обоснование рекомендации
    source: str = ""  # Источник данных

class MultiSourceController:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Инициализируем контроллеры для разных источников
        self.betzona_controller = BetzonaController()
        self.scores24_controller = EnhancedRealDataController()
        
        # Приоритет источников (от лучшего к худшему)
        self.source_priority = ['betzona', 'scores24']

    def get_live_matches(self, sport_type: str) -> List[MatchData]:
        """Получение live-матчей из всех доступных источников"""
        all_matches = []
        
        # Получаем данные из Betzona
        try:
            self.logger.info(f"Получение данных из Betzona для {sport_type}...")
            betzona_matches = self.betzona_controller.get_live_matches(sport_type)
            for match in betzona_matches:
                match.source = 'betzona'
            all_matches.extend(betzona_matches)
            self.logger.info(f"Betzona: найдено {len(betzona_matches)} матчей")
        except Exception as e:
            self.logger.error(f"Ошибка при получении данных из Betzona: {e}")
        
        # Получаем данные из Scores24
        try:
            self.logger.info(f"Получение данных из Scores24 для {sport_type}...")
            scores24_matches = self.scores24_controller.get_live_matches('scores24', sport_type)
            for match in scores24_matches:
                match.source = 'scores24'
            all_matches.extend(scores24_matches)
            self.logger.info(f"Scores24: найдено {len(scores24_matches)} матчей")
        except Exception as e:
            self.logger.error(f"Ошибка при получении данных из Scores24: {e}")
        
        # Удаляем дубликаты (по названиям команд и счету)
        unique_matches = self._remove_duplicates(all_matches)
        
        self.logger.info(f"Всего уникальных матчей для {sport_type}: {len(unique_matches)}")
        return unique_matches

    def _remove_duplicates(self, matches: List[MatchData]) -> List[MatchData]:
        """Удаление дубликатов матчей"""
        seen = set()
        unique_matches = []
        
        for match in matches:
            # Создаем ключ для сравнения
            key = (match.sport_type, match.team1.lower(), match.team2.lower(), match.score)
            
            if key not in seen:
                seen.add(key)
                unique_matches.append(match)
            else:
                # Если матч уже есть, выбираем из источника с более высоким приоритетом
                existing_match = next(m for m in unique_matches if (m.sport_type, m.team1.lower(), m.team2.lower(), m.score) == key)
                if self.source_priority.index(match.source) < self.source_priority.index(existing_match.source):
                    # Заменяем на матч из источника с более высоким приоритетом
                    unique_matches.remove(existing_match)
                    unique_matches.append(match)
        
        return unique_matches

    def get_all_live_matches(self) -> List[MatchData]:
        """Получение всех live-матчей по всем видам спорта"""
        all_matches = []
        
        sports = ['football', 'tennis', 'table_tennis', 'handball']
        
        for sport in sports:
            self.logger.info(f"Получение live-матчей для {sport}...")
            matches = self.get_live_matches(sport)
            all_matches.extend(matches)
            
        return all_matches

    def get_matches_by_source(self, source: str) -> List[MatchData]:
        """Получение матчей из конкретного источника"""
        all_matches = []
        
        sports = ['football', 'tennis', 'table_tennis', 'handball']
        
        for sport in sports:
            if source == 'betzona':
                matches = self.betzona_controller.get_live_matches(sport)
            elif source == 'scores24':
                matches = self.scores24_controller.get_live_matches('scores24', sport)
            else:
                continue
                
            for match in matches:
                match.source = source
            all_matches.extend(matches)
            
        return all_matches

def test_multi_source_controller():
    logging.info("============================================================")
    logging.info("ТЕСТ МУЛЬТИ-ИСТОЧНИКОВОГО КОНТРОЛЛЕРА")
    logging.info("============================================================")
    controller = MultiSourceController()
    all_matches = []

    sports = ['football', 'tennis', 'table_tennis', 'handball']

    for sport in sports:
        logging.info(f"\n--- Тестирование {sport.upper()} ---")
        matches = controller.get_live_matches(sport)
        all_matches.extend(matches)
        logging.info(f"Найдено {len(matches)} матчей:")
        for i, match in enumerate(matches[:5]):  # Print first 5 matches
            logging.info(f"  {i+1}. {match.team1} - {match.team2}")
            logging.info(f"     Счет: {match.score}, Минута: {match.minute}")
            logging.info(f"     Лига: {match.league}")
            logging.info(f"     Источник: {match.source}")

    logging.info("\n============================================================")
    logging.info("СВОДНАЯ СТАТИСТИКА:")
    logging.info("============================================================")
    for sport in sports:
        count = sum(1 for m in all_matches if m.sport_type == sport)
        logging.info(f"{sport.upper()}: {count} матчей")

    # Статистика по источникам
    sources = {}
    for match in all_matches:
        source = match.source
        if source not in sources:
            sources[source] = 0
        sources[source] += 1
    
    logging.info("\nСтатистика по источникам:")
    for source, count in sources.items():
        logging.info(f"{source.upper()}: {count} матчей")

    total_count = len(all_matches)
    logging.info(f"\nВСЕГО: {total_count} матчей")

    if total_count == 0:
        logging.info("\n❌ МУЛЬТИ-ИСТОЧНИКОВЫЙ КОНТРОЛЛЕР НЕ РАБОТАЕТ. Матчи не найдены.")
    else:
        logging.info("\n✅ МУЛЬТИ-ИСТОЧНИКОВЫЙ КОНТРОЛЛЕР РАБОТАЕТ. Матчи найдены.")

    logging.info("\n============================================================")
    logging.info("ТЕСТ ЗАВЕРШЕН")
    logging.info("============================================================")

if __name__ == "__main__":
    test_multi_source_controller()