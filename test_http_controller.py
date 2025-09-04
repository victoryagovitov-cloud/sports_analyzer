"""
Тестовый скрипт для проверки HTTP-контроллера
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from http_controller import HTTPController, HTTPBrowserController
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_site_accessibility():
    """Тест доступности сайтов"""
    print("=" * 60)
    print("ТЕСТ ДОСТУПНОСТИ САЙТОВ")
    print("=" * 60)
    
    controller = HTTPController()
    results = controller.test_site_accessibility()
    
    for site_sport, accessible in results.items():
        status = "✅ ДОСТУПЕН" if accessible else "❌ НЕ ДОСТУПЕН"
        print(f"{site_sport}: {status}")
    
    controller.close()


def test_http_parsing():
    """Тест парсинга HTTP-страниц"""
    print("\n" + "=" * 60)
    print("ТЕСТ ПАРСИНГА HTTP-СТРАНИЦ")
    print("=" * 60)
    
    controller = HTTPController()
    
    # Тестируем каждый сайт
    for site in ['winline', 'betboom', 'baltbet']:
        print(f"\n--- Тестирование {site.upper()} ---")
        
        for sport in ['football', 'tennis', 'table_tennis', 'handball']:
            try:
                matches = controller.get_live_matches(site, sport)
                print(f"  {sport}: {len(matches)} матчей")
                
                # Показываем первые 2 матча
                for i, match in enumerate(matches[:2]):
                    print(f"    {i+1}. {match.team1} - {match.team2}")
                    print(f"       Счет: {match.score}, Минута: {match.minute}")
                    print(f"       Кэф: {match.coefficient}, Заблокирован: {match.is_locked}")
                    print(f"       Лига: {match.league}")
                
            except Exception as e:
                print(f"  {sport}: ОШИБКА - {e}")
    
    controller.close()


def test_http_browser_controller():
    """Тест HTTPBrowserController для совместимости"""
    print("\n" + "=" * 60)
    print("ТЕСТ HTTP BROWSER CONTROLLER")
    print("=" * 60)
    
    controller = HTTPBrowserController()
    
    # Тестируем переход на страницы
    test_urls = [
        'https://winline.ru/now/football/',
        'https://betboom.ru/sport/football?type=live',
        'https://baltbet.ru/live/football'
    ]
    
    for url in test_urls:
        print(f"\nТестирование URL: {url}")
        
        if controller.navigate_to_page(url):
            print("  ✅ Переход успешен")
            
            # Получаем матчи
            matches = controller.find_matches('football')
            print(f"  📊 Найдено {len(matches)} футбольных матчей")
            
            # Показываем первые 2 матча
            for i, match in enumerate(matches[:2]):
                print(f"    {i+1}. {match.team1} - {match.team2}")
                print(f"       Счет: {match.score}, Кэф: {match.coefficient}")
        else:
            print("  ❌ Ошибка перехода")
    
    controller.close_browser()


def test_handball_total_calculation():
    """Тест расчета тоталов для гандбола"""
    print("\n" + "=" * 60)
    print("ТЕСТ РАСЧЕТА ТОТАЛОВ ГАНДБОЛА")
    print("=" * 60)
    
    controller = HTTPBrowserController()
    
    test_cases = [
        ("25:23", "40"),  # Быстрый темп
        ("18:16", "50"),  # Медленный темп
        ("22:18", "40"),  # Нейтральный темп
        ("30:25", "35"),  # Очень быстрый темп
        ("15:12", "60"),  # Очень медленный темп
    ]
    
    for score, minute in test_cases:
        total_data = controller.calculate_handball_total(score, minute)
        print(f"\nСчет: {score}, Минута: {minute}")
        
        if total_data:
            print(f"  Прогнозный тотал: {total_data['predicted_total']}")
            print(f"  ТБ: {total_data['total_more']}, ТМ: {total_data['total_less']}")
            print(f"  Темп: {total_data['tempo']}")
            print(f"  Рекомендация: {total_data['recommendation']}")
        else:
            print("  ❌ Ошибка расчета")
    
    controller.close_browser()


def test_favorite_probability():
    """Тест анализа вероятности фаворита"""
    print("\n" + "=" * 60)
    print("ТЕСТ АНАЛИЗА ВЕРОЯТНОСТИ ФАВОРИТА")
    print("=" * 60)
    
    controller = HTTPBrowserController()
    
    from http_controller import MatchData
    
    test_matches = [
        MatchData("Команда А", "Команда Б", "2:1", "67'", 1.5, False, "football"),
        MatchData("Команда В", "Команда Г", "1:0", "23'", 2.1, False, "football"),
        MatchData("Команда Д", "Команда Е", "3:0", "45'", 1.2, False, "football"),
    ]
    
    for match in test_matches:
        probability = controller.analyze_favorite_probability(match, {})
        print(f"{match.team1} - {match.team2}")
        print(f"  Счет: {match.score}, Кэф: {match.coefficient}")
        print(f"  Вероятность победы фаворита: {probability:.1f}%")
        print()
    
    controller.close_browser()


if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ HTTP-КОНТРОЛЛЕРА")
    print("=" * 60)
    
    try:
        # Тест доступности сайтов
        test_site_accessibility()
        
        # Тест парсинга
        test_http_parsing()
        
        # Тест HTTPBrowserController
        test_http_browser_controller()
        
        # Тест расчета тоталов
        test_handball_total_calculation()
        
        # Тест анализа вероятности
        test_favorite_probability()
        
        print("\n" + "=" * 60)
        print("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nОШИБКА В ТЕСТАХ: {e}")
        import traceback
        traceback.print_exc()