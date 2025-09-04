"""
HTTP-контроллер для получения данных с сайтов букмекеров
"""

import requests
import time
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin


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


class HTTPController:
    """HTTP-контроллер для получения данных с сайтов букмекеров"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # URL-адреса сайтов
        self.urls = {
            'winline': {
                'football': 'https://winline.ru/now/football/',
                'tennis': 'https://winline.ru/now/tennis/',
                'table_tennis': 'https://winline.ru/now/table-tennis/',
                'handball': 'https://winline.ru/now/handball/'
            },
            'betboom': {
                'football': 'https://betboom.ru/sport/football?type=live',
                'tennis': 'https://betboom.ru/sport/tennis?type=live',
                'table_tennis': 'https://betboom.ru/sport/table-tennis?type=live',
                'handball': 'https://betboom.ru/sport/handball?type=live'
            },
            'baltbet': {
                'football': 'https://baltbet.ru/live/football',
                'tennis': 'https://baltbet.ru/live/tennis',
                'table_tennis': 'https://baltbet.ru/live/table-tennis',
                'handball': 'https://baltbet.ru/live/handball'
            }
        }
        
        # Селекторы для парсинга
        self.selectors = {
            'winline': {
                'match_container': '.event-item, .match-item',
                'team_names': '.team-name, .participant-name',
                'score': '.score, .result',
                'minute': '.minute, .time',
                'coefficient': '.coefficient, .odds',
                'locked': '.locked, .disabled',
                'league': '.league, .tournament'
            },
            'betboom': {
                'match_container': '.event-item, .match-item',
                'team_names': '.team-name, .participant-name',
                'score': '.score, .result',
                'minute': '.minute, .time',
                'coefficient': '.coefficient, .odds',
                'locked': '.locked, .disabled',
                'league': '.league, .tournament'
            },
            'baltbet': {
                'match_container': '.event-item, .match-item',
                'team_names': '.team-name, .participant-name',
                'score': '.score, .result',
                'minute': '.minute, .time',
                'coefficient': '.coefficient, .odds',
                'locked': '.locked, .disabled',
                'league': '.league, .tournament'
            }
        }
    
    def get_page_content(self, url: str, timeout: int = 30) -> Optional[str]:
        """
        Получение содержимого страницы
        
        Args:
            url (str): URL страницы
            timeout (int): Таймаут запроса
            
        Returns:
            Optional[str]: HTML содержимое или None
        """
        try:
            print(f"HTTP запрос к: {url}")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            # Проверяем кодировку
            if response.encoding == 'ISO-8859-1':
                response.encoding = 'utf-8'
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка HTTP запроса к {url}: {e}")
            return None
    
    def parse_matches(self, html: str, site: str, sport_type: str) -> List[MatchData]:
        """
        Парсинг матчей из HTML
        
        Args:
            html (str): HTML содержимое
            site (str): Название сайта
            sport_type (str): Тип спорта
            
        Returns:
            List[MatchData]: Список матчей
        """
        if not html:
            return []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            selectors = self.selectors.get(site, {})
            
            # Ищем контейнеры матчей
            match_containers = soup.select(selectors.get('match_container', '.event-item'))
            
            matches = []
            for container in match_containers:
                match_data = self._extract_match_data(container, selectors, sport_type)
                if match_data:
                    matches.append(match_data)
            
            return matches
            
        except Exception as e:
            print(f"Ошибка парсинга HTML для {site}: {e}")
            return []
    
    def _extract_match_data(self, container, selectors: Dict, sport_type: str) -> Optional[MatchData]:
        """
        Извлечение данных матча из контейнера
        
        Args:
            container: BeautifulSoup контейнер
            selectors (Dict): Селекторы для извлечения
            sport_type (str): Тип спорта
            
        Returns:
            Optional[MatchData]: Данные матча или None
        """
        try:
            # Извлекаем названия команд
            team_elements = container.select(selectors.get('team_names', '.team-name'))
            if len(team_elements) < 2:
                return None
            
            team1 = team_elements[0].get_text(strip=True)
            team2 = team_elements[1].get_text(strip=True)
            
            # Извлекаем счет
            score_element = container.select_one(selectors.get('score', '.score'))
            score = score_element.get_text(strip=True) if score_element else ""
            
            # Извлекаем минуту
            minute_element = container.select_one(selectors.get('minute', '.minute'))
            minute = minute_element.get_text(strip=True) if minute_element else ""
            
            # Извлекаем коэффициент
            coeff_element = container.select_one(selectors.get('coefficient', '.coefficient'))
            coefficient = 0.0
            if coeff_element:
                coeff_text = coeff_element.get_text(strip=True)
                try:
                    coefficient = float(re.sub(r'[^\d.,]', '', coeff_text).replace(',', '.'))
                except (ValueError, AttributeError):
                    coefficient = 0.0
            
            # Проверяем, заблокирована ли ставка
            is_locked = bool(container.select_one(selectors.get('locked', '.locked')))
            
            # Извлекаем лигу
            league_element = container.select_one(selectors.get('league', '.league'))
            league = league_element.get_text(strip=True) if league_element else ""
            
            # Извлекаем URL матча
            url_element = container.select_one('a')
            url = url_element.get('href', '') if url_element else ""
            
            return MatchData(
                team1=team1,
                team2=team2,
                score=score,
                minute=minute,
                coefficient=coefficient,
                is_locked=is_locked,
                sport_type=sport_type,
                league=league,
                url=url
            )
            
        except Exception as e:
            print(f"Ошибка извлечения данных матча: {e}")
            return None
    
    def get_live_matches(self, site: str, sport_type: str) -> List[MatchData]:
        """
        Получение live-матчей с сайта
        
        Args:
            site (str): Название сайта (winline, betboom, baltbet)
            sport_type (str): Тип спорта
            
        Returns:
            List[MatchData]: Список live-матчей
        """
        url = self.urls.get(site, {}).get(sport_type)
        if not url:
            print(f"URL не найден для {site} - {sport_type}")
            return []
        
        html = self.get_page_content(url)
        if not html:
            return []
        
        matches = self.parse_matches(html, site, sport_type)
        print(f"Найдено {len(matches)} матчей на {site} для {sport_type}")
        
        return matches
    
    def get_all_live_matches(self, sport_type: str) -> List[MatchData]:
        """
        Получение live-матчей со всех сайтов
        
        Args:
            sport_type (str): Тип спорта
            
        Returns:
            List[MatchData]: Объединенный список матчей
        """
        all_matches = []
        
        for site in ['winline', 'betboom', 'baltbet']:
            try:
                matches = self.get_live_matches(site, sport_type)
                all_matches.extend(matches)
                time.sleep(1)  # Пауза между запросами
            except Exception as e:
                print(f"Ошибка получения матчей с {site}: {e}")
                continue
        
        return all_matches
    
    def test_site_accessibility(self) -> Dict[str, bool]:
        """
        Тестирование доступности сайтов
        
        Returns:
            Dict[str, bool]: Результаты тестирования
        """
        results = {}
        
        for site in ['winline', 'betboom', 'baltbet']:
            for sport in ['football', 'tennis', 'table_tennis', 'handball']:
                url = self.urls.get(site, {}).get(sport)
                if url:
                    try:
                        response = self.session.head(url, timeout=10)
                        results[f"{site}_{sport}"] = response.status_code == 200
                    except:
                        results[f"{site}_{sport}"] = False
        
        return results
    
    def close(self):
        """Закрытие сессии"""
        self.session.close()


# Функции для обратной совместимости с существующим кодом
class HTTPBrowserController:
    """Обертка для совместимости с существующим кодом"""
    
    def __init__(self):
        self.http_controller = HTTPController()
        self.current_page = None
    
    def navigate_to_page(self, url: str) -> bool:
        """Совместимость с BrowserController"""
        self.current_page = url
        return True
    
    def find_matches(self, sport_type: str) -> List[MatchData]:
        """Получение матчей через HTTP"""
        # Определяем сайт по URL
        if 'winline.ru' in self.current_page:
            site = 'winline'
        elif 'betboom.ru' in self.current_page:
            site = 'betboom'
        elif 'baltbet.ru' in self.current_page:
            site = 'baltbet'
        else:
            site = 'betboom'  # По умолчанию
        
        return self.http_controller.get_live_matches(site, sport_type)
    
    def get_scores24_matches(self, sport_type: str) -> List[Dict]:
        """Заглушка для Scores24 (пока не реализовано)"""
        # Здесь можно добавить парсинг Scores24 или использовать API
        return []
    
    def analyze_favorite_probability(self, match_data: MatchData, scores24_data: Dict) -> float:
        """Анализ вероятности победы фаворита"""
        # Упрощенный анализ на основе коэффициентов
        if match_data.coefficient > 0:
            # Чем меньше коэффициент, тем выше вероятность
            probability = max(50, 100 - (match_data.coefficient - 1) * 20)
            return min(probability, 95)
        return 50
    
    def calculate_handball_total(self, score: str, minute: str) -> Dict:
        """Расчет тотала для гандбола"""
        if ':' not in score:
            return {}
        
        try:
            home_goals, away_goals = score.split(':')
            home_goals = int(home_goals.strip())
            away_goals = int(away_goals.strip())
            
            total_goals = home_goals + away_goals
            played_minutes = int(minute.replace("'", ""))
            
            # Прогнозный тотал
            predicted_total = (total_goals / played_minutes) * 60
            predicted_total = int(predicted_total) + (1 if predicted_total % 1 > 0 else 0)
            
            # Интервал
            total_more = predicted_total - 4
            total_less = predicted_total + 4
            
            # Определение темпа
            if total_goals < played_minutes:
                tempo = "МЕДЛЕННЫЙ"
                recommendation = f"ТМ {total_less}"
            elif total_goals > played_minutes:
                tempo = "БЫСТРЫЙ"
                recommendation = f"ТБ {total_more}"
            else:
                tempo = "НЕЙТРАЛЬНЫЙ"
                recommendation = f"ТМ {total_less} или ТБ {total_more}"
            
            return {
                'predicted_total': predicted_total,
                'total_more': total_more,
                'total_less': total_less,
                'tempo': tempo,
                'recommendation': recommendation,
                'total_goals': total_goals,
                'played_minutes': played_minutes
            }
            
        except (ValueError, AttributeError):
            return {}
    
    def close_browser(self):
        """Закрытие браузера"""
        self.http_controller.close()
        self.current_page = None