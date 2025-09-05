#!/usr/bin/env python3
"""
Тест анализатора с внешними знаниями OpenAI
"""

import os
import logging
from external_knowledge_analyzer import get_external_knowledge_analyzer
from multi_source_controller import MatchData

logging.basicConfig(level=logging.INFO)

def test_external_knowledge():
    """Тестирует анализ с внешними знаниями"""
    print("🌐 ТЕСТ АНАЛИЗА С ВНЕШНИМИ ЗНАНИЯМИ")
    print("=" * 45)
    
    # Проверяем API ключ
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY не найден")
        return False
    
    # Создаем анализатор
    analyzer = get_external_knowledge_analyzer(api_key)
    
    # Тестовые матчи с известными командами
    test_matches = [
        # Топ-команды футбола
        MatchData(
            sport='football',
            team1='Manchester City',
            team2='Brighton',
            score='1:0',
            minute='67',
            league='Premier League',
            link='test'
        ),
        
        # Известные теннисисты
        MatchData(
            sport='tennis',
            team1='Новак Джокович',
            team2='Рафаэль Надаль',
            score='1:0',
            minute='2-й сет',
            league='ATP Masters',
            link='test'
        ),
        
        # Менее известные команды
        MatchData(
            sport='football',
            team1='Неизвестная команда А',
            team2='Неизвестная команда Б',
            score='2:1',
            minute='65',
            league='Региональная лига',
            link='test'
        )
    ]
    
    print(f"📊 Тестируем {len(test_matches)} матчей:")
    
    for i, match in enumerate(test_matches, 1):
        print(f"\n{i}. {match.team1} vs {match.team2}")
        print(f"   Счет: {match.score} ({match.minute})")
        print(f"   Лига: {match.league}")
        
        try:
            sport_type = getattr(match, 'sport', 'football')
            recommendations = analyzer.analyze_with_external_knowledge([match], sport_type)
            
            if recommendations:
                rec = recommendations[0]
                print(f"   ✅ Рекомендация: {rec.recommendation_value}")
                print(f"   📊 Уверенность: {rec.probability:.1f}%")
                print(f"   📌 Обоснование: {rec.justification}")
            else:
                print("   ❌ Рекомендация не прошла проверку внешними знаниями")
                
        except Exception as e:
            print(f"   ❌ Ошибка анализа: {e}")
    
    return True

def test_known_vs_unknown():
    """Сравнивает анализ известных и неизвестных команд"""
    print("\n⚖️  СРАВНЕНИЕ: ИЗВЕСТНЫЕ vs НЕИЗВЕСТНЫЕ КОМАНДЫ")
    print("=" * 55)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return
    
    analyzer = get_external_knowledge_analyzer(api_key)
    
    # Известная топ-команда
    known_match = MatchData(
        sport='football',
        team1='Real Madrid',
        team2='Valencia',
        score='2:0',
        minute='70',
        league='La Liga',
        link='test'
    )
    
    # Неизвестная команда
    unknown_match = MatchData(
        sport='football',
        team1='Местная команда А',
        team2='Местная команда Б',
        score='2:0',
        minute='70',
        league='Любительская лига',
        link='test'
    )
    
    matches = [
        ("🏆 Известные (Real Madrid vs Valencia)", known_match),
        ("❓ Неизвестные (Местные команды)", unknown_match)
    ]
    
    for description, match in matches:
        print(f"\n{description}:")
        try:
            recommendations = analyzer.analyze_with_external_knowledge([match], 'football')
            
            if recommendations:
                rec = recommendations[0]
                print(f"   ✅ Рекомендация: {rec.recommendation_value} ({rec.probability:.1f}%)")
                print(f"   📌 Обоснование: {rec.justification}")
            else:
                print("   ❌ Нет рекомендации")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

if __name__ == "__main__":
    success = test_external_knowledge()
    if success:
        test_known_vs_unknown()
        
        print("\n" + "=" * 55)
        print("🌐 Анализатор с внешними знаниями готов к работе!")
        print("💡 Он будет использовать знания OpenAI о командах и игроках")
        print("📊 Это повысит качество анализа и точность прогнозов")