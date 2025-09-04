#!/usr/bin/env python3
"""
Тест новых правил анализа футбола
"""

import json
import logging
from claude_final_integration import ClaudeFinalIntegration
from multi_source_controller import MatchData

logging.basicConfig(level=logging.INFO)

def create_test_matches():
    """Создает тестовые матчи для проверки новых правил"""
    test_matches = [
        # Тест 1: Топ-команда с преимуществом в 1 гол
        MatchData(
            sport='football',
            team1='Manchester City',
            team2='Brighton',
            score='1:0',
            minute='67',
            league='Premier League',
            link='test_url_1'
        ),
        
        # Тест 2: Обычная команда с преимуществом в 1 гол (не должно пройти)
        MatchData(
            sport='football',
            team1='Fulham',
            team2='Brentford',
            score='1:0',
            minute='55',
            league='Premier League',
            link='test_url_2'
        ),
        
        # Тест 3: Любая команда с преимуществом в 2 гола (должно пройти)
        MatchData(
            sport='football',
            team1='Wolves',
            team2='Crystal Palace',
            score='2:0',
            minute='68',
            league='Premier League',
            link='test_url_3'
        ),
        
        # Тест 4: Топ-команда в топ-лиге, поздняя минута
        MatchData(
            sport='football',
            team1='Barcelona',
            team2='Getafe',
            score='1:0',
            minute='75',
            league='La Liga',
            link='test_url_4'
        ),
        
        # Тест 5: Рано во втором тайме (не должно пройти)
        MatchData(
            sport='football',
            team1='Real Madrid',
            team2='Valencia',
            score='1:0',
            minute='35',
            league='La Liga',
            link='test_url_5'
        ),
        
        # Тест 6: Ничья (не должно пройти)
        MatchData(
            sport='football',
            team1='Liverpool',
            team2='Arsenal',
            score='1:1',
            minute='70',
            league='Premier League',
            link='test_url_6'
        )
    ]
    
    return test_matches

def test_football_analysis():
    """Тестирует новые правила анализа футбола"""
    print("🧪 ТЕСТ НОВЫХ ПРАВИЛ АНАЛИЗА ФУТБОЛА")
    print("=" * 50)
    
    # Создаем анализатор
    analyzer = ClaudeFinalIntegration()
    
    # Создаем тестовые матчи
    test_matches = create_test_matches()
    
    print(f"📊 Тестируем {len(test_matches)} матчей:")
    for i, match in enumerate(test_matches, 1):
        print(f"  {i}. {match.team1} vs {match.team2} - {match.score} ({match.minute}') - {match.league}")
    
    print("\n🤖 Запуск AI-анализа...")
    
    # Анализируем матчи
    recommendations = analyzer.analyze_matches_with_claude(test_matches, 'football')
    
    print(f"\n📈 Результаты анализа:")
    print(f"Найдено рекомендаций: {len(recommendations)}")
    
    if recommendations:
        print("\n✅ РЕКОМЕНДАЦИИ:")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec.team1} vs {rec.team2}")
            print(f"   Счет: {rec.score}")
            print(f"   Рекомендация: {rec.recommendation_value}")
            print(f"   Уверенность: {rec.probability:.1f}%")
            print(f"   Обоснование: {rec.justification}")
    else:
        print("\n❌ Рекомендации не найдены")
        print("Возможные причины:")
        print("- Критерии фаворитизма слишком строгие")
        print("- Минимальная уверенность (85%) не достигнута")
        print("- Время матча менее 45 минут")
    
    print("\n" + "=" * 50)

def test_heuristic_directly():
    """Прямое тестирование эвристического анализа"""
    print("🔍 ПРЯМОЙ ТЕСТ ЭВРИСТИЧЕСКОГО АНАЛИЗА")
    print("=" * 50)
    
    analyzer = ClaudeFinalIntegration()
    
    # Тестовые данные матча
    test_match_data = {
        'team1': 'Manchester City',
        'team2': 'Brighton',
        'score': '2:0',
        'minute': '67',
        'league': 'Premier League'
    }
    
    print(f"Тестируем матч: {test_match_data}")
    
    # Прямой вызов эвристического анализа
    result = analyzer._analyze_match_heuristic(test_match_data)
    
    if result:
        print("\n✅ РЕЗУЛЬТАТ АНАЛИЗА:")
        print(f"Команды: {result['team1']} vs {result['team2']}")
        print(f"Счет: {result['score']}")
        print(f"Рекомендация: {result['recommendation']}")
        print(f"Уверенность: {result['confidence']:.1%}")
        print(f"Обоснование: {result['reasoning']}")
    else:
        print("\n❌ Матч не прошел критерии анализа")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_heuristic_directly()
    print()
    test_football_analysis()