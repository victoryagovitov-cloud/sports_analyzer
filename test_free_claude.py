#!/usr/bin/env python3
"""
Тест БЕСПЛАТНОГО Claude анализа через Cursor
"""

import logging
from cursor_claude_analyzer import cursor_claude_analyzer
from real_claude_integration import real_claude_integration
from multi_source_controller import MatchData

logging.basicConfig(level=logging.INFO)

def test_free_claude_analysis():
    """Тестирует бесплатный Claude анализ"""
    print("🆓 ТЕСТ БЕСПЛАТНОГО CLAUDE АНАЛИЗА ЧЕРЕЗ CURSOR")
    print("=" * 55)
    
    # Создаем тестовые матчи
    test_matches = [
        # Топ-лига, хорошее время, разрыв в счете
        MatchData(
            sport='football',
            team1='Manchester City',
            team2='Brighton',
            score='2:1',
            minute='67',
            league='Premier League',
            link='test'
        ),
        
        # Большой разрыв, топ-команда
        MatchData(
            sport='football',
            team1='Barcelona',
            team2='Getafe',
            score='3:0',
            minute='58',
            league='La Liga',
            link='test'
        ),
        
        # Обычная лига, небольшой разрыв
        MatchData(
            sport='football',
            team1='Локомотив',
            team2='Спартак',
            score='1:0',
            minute='72',
            league='РПЛ',
            link='test'
        ),
        
        # Теннис
        MatchData(
            sport='tennis',
            team1='Джокович Н.',
            team2='Надаль Р.',
            score='1-0 (6-4, 4-3)',
            minute='',
            league='ATP Masters',
            link='test'
        )
    ]
    
    print(f"📊 Тестируем {len(test_matches)} матчей:")
    for i, match in enumerate(test_matches, 1):
        print(f"  {i}. {match.team1} vs {match.team2} ({match.score}, {match.minute}') - {match.league}")
    
    print("\n🤖 Запуск БЕСПЛАТНОГО Claude анализа...")
    
    # Тестируем футбол
    football_matches = [m for m in test_matches if getattr(m, 'sport', '') == 'football']
    recommendations = cursor_claude_analyzer.analyze_matches_with_cursor_claude(football_matches, 'football')
    
    print(f"\n📈 РЕЗУЛЬТАТЫ АНАЛИЗА:")
    print(f"Найдено рекомендаций: {len(recommendations)}")
    
    if recommendations:
        print("\n✅ БЕСПЛАТНЫЕ РЕКОМЕНДАЦИИ ОТ CLAUDE:")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec.team1} vs {rec.team2}")
            print(f"   Счет: {rec.score} ({rec.minute}')")
            print(f"   Лига: {rec.league}")
            print(f"   Рекомендация: {rec.recommendation_value}")
            print(f"   Уверенность: {rec.probability:.1f}%")
            print(f"   Обоснование: {rec.justification}")
    else:
        print("\n❌ Рекомендации не найдены")
        print("Возможные причины:")
        print("- Критерии фаворитизма не выполнены")
        print("- Время матча вне окна 25-75 минут")
        print("- Недостаточная уверенность (<80%)")
    
    # Статистика
    stats = cursor_claude_analyzer.get_statistics()
    print(f"\n💰 ЭКОНОМИЯ:")
    print(f"Анализов выполнено: {stats['total_analyses']}")
    print(f"Использование кэша: {stats['cache_hit_rate']}")
    print(f"Сэкономлено: {stats['estimated_cost_savings']}")
    print(f"💎 ВСЕ БЕСПЛАТНО через Claude в Cursor!")
    
    print("\n" + "=" * 55)
    return len(recommendations) > 0

def test_real_claude_integration():
    """Тестирует реальную Claude интеграцию"""
    print("\n🎯 ТЕСТ РЕАЛЬНОЙ CLAUDE ИНТЕГРАЦИИ")
    print("=" * 40)
    
    test_match = MatchData(
        sport='football',
        team1='Real Madrid',
        team2='Valencia',
        score='2:0',
        minute='65',
        league='La Liga',
        link='test'
    )
    
    print(f"Тестируем матч: {test_match.team1} vs {test_match.team2}")
    print(f"Счет: {test_match.score} ({test_match.minute}') - {test_match.league}")
    
    # Реальный анализ через Claude
    result = real_claude_integration.analyze_football_match_with_real_claude(test_match)
    
    if result:
        print("\n✅ РЕЗУЛЬТАТ РЕАЛЬНОГО CLAUDE АНАЛИЗА:")
        print(f"Рекомендация: {result.recommendation_value}")
        print(f"Уверенность: {result.probability:.1f}%")
        print(f"Обоснование: {result.justification}")
    else:
        print("\n❌ Матч не прошел критерии Claude анализа")
    
    # Статистика экономии
    stats = real_claude_integration.get_free_analysis_stats()
    print(f"\n💰 ЭКОНОМИЯ:")
    print(f"Провайдер: {stats['provider']}")
    print(f"Анализов: {stats['total_free_analyses']}")
    print(f"Сэкономлено: {stats['estimated_savings']}")
    
    return result is not None

def compare_analyzers():
    """Сравнивает разные анализаторы"""
    print("\n⚖️  СРАВНЕНИЕ АНАЛИЗАТОРОВ")
    print("=" * 35)
    
    test_match = MatchData(
        sport='football',
        team1='Bayern Munich',
        team2='Hoffenheim', 
        score='3:1',
        minute='68',
        league='Bundesliga',
        link='test'
    )
    
    print(f"Тестовый матч: {test_match.team1} vs {test_match.team2}")
    print(f"Счет: {test_match.score} ({test_match.minute}') - {test_match.league}")
    
    analyzers = [
        ("🆓 Cursor Claude (БЕСПЛАТНО)", cursor_claude_analyzer.analyze_matches_with_cursor_claude, [test_match], 'football'),
        ("🎯 Real Claude Integration", real_claude_integration.analyze_football_match_with_real_claude, test_match, None)
    ]
    
    print(f"\n📊 Результаты сравнения:")
    
    for name, analyzer_func, data, sport_type in analyzers:
        try:
            if sport_type:
                result = analyzer_func(data, sport_type)
                if result and len(result) > 0:
                    rec = result[0]
                    print(f"  ✅ {name}: {rec.recommendation_value} ({rec.probability:.0f}%)")
                else:
                    print(f"  ❌ {name}: Нет рекомендации")
            else:
                result = analyzer_func(data)
                if result:
                    print(f"  ✅ {name}: {result.recommendation_value} ({result.probability:.0f}%)")
                else:
                    print(f"  ❌ {name}: Нет рекомендации")
                    
        except Exception as e:
            print(f"  ❌ {name}: Ошибка - {e}")

if __name__ == "__main__":
    # Тестируем бесплатный Claude
    success1 = test_free_claude_analysis()
    
    # Тестируем реальную интеграцию
    success2 = test_real_claude_integration()
    
    # Сравниваем анализаторы
    compare_analyzers()
    
    if success1 or success2:
        print("\n🎉 БЕСПЛАТНЫЙ CLAUDE АНАЛИЗ РАБОТАЕТ!")
        print("💰 Экономия: 100% расходов на AI API")
        print("🚀 Система готова к работе без затрат на анализ")
    else:
        print("\n⚠️  Требуется доработка Claude интеграции")