import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import List
from dataclasses import dataclass, field
import config

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

@dataclass
class MatchData:
    team1: str
    team2: str
    score: str
    minute: str = ""
    coefficient: float = 0.0
    is_locked: bool = False
    sport_type: str = ""
    league: str = ""
    url: str = ""
    probability: float = 0.0  # Вероятность победы фаворита
    recommendation_type: str = ""  # 'win' or 'total'
    recommendation_value: str = ""  # 'П1', 'ТБ X', 'ТМ Y'
    justification: str = ""  # Обоснование рекомендации
    source: str = ""  # Источник данных

class BetzonaController:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Connection': 'keep-alive',
        }
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # URL-адреса для разных видов спорта
        self.sport_urls = {
            'football': 'https://betzona.ru/live-futbol.html',
            'tennis': 'https://betzona.ru/live-tennis.html',
            'table_tennis': 'https://betzona.ru/live-tennis.html',  # Используем теннис для настольного тенниса
            'handball': 'https://betzona.ru/live-gandball.html'
        }

    def _fetch_page(self, url):
        try:
            response = self.session.get(url, headers=self.headers, allow_redirects=True, timeout=10)
            response.raise_for_status()
            self.logger.info(f"Запрос к Betzona: {url}")
            self.logger.info(f"Получен ответ: {len(response.text)} символов")
            return response.text
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при запросе к Betzona ({url}): {e}")
            return None

    def _parse_match_data(self, match_element, sport_type):
        """Парсинг данных одного матча"""
        try:
            # Проверяем, что это live-матч
            if match_element.get('data-is-live') != '1':
                return None
                
            # Извлекаем команды
            teams = match_element.find_all('div', class_='match-scores-item__team')
            if len(teams) < 2:
                return None
                
            team1 = teams[0].get_text(strip=True)
            team2 = teams[1].get_text(strip=True)
            
            # Извлекаем счет
            score_element = match_element.find('div', class_='match-scores-item__scores_main')
            if not score_element:
                return None
                
            home_score = score_element.find('div', class_='match-scores-item__scores_home')
            away_score = score_element.find('div', class_='match-scores-item__scores_away')
            
            if not home_score or not away_score:
                return None
                
            score = f"{home_score.get_text(strip=True)}:{away_score.get_text(strip=True)}"
            
            # Извлекаем минуту
            minute_element = match_element.find('div', class_='match-scores-item__status')
            minute = ""
            if minute_element:
                minute_text = minute_element.get_text(strip=True)
                # Извлекаем только цифры из текста типа "53′"
                minute_match = re.search(r'(\d+)', minute_text)
                if minute_match:
                    minute = minute_match.group(1)
            
            # Извлекаем лигу/турнир
            league = ""
            tournament_element = match_element.find_parent('div', class_='match-scores-tournament')
            if tournament_element:
                title_element = tournament_element.find('div', class_='match-scores-tournament__header_title')
                if title_element:
                    league = title_element.get_text(strip=True)
            
            # Извлекаем ссылку на матч
            link = ""
            link_element = match_element.find('a')
            if link_element and link_element.get('href'):
                link = link_element.get('href')
                if not link.startswith('http'):
                    link = 'https://betzona.ru' + link
            
            return MatchData(
                team1=team1,
                team2=team2,
                score=score,
                minute=minute,
                league=league,
                url=link,
                sport_type=sport_type
            )
            
        except Exception as e:
            self.logger.error(f"Ошибка при парсинге матча: {e}")
            return None

    def get_live_matches(self, sport_type: str) -> List[MatchData]:
        """Получение live-матчей для указанного вида спорта"""
        url = self.sport_urls.get(sport_type)
        if not url:
            self.logger.warning(f"URL для {sport_type} на Betzona не найден.")
            return []

        html_content = self._fetch_page(url)
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        matches = []

        # Ищем все live-матчи (они находятся в ссылках <a>)
        match_elements = soup.find_all('a', class_='match-scores-item', attrs={'data-is-live': '1'})
        self.logger.info(f"Найдено {len(match_elements)} live-матчей на Betzona для {sport_type}")

        for match_element in match_elements:
            match_data = self._parse_match_data(match_element, sport_type)
            if match_data:
                matches.append(match_data)

        self.logger.info(f"Успешно обработано {len(matches)} матчей для {sport_type}")
        return matches

    def get_all_live_matches(self) -> List[MatchData]:
        """Получение всех live-матчей по всем видам спорта"""
        all_matches = []
        
        for sport in self.sport_urls.keys():
            self.logger.info(f"Получение live-матчей для {sport}...")
            matches = self.get_live_matches(sport)
            all_matches.extend(matches)
            
        return all_matches

def test_betzona_controller():
    logging.info("============================================================")
    logging.info("ТЕСТ КОНТРОЛЛЕРА BETZONA")
    logging.info("============================================================")
    controller = BetzonaController()
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

    logging.info("\n============================================================")
    logging.info("СВОДНАЯ СТАТИСТИКА:")
    logging.info("============================================================")
    for sport in sports:
        count = sum(1 for m in all_matches if m.sport == sport)
        logging.info(f"{sport.upper()}: {count} матчей")

    total_count = len(all_matches)
    logging.info(f"\nВСЕГО: {total_count} матчей")

    if total_count == 0:
        logging.info("\n❌ BETZONA НЕ РАБОТАЕТ. Матчи не найдены.")
        logging.info("Возможные причины:")
        logging.info("- Неправильные селекторы")
        logging.info("- Изменилась структура сайта")
        logging.info("- Нет live-матчей в данный момент")
        logging.info("- Защита от ботов")
    else:
        logging.info("\n✅ BETZONA РАБОТАЕТ. Матчи найдены.")

    logging.info("\n============================================================")
    logging.info("ТЕСТ ЗАВЕРШЕН")
    logging.info("============================================================")

if __name__ == "__main__":
    test_betzona_controller()