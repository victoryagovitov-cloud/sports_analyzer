"""
Контроллер для сбора данных с Winline.ru
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


class WinlineController:
    """Контроллер для сбора данных с Winline"""
    
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
        
        # URL-адреса Winline
        self.urls = {
            'football': 'https://winline.ru/now/football/',
            'tennis': 'https://winline.ru/now/tennis/',
            'table_tennis': 'https://winline.ru/now/table-tennis/',
            'handball': 'https://winline.ru/now/handball/'
        }
    
    def get_page_content(self, url: str, timeout: int = 30) -> Optional[str]:
        """Получение содержимого страницы"""
        try:
            logger.info(f"Запрос к Winline: {url}")
            response = self.session.get(url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            
            if response.encoding == 'ISO-8859-1':
                response.encoding = 'utf-8'
            
            logger.info(f"Получен ответ: {len(response.text)} символов")
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка HTTP запроса к {url}: {e}")
            return None
    
    def parse_winline_matches(self, html: str, sport_type: str) -> List[MatchData]:
        """Парсинг матчей с Winline"""
        if not html:
            return []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            matches = []
            
            # Ищем различные возможные селекторы для матчей
            possible_selectors = [
                '.event-item',
                '.match-item',
                '.sport-event',
                '.live-event',
                '.game-item',
                '[data-sport]',
                '.event',
                '.match',
                '.game'
            ]
            
            match_containers = []
            for selector in possible_selectors:
                containers = soup.select(selector)
                if containers:
                    logger.info(f"Найдено {len(containers)} контейнеров с селектором: {selector}")
                    match_containers.extend(containers)
                    break
            
            if not match_containers:
                # Попробуем найти любые элементы с текстом, содержащим ":" (счет)
                all_elements = soup.find_all(text=re.compile(r'\d+:\d+'))
                logger.info(f"Найдено {len(all_elements)} элементов с возможным счетом")
                
                # Ищем родительские контейнеры
                for element in all_elements[:10]:  # Ограничиваем для производительности
                    parent = element.parent
                    if parent and parent not in match_containers:
                        match_containers.append(parent)
            
            logger.info(f"Всего найдено {len(match_containers)} контейнеров матчей на Winline")
            
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
            # Получаем весь текст контейнера
            container_text = container.get_text(strip=True)
            
            # Ищем счет в формате X:Y
            score_match = re.search(r'(\d+):(\d+)', container_text)
            if not score_match:
                return None
            
            score = score_match.group(0)
            
            # Ищем названия команд - ищем текст до и после счета
            text_parts = container_text.split(score)
            if len(text_parts) < 2:
                return None
            
            # Извлекаем команды из текста
            before_score = text_parts[0].strip()
            after_score = text_parts[1].strip()
            
            # Пытаемся найти названия команд
            team1 = ""
            team2 = ""
            
            # Ищем команды в разных местах
            team_elements = container.select('.team-name, .participant-name, .competitor-name, .player-name')
            if len(team_elements) >= 2:
                team1 = team_elements[0].get_text(strip=True)
                team2 = team_elements[1].get_text(strip=True)
            else:
                # Пытаемся извлечь из текста
                words = container_text.split()
                score_index = -1
                for i, word in enumerate(words):
                    if ':' in word and re.match(r'\d+:\d+', word):
                        score_index = i
                        break
                
                if score_index > 0:
                    # Берем слова до счета как первую команду
                    team1 = ' '.join(words[:score_index])
                    # Берем слова после счета как вторую команду
                    if score_index + 1 < len(words):
                        team2 = ' '.join(words[score_index + 1:])
            
            if not team1 or not team2:
                return None
            
            # Ищем минуту/время
            minute = ""
            time_elements = container.select('.minute, .time, .match-time, .event-time')
            if time_elements:
                minute = time_elements[0].get_text(strip=True)
            else:
                # Ищем в тексте
                time_match = re.search(r'(\d+[\'\"]?)', container_text)
                if time_match:
                    minute = time_match.group(1)
            
            # Ищем коэффициент
            coefficient = 0.0
            coeff_elements = container.select('.coefficient, .odds, .bet-value, .coeff')
            if coeff_elements:
                coeff_text = coeff_elements[0].get_text(strip=True)
                try:
                    coefficient = float(re.sub(r'[^\d.,]', '', coeff_text).replace(',', '.'))
                except (ValueError, AttributeError):
                    coefficient = 0.0
            
            # Проверяем заблокированность
            is_locked = bool(container.select('.locked, .disabled, .unavailable, .closed'))
            
            # Лига/турнир
            league = ""
            league_elements = container.select('.league, .tournament, .competition, .championship')
            if league_elements:
                league = league_elements[0].get_text(strip=True)
            
            # URL матча
            url = ""
            url_element = container.select_one('a')
            if url_element:
                url = urljoin("https://winline.ru", url_element.get('href', ''))
            
            # Статус
            status = "live" if "live" in container_text.lower() else ""
            
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
                status=status
            )
            
        except Exception as e:
            logger.error(f"Ошибка извлечения данных матча Winline: {e}")
            return None
    
    def get_live_matches(self, sport_type: str) -> List[MatchData]:
        """Получение live-матчей с Winline"""
        url = self.urls.get(sport_type)
        if not url:
            logger.error(f"URL не найден для {sport_type}")
            return []
        
        html = self.get_page_content(url)
        if not html:
            return []
        
        matches = self.parse_winline_matches(html, sport_type)
        logger.info(f"Найдено {len(matches)} матчей на Winline для {sport_type}")
        return matches
    
    def test_all_sports(self) -> Dict[str, List[MatchData]]:
        """Тестирование всех видов спорта"""
        results = {}
        
        for sport in ['football', 'tennis', 'table_tennis', 'handball']:
            logger.info(f"\n--- Тестирование {sport.upper()} ---")
            matches = self.get_live_matches(sport)
            results[sport] = matches
            
            logger.info(f"Найдено {len(matches)} матчей:")
            for i, match in enumerate(matches[:3]):  # Показываем первые 3
                logger.info(f"  {i+1}. {match.team1} - {match.team2}")
                logger.info(f"     Счет: {match.score}, Минута: {match.minute}")
                logger.info(f"     Кэф: {match.coefficient}, Заблокирован: {match.is_locked}")
                logger.info(f"     Лига: {match.league}")
        
        return results
    
    def close(self):
        """Закрытие сессии"""
        self.session.close()


def test_winline_controller():
    """Тест контроллера Winline"""
    print("=" * 60)
    print("ТЕСТ КОНТРОЛЛЕРА WINLINE")
    print("=" * 60)
    
    controller = WinlineController()
    
    try:
        # Тестируем все виды спорта
        results = controller.test_all_sports()
        
        # Сводная статистика
        print("\n" + "=" * 60)
        print("СВОДНАЯ СТАТИСТИКА:")
        print("=" * 60)
        
        total_matches = 0
        for sport, matches in results.items():
            print(f"{sport.upper()}: {len(matches)} матчей")
            total_matches += len(matches)
        
        print(f"\nВСЕГО: {total_matches} матчей")
        
        if total_matches > 0:
            print("\n✅ WINLINE РАБОТАЕТ! Данные успешно получены.")
        else:
            print("\n❌ WINLINE НЕ РАБОТАЕТ. Матчи не найдены.")
            print("Возможные причины:")
            print("- Неправильные селекторы")
            print("- Изменилась структура сайта")
            print("- Нет live-матчей в данный момент")
            print("- Защита от ботов")
    
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
    
    finally:
        controller.close()
        print("\n" + "=" * 60)
        print("ТЕСТ ЗАВЕРШЕН")
        print("=" * 60)


if __name__ == "__main__":
    test_winline_controller()