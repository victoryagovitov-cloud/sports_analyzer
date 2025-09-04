"""
Контроллер для сбора реальных данных с Scores24.live и Winline
"""

import requests
import time
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MatchData:
    """Структура данных о матче"""
    team1: str
    team2: str
    score: str
    minute: str
    coefficient: float
    is_locked: bool
    sport_type: str
    league: str = ""
    url: str = ""
    status: str = ""


class RealDataController:
    """Контроллер для сбора реальных данных"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        # URL-адреса
        self.urls = {
            'scores24': {
                'football': 'https://scores24.live/ru/soccer?matchesFilter=live',
                'tennis': 'https://scores24.live/ru/tennis?matchesFilter=live',
                'table_tennis': 'https://scores24.live/ru/table-tennis?matchesFilter=live',
                'handball': 'https://scores24.live/ru/handball?matchesFilter=live'
            },
            'winline': {
                'football': 'https://winline.ru/now/football/',
                'tennis': 'https://winline.ru/now/tennis/',
                'table_tennis': 'https://winline.ru/now/table-tennis/',
                'handball': 'https://winline.ru/now/handball/'
            }
        }
    
    def get_page_content(self, url: str, timeout: int = 30) -> Optional[str]:
        """Получение содержимого страницы"""
        try:
            logger.info(f"Запрос к: {url}")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            # Проверяем кодировку
            if response.encoding == 'ISO-8859-1':
                response.encoding = 'utf-8'
            
            logger.info(f"Получен ответ: {len(response.text)} символов")
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка HTTP запроса к {url}: {e}")
            return None
    
    def parse_scores24_matches(self, html: str, sport_type: str) -> List[MatchData]:
        """Парсинг матчей с Scores24.live"""
        if not html:
            return []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            matches = []
            
            # Ищем контейнеры матчей
            match_containers = soup.select('.sc-17qxh4e-0.dHxDFU')
            
            logger.info(f"Найдено {len(match_containers)} контейнеров матчей на Scores24")
            
            for container in match_containers:
                match_data = self._extract_scores24_match(container, sport_type)
                if match_data:
                    matches.append(match_data)
            
            return matches
            
        except Exception as e:
            logger.error(f"Ошибка парсинга Scores24: {e}")
            return []
    
    def _extract_scores24_match(self, container, sport_type: str) -> Optional[MatchData]:
        """Извлечение данных матча из контейнера Scores24"""
        try:
            # Названия команд
            team_elements = container.select('.sc-17qxh4e-10.esbhnW')
            if len(team_elements) < 2:
                return None
            
            team1 = team_elements[0].get_text(strip=True)
            team2 = team_elements[1].get_text(strip=True)
            
            # Счет
            score_elements = container.select('.sc-pvs6fr-1.bAhpay')
            score = ""
            if len(score_elements) >= 2:
                score = f"{score_elements[0].get_text(strip=True)}:{score_elements[1].get_text(strip=True)}"
            
            # Минута/статус
            minute_element = container.select_one('.sc-1p31vt4-0.ghrzJz')
            minute = minute_element.get_text(strip=True) if minute_element else ""
            
            # Время матча
            time_element = container.select_one('.sc-oh2bsf-0.fUZLA span')
            time_str = time_element.get_text(strip=True) if time_element else ""
            
            # Лига
            league_element = container.select_one('.sc-5a92rz-5.knTRcb')
            league = league_element.get_text(strip=True) if league_element else ""
            
            # URL матча
            url_element = container.select_one('a[href*="/soccer/m-"]')
            url = urljoin("https://scores24.live", url_element.get('href', '')) if url_element else ""
            
            # Статус (live, finished, etc.)
            status_element = container.select_one('.sc-1p31vt4-0.ghrzJz')
            status = status_element.get_text(strip=True) if status_element else ""
            
            return MatchData(
                team1=team1,
                team2=team2,
                score=score,
                minute=minute,
                coefficient=0.0,  # Scores24 не показывает коэффициенты
                is_locked=False,
                sport_type=sport_type,
                league=league,
                url=url,
                status=status
            )
            
        except Exception as e:
            logger.error(f"Ошибка извлечения данных матча Scores24: {e}")
            return None
    
    def parse_winline_matches(self, html: str, sport_type: str) -> List[MatchData]:
        """Парсинг матчей с Winline"""
        if not html:
            return []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            matches = []
            
            # Ищем контейнеры матчей (нужно определить правильные селекторы)
            match_containers = soup.select('.event-item, .match-item, .sport-event')
            
            logger.info(f"Найдено {len(match_containers)} контейнеров матчей на Winline")
            
            for container in match_containers:
                match_data = self._extract_winline_match(container, sport_type)
                if match_data:
                    matches.append(match_data)
            
            return matches
            
        except Exception as e:
            logger.error(f"Ошибка парсинга Winline: {e}")
            return []
    
    def _extract_winline_match(self, container, sport_type: str) -> Optional[MatchData]:
        """Извлечение данных матча из контейнера Winline"""
        try:
            # Названия команд
            team_elements = container.select('.team-name, .participant-name, .competitor-name')
            if len(team_elements) < 2:
                return None
            
            team1 = team_elements[0].get_text(strip=True)
            team2 = team_elements[1].get_text(strip=True)
            
            # Счет
            score_element = container.select_one('.score, .result, .current-score')
            score = score_element.get_text(strip=True) if score_element else ""
            
            # Минута
            minute_element = container.select_one('.minute, .time, .match-time')
            minute = minute_element.get_text(strip=True) if minute_element else ""
            
            # Коэффициент
            coeff_element = container.select_one('.coefficient, .odds, .bet-value')
            coefficient = 0.0
            if coeff_element:
                coeff_text = coeff_element.get_text(strip=True)
                try:
                    coefficient = float(re.sub(r'[^\d.,]', '', coeff_text).replace(',', '.'))
                except (ValueError, AttributeError):
                    coefficient = 0.0
            
            # Заблокированность
            is_locked = bool(container.select_one('.locked, .disabled, .unavailable'))
            
            # Лига
            league_element = container.select_one('.league, .tournament, .competition')
            league = league_element.get_text(strip=True) if league_element else ""
            
            # URL матча
            url_element = container.select_one('a')
            url = urljoin("https://winline.ru", url_element.get('href', '')) if url_element else ""
            
            return MatchData(
                team1=team1,
                team2=team2,
                score=score,
                minute=minute,
                coefficient=coefficient,
                is_locked=is_locked,
                sport_type=sport_type,
                league=league,
                url=url,
                status="live" if "live" in container.get('class', []) else ""
            )
            
        except Exception as e:
            logger.error(f"Ошибка извлечения данных матча Winline: {e}")
            return None
    
    def get_live_matches(self, site: str, sport_type: str) -> List[MatchData]:
        """Получение live-матчей с сайта"""
        url = self.urls.get(site, {}).get(sport_type)
        if not url:
            logger.error(f"URL не найден для {site} - {sport_type}")
            return []
        
        html = self.get_page_content(url)
        if not html:
            return []
        
        if site == 'scores24':
            matches = self.parse_scores24_matches(html, sport_type)
        elif site == 'winline':
            matches = self.parse_winline_matches(html, sport_type)
        else:
            matches = []
        
        logger.info(f"Найдено {len(matches)} матчей на {site} для {sport_type}")
        return matches
    
    def get_all_live_matches(self, sport_type: str) -> List[MatchData]:
        """Получение live-матчей со всех сайтов"""
        all_matches = []
        
        for site in ['scores24', 'winline']:
            try:
                matches = self.get_live_matches(site, sport_type)
                all_matches.extend(matches)
                time.sleep(1)  # Пауза между запросами
            except Exception as e:
                logger.error(f"Ошибка получения матчей с {site}: {e}")
                continue
        
        return all_matches
    
    def test_site_accessibility(self) -> Dict[str, bool]:
        """Тестирование доступности сайтов"""
        results = {}
        
        for site in ['scores24', 'winline']:
            for sport in ['football', 'tennis', 'table_tennis', 'handball']:
                url = self.urls.get(site, {}).get(sport)
                if url:
                    try:
                        response = self.session.head(url, timeout=10)
                        results[f"{site}_{sport}"] = response.status_code == 200
                        logger.info(f"{site}_{sport}: {response.status_code}")
                    except Exception as e:
                        results[f"{site}_{sport}"] = False
                        logger.error(f"{site}_{sport}: {e}")
        
        return results
    
    def close(self):
        """Закрытие сессии"""
        self.session.close()


def test_real_data_collection():
    """Тест сбора реальных данных"""
    print("=" * 60)
    print("ТЕСТ СБОРА РЕАЛЬНЫХ ДАННЫХ")
    print("=" * 60)
    
    controller = RealDataController()
    
    # Тест доступности
    print("\n1. Тестирование доступности сайтов:")
    accessibility = controller.test_site_accessibility()
    for site_sport, accessible in accessibility.items():
        status = "✅ ДОСТУПЕН" if accessible else "❌ НЕ ДОСТУПЕН"
        print(f"  {site_sport}: {status}")
    
    # Тест сбора данных
    print("\n2. Сбор live-матчей:")
    
    for sport in ['football', 'tennis', 'table_tennis', 'handball']:
        print(f"\n--- {sport.upper()} ---")
        
        # Scores24
        print(f"Scores24 {sport}:")
        scores24_matches = controller.get_live_matches('scores24', sport)
        for i, match in enumerate(scores24_matches[:3]):  # Показываем первые 3
            print(f"  {i+1}. {match.team1} - {match.team2}")
            print(f"     Счет: {match.score}, Минута: {match.minute}")
            print(f"     Лига: {match.league}")
            print(f"     Статус: {match.status}")
        
        # Winline
        print(f"Winline {sport}:")
        winline_matches = controller.get_live_matches('winline', sport)
        for i, match in enumerate(winline_matches[:3]):  # Показываем первые 3
            print(f"  {i+1}. {match.team1} - {match.team2}")
            print(f"     Счет: {match.score}, Минута: {match.minute}")
            print(f"     Кэф: {match.coefficient}, Заблокирован: {match.is_locked}")
            print(f"     Лига: {match.league}")
    
    controller.close()
    print("\n" + "=" * 60)
    print("ТЕСТ ЗАВЕРШЕН")
    print("=" * 60)


if __name__ == "__main__":
    test_real_data_collection()