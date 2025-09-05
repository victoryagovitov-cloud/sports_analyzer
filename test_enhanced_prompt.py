#!/usr/bin/env python3
"""
Тест улучшенного промпта для анализа матчей
"""

import os
import logging
from enhanced_openai_analyzer import EnhancedOpenAIAnalyzer
from enhanced_telegram_formatter import enhanced_formatter
from totals_calculator import totals_calculator
from multi_source_controller import MatchData

logging.basicConfig(level=logging.INFO)

def test_enhanced_analyzer():
    """Тестирует улучшенный анализатор"""
    print("🤖 ТЕСТ УЛУЧШЕННОГО OPENAI АНАЛИЗАТОРА")
    print("=" * 45)
    
    # Проверяем API ключ
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY не найден в переменных окружения")
        print("Установите: export OPENAI_API_KEY='ваш_ключ'")
        return False
    
    # Создаем анализатор
    analyzer = EnhancedOpenAIAnalyzer(api_key)
    
    # Тестируем подключение
    if not analyzer.test_enhanced_connection():
        print("❌ Ошибка подключения к OpenAI")
        return False
    
    # Создаем тестовые матчи по новым критериям
    test_matches = [
        # Футбол: 25-75 минута, не ничья
        MatchData(
            sport='football',
            team1='Manchester City',
            team2='Brighton',
            score='2:1',
            minute='67',
            league='Premier League',
            link='test'
        ),
        
        # Теннис: преимущество по сетам
        MatchData(
            sport='tennis',
            team1='Джокович Н.',
            team2='Надаль Р.',
            score='1-0 (6-4, 3-2)',
            minute='',
            league='ATP Masters',
            link='test'
        ),
        
        # Гандбол: ≥4 голов разрыв, вторая половина
        MatchData(
            sport='handball',
            team1='Барселона',
            team2='Киль',
            score='32:26',
            minute='48',
            league='Champions League',
            link='test'
        )
    ]
    
    print(f"📊 Тестируем {len(test_matches)} матчей с новыми критериями:")
    
    all_recommendations = []
    
    # Тестируем каждый вид спорта
    for sport_type in ['football', 'tennis', 'handball']:
        sport_matches = [m for m in test_matches if getattr(m, 'sport', '') == sport_type]
        
        if sport_matches:
            print(f"\n🔍 Анализ {sport_type}:")
            for match in sport_matches:
                print(f"  - {match.team1} vs {match.team2} ({match.score}, {match.minute}') - {match.league}")
            
            try:
                recommendations = analyzer.analyze_matches_with_enhanced_gpt(sport_matches, sport_type)
                all_recommendations.extend(recommendations)
                
                if recommendations:
                    print(f"✅ Найдено {len(recommendations)} рекомендаций для {sport_type}")
                else:
                    print(f"❌ Рекомендации для {sport_type} не найдены")
                    
            except Exception as e:
                print(f"❌ Ошибка анализа {sport_type}: {e}")
    
    # Тестируем тоталы для гандбола
    handball_matches = [m for m in test_matches if getattr(m, 'sport', '') == 'handball']
    if handball_matches:
        print(f"\n📊 Тест расчета тоталов:")
        for match in handball_matches:
            totals_data = totals_calculator.calculate_handball_totals(match)
            if totals_data:
                print(f"  ✅ {match.team1} vs {match.team2}: {totals_data['recommendation']} (темп: {totals_data['tempo']})")
                
                # Создаем рекомендацию по тоталам
                totals_rec = totals_calculator.create_totals_recommendation(match, totals_data)
                if totals_rec:
                    all_recommendations.append(totals_rec)
    
    # Тестируем форматирование отчета
    if all_recommendations:
        print(f"\n📱 ТЕСТ ФОРМАТИРОВАНИЯ ОТЧЕТА:")
        print(f"Всего рекомендаций: {len(all_recommendations)}")
        
        formatted_report = enhanced_formatter.format_enhanced_report(all_recommendations)
        print("\n" + "="*50)
        print("СГЕНЕРИРОВАННЫЙ ОТЧЕТ:")
        print("="*50)
        print(formatted_report)
        print("="*50)
        
        return True
    else:
        print("\n❌ Нет рекомендаций для форматирования")
        return False

def test_totals_calculator():
    """Тестирует калькулятор тоталов отдельно"""
    print("\n📊 ТЕСТ КАЛЬКУЛЯТОРА ТОТАЛОВ")
    print("=" * 35)
    
    test_handball_matches = [
        {
            'team1': 'Команда А', 'team2': 'Команда Б',
            'score': '28:22', 'minute': '48',
            'expected_total': 'ТМ', 'expected_tempo': 'МЕДЛЕННЫЙ'
        },
        {
            'team1': 'Команда В', 'team2': 'Команда Г', 
            'score': '35:30', 'minute': '45',
            'expected_total': 'ТБ', 'expected_tempo': 'БЫСТРЫЙ'
        }
    ]
    
    for test_data in test_handball_matches:
        match = MatchData(
            sport='handball',
            team1=test_data['team1'],
            team2=test_data['team2'],
            score=test_data['score'],
            minute=test_data['minute'],
            league='Test League',
            link='test'
        )
        
        totals_result = totals_calculator.calculate_handball_totals(match)
        
        if totals_result:
            print(f"✅ {match.team1} vs {match.team2} ({match.score}, {match.minute}'):")
            print(f"   Прогноз: {totals_result['recommendation']}")
            print(f"   Темп: {totals_result['tempo']}")
            print(f"   Расчет: {totals_result['predicted_total']} (точный: {totals_result['predicted_total_float']:.2f})")
        else:
            print(f"❌ Ошибка расчета для {match.team1} vs {match.team2}")

if __name__ == "__main__":
    # Тестируем калькулятор тоталов
    test_totals_calculator()
    
    # Тестируем улучшенный анализатор
    test_enhanced_analyzer()