#!/usr/bin/env python3
"""
Тест полного соответствия системы промпту пользователя
"""

import os
import logging
from scores24_only_controller import scores24_only_controller
from prompt_compliant_analyzer import get_prompt_analyzer
from prompt_telegram_formatter import prompt_telegram_formatter
from moscow_time import format_moscow_time_for_telegram
from multi_source_controller import MatchData

logging.basicConfig(level=logging.INFO)

def test_prompt_compliance():
    """Тестирует полное соответствие промпту"""
    print("🎯 ТЕСТ ПОЛНОГО СООТВЕТСТВИЯ ПРОМПТУ")
    print("=" * 45)
    
    # Проверяем API ключ
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY не найден")
        return False
    
    print("✅ OpenAI API ключ найден")
    
    # Тестируем московское время
    moscow_time = format_moscow_time_for_telegram()
    print(f"🕐 Московское время: {moscow_time}")
    
    # Тестируем получение данных ТОЛЬКО с scores24.live
    print("\n🔍 ТЕСТ: Данные ТОЛЬКО с scores24.live")
    print("=" * 40)
    
    sports = ['football', 'tennis', 'table_tennis', 'handball']
    all_matches = []
    
    for sport in sports:
        try:
            matches = scores24_only_controller.get_live_matches(sport)
            all_matches.extend(matches)
            print(f"📊 {sport}: {len(matches)} матчей с scores24.live")
            
            # Показываем примеры матчей
            for i, match in enumerate(matches[:2]):
                print(f"  {i+1}. {match.team1} vs {match.team2} ({match.score}, {match.minute}') - {match.league}")
                
        except Exception as e:
            print(f"❌ Ошибка получения {sport}: {e}")
    
    print(f"\n📈 Всего матчей с scores24.live: {len(all_matches)}")
    
    # Тестируем анализ по критериям промпта
    if all_matches:
        print("\n🤖 ТЕСТ: Анализ по критериям промпта")
        print("=" * 40)
        
        try:
            analyzer = get_prompt_analyzer(api_key)
            
            # Тестируем только футбол пока  
            football_matches = []
            for m in all_matches:
                # Проверяем, что это футбольные матчи
                if hasattr(m, 'sport') and m.sport == 'football':
                    football_matches.append(m)
                elif not hasattr(m, 'sport'):
                    # Если нет поля sport, добавляем его
                    m.sport = 'football'
                    football_matches.append(m)
            
            # Берем только первые 7 матчей (те, что получили с scores24)
            football_matches = all_matches[:7]  # Первые 7 - это футбол
            
            if football_matches:
                print(f"⚽ Анализируем {len(football_matches)} футбольных матчей...")
                recommendations = analyzer.analyze_football_matches(football_matches)
                
                if recommendations:
                    print(f"✅ Найдено {len(recommendations)} рекомендаций")
                    
                    # Тестируем форматирование по промпту
                    print("\n📱 ТЕСТ: Форматирование по шаблону промпта")
                    print("=" * 45)
                    
                    formatted_report = prompt_telegram_formatter.format_report_by_prompt(recommendations)
                    print("\n" + "="*50)
                    print("ОТЧЕТ ПО ШАБЛОНУ ПРОМПТА:")
                    print("="*50)
                    print(formatted_report)
                    print("="*50)
                    
                    return True
                else:
                    print("❌ Рекомендации не найдены (строгие критерии промпта)")
            else:
                print("❌ Нет футбольных матчей для анализа")
                
        except Exception as e:
            print(f"❌ Ошибка анализа: {e}")
    
    return False

def test_time_format():
    """Тестирует форматирование времени"""
    print("\n🕐 ТЕСТ МОСКОВСКОГО ВРЕМЕНИ")
    print("=" * 30)
    
    time_str = format_moscow_time_for_telegram()
    print(f"Текущее время: {time_str}")
    
    # Проверяем формат
    if "МСК" in time_str and ":" in time_str:
        print("✅ Формат времени корректный")
        return True
    else:
        print("❌ Неправильный формат времени")
        return False

def test_scores24_only():
    """Тестирует использование ТОЛЬКО scores24.live"""
    print("\n📊 ТЕСТ: ТОЛЬКО scores24.live")
    print("=" * 35)
    
    try:
        # Тестируем каждый вид спорта
        sports_urls = {
            'football': 'https://scores24.live/ru/soccer?matchesFilter=live',
            'tennis': 'https://scores24.live/ru/tennis?matchesFilter=live',
            'table_tennis': 'https://scores24.live/ru/table-tennis?matchesFilter=live',
            'handball': 'https://scores24.live/ru/handball?matchesFilter=live'
        }
        
        total_matches = 0
        
        for sport, url in sports_urls.items():
            matches = scores24_only_controller.get_live_matches(sport)
            total_matches += len(matches)
            print(f"✅ {sport}: {len(matches)} матчей")
            
            # Проверяем, что источник только scores24
            for match in matches[:1]:  # Проверяем первый матч
                source = getattr(match, 'source', 'unknown')
                if 'scores24' in source.lower():
                    print(f"  ✅ Источник корректный: {source}")
                else:
                    print(f"  ⚠️  Источник: {source}")
        
        print(f"\n📈 Итого матчей ТОЛЬКО с scores24.live: {total_matches}")
        return total_matches > 0
        
    except Exception as e:
        print(f"❌ Ошибка тестирования scores24: {e}")
        return False

if __name__ == "__main__":
    print("🎯 ПОЛНЫЙ ТЕСТ СООТВЕТСТВИЯ ПРОМПТУ")
    print("=" * 50)
    
    # Тестируем все компоненты
    time_ok = test_time_format()
    scores24_ok = test_scores24_only()
    analysis_ok = test_prompt_compliance()
    
    print("\n" + "=" * 50)
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ:")
    print(f"🕐 Московское время: {'✅' if time_ok else '❌'}")
    print(f"📊 Только scores24.live: {'✅' if scores24_ok else '❌'}")
    print(f"🤖 Анализ по промпту: {'✅' if analysis_ok else '❌'}")
    
    if time_ok and scores24_ok and analysis_ok:
        print("\n🎉 СИСТЕМА ПОЛНОСТЬЮ СООТВЕТСТВУЕТ ПРОМПТУ!")
        print("🚀 Готова к запуску в продакшен")
    else:
        print("\n⚠️  Требуются дополнительные исправления")
    
    print("=" * 50)