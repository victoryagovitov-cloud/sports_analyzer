"""
HTTP-контроллер с демонстрационными данными
Поскольку сайты используют SPA и не предоставляют открытые API,
используем тестовые данные для демонстрации работы системы
"""

import time
import random
from typing import List, Dict, Optional
from dataclasses import dataclass
from http_controller import MatchData


class HTTPControllerDemo:
    """HTTP-контроллер с демонстрационными данными"""
    
    def __init__(self):
        self.current_page = None
        
        # Демонстрационные данные
        self.demo_data = {
            'football': [
                {
                    'team1': 'Манчестер Сити',
                    'team2': 'Арсенал',
                    'score': '2:1',
                    'minute': "67'",
                    'coefficient': 1.85,
                    'is_locked': False,
                    'league': 'Premier League'
                },
                {
                    'team1': 'Барселона',
                    'team2': 'Реал Мадрид',
                    'score': '1:0',
                    'minute': "23'",
                    'coefficient': 2.10,
                    'is_locked': False,
                    'league': 'La Liga'
                },
                {
                    'team1': 'Бавария',
                    'team2': 'Боруссия Д',
                    'score': '3:1',
                    'minute': "78'",
                    'coefficient': 1.45,
                    'is_locked': False,
                    'league': 'Bundesliga'
                }
            ],
            'tennis': [
                {
                    'team1': 'Новак Джокович',
                    'team2': 'Рафаэль Надаль',
                    'score': '1-0',
                    'minute': '6-4',
                    'coefficient': 1.75,
                    'is_locked': False,
                    'league': 'ATP Masters'
                },
                {
                    'team1': 'Роджер Федерер',
                    'team2': 'Энди Мюррей',
                    'score': '2-0',
                    'minute': '6-4',
                    'coefficient': 1.90,
                    'is_locked': False,
                    'league': 'ATP Masters'
                }
            ],
            'table_tennis': [
                {
                    'team1': 'Тимо Болль',
                    'team2': 'Ма Лонг',
                    'score': '1:0',
                    'minute': '11-8',
                    'coefficient': 1.80,
                    'is_locked': False,
                    'league': 'ITTF World Tour'
                },
                {
                    'team1': 'Дмитрий Овчаров',
                    'team2': 'Фань Чжэньдун',
                    'score': '2:0',
                    'minute': '11-6',
                    'coefficient': 1.95,
                    'is_locked': False,
                    'league': 'ITTF World Tour'
                }
            ],
            'handball': [
                {
                    'team1': 'Барселона',
                    'team2': 'Киль',
                    'score': '28:22',
                    'minute': "45'",
                    'coefficient': 1.70,
                    'is_locked': False,
                    'league': 'Champions League'
                },
                {
                    'team1': 'ПСЖ',
                    'team2': 'Монпелье',
                    'score': '25:18',
                    'minute': "38'",
                    'coefficient': 1.85,
                    'is_locked': False,
                    'league': 'Champions League'
                },
                {
                    'team1': 'Вардар',
                    'team2': 'Санкт-Петербург',
                    'score': '32:28',
                    'minute': "52'",
                    'coefficient': 1.60,
                    'is_locked': False,
                    'league': 'Champions League'
                }
            ]
        }
    
    def navigate_to_page(self, url: str) -> bool:
        """Совместимость с BrowserController"""
        print(f"HTTP Demo: Переход на {url}")
        self.current_page = url
        time.sleep(0.5)  # Имитация загрузки
        return True
    
    def find_matches(self, sport_type: str) -> List[MatchData]:
        """Получение демонстрационных матчей"""
        print(f"HTTP Demo: Получение {sport_type} матчей")
        
        if sport_type not in self.demo_data:
            return []
        
        matches = []
        for data in self.demo_data[sport_type]:
            # Добавляем случайные вариации для реалистичности
            if random.random() < 0.7:  # 70% шанс что матч будет показан
                match = MatchData(
                    team1=data['team1'],
                    team2=data['team2'],
                    score=data['score'],
                    minute=data['minute'],
                    coefficient=data['coefficient'] + random.uniform(-0.1, 0.1),
                    is_locked=data['is_locked'],
                    sport_type=sport_type,
                    league=data['league'],
                    url=f"https://demo.com/match/{random.randint(1000, 9999)}"
                )
                matches.append(match)
        
        print(f"HTTP Demo: Найдено {len(matches)} матчей")
        return matches
    
    def get_scores24_matches(self, sport_type: str) -> List[Dict]:
        """Демонстрационные данные Scores24"""
        print(f"HTTP Demo: Получение Scores24 данных для {sport_type}")
        
        # Демонстрационные статистики
        demo_stats = {
            'football': [
                {
                    'team1': 'Ман Сити',
                    'team2': 'Арсенал',
                    'score': '2:1',
                    'minute': '67',
                    'statistics': {
                        'form_team1': 'WWLWW',
                        'form_team2': 'LWWLW',
                        'position_team1': 1,
                        'position_team2': 3,
                        'league_level': 'Premier League'
                    }
                },
                {
                    'team1': 'Барселона',
                    'team2': 'Реал Мадрид',
                    'score': '1:0',
                    'minute': '23',
                    'statistics': {
                        'form_team1': 'WWWWW',
                        'form_team2': 'WLWWL',
                        'position_team1': 1,
                        'position_team2': 2,
                        'league_level': 'La Liga'
                    }
                }
            ],
            'tennis': [
                {
                    'player1': 'Джокович Н.',
                    'player2': 'Надаль Р.',
                    'score': '1-0',
                    'games': '6-4',
                    'statistics': {
                        'rating_player1': 1,
                        'rating_player2': 2,
                        'form_player1': 'WWWWW',
                        'form_player2': 'WWLWW',
                        'h2h': '30-28'
                    }
                }
            ],
            'table_tennis': [
                {
                    'player1': 'Болль Т.',
                    'player2': 'Ма Л.',
                    'score': '1:0',
                    'statistics': {
                        'rating_player1': 15,
                        'rating_player2': 3,
                        'form_player1': 'WWLWW',
                        'form_player2': 'LWWLW'
                    }
                }
            ],
            'handball': [
                {
                    'team1': 'Барселона Эспаньол',
                    'team2': 'Киль',
                    'score': '28:22',
                    'minute': '45',
                    'statistics': {
                        'form_team1': 'WWWWW',
                        'form_team2': 'WLWWL',
                        'position_team1': 1,
                        'position_team2': 4,
                        'avg_goals_team1': 32.5,
                        'avg_goals_team2': 28.2
                    }
                }
            ]
        }
        
        return demo_stats.get(sport_type, [])
    
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
        print("HTTP Demo: Закрытие браузера")
        self.current_page = None


# Функция для замены в main.py
def get_http_controller():
    """Получение HTTP-контроллера"""
    return HTTPControllerDemo()