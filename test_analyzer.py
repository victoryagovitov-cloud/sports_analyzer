"""
Тестовый скрипт для проверки работы анализатора
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import LiveBettingAnalyzer
import logging

# Настройка логирования для тестов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_fuzzy_matcher():
    """Тест fuzzy matching"""
    from fuzzy_matcher import FuzzyMatcher
    
    matcher = FuzzyMatcher()
    
    # Тест сопоставления команд
    betboom_teams = ["Манчестер Сити", "Барселона", "Реал Мадрид"]
    scores24_teams = ["Ман Сити", "Барселона Эспаньол", "Реал Мадрид"]
    
    print("Тест сопоставления команд:")
    for team in betboom_teams:
        match, confidence = matcher.match_teams(team, scores24_teams)
        print(f"  {team} -> {match} (уверенность: {confidence}%)")
    
    # Тест сопоставления игроков
    betboom_players = ["Новак Джокович", "Рафаэль Надаль", "Роджер Федерер"]
    scores24_players = ["Джокович Н.", "Надаль Р.", "Федерер Р."]
    
    print("\nТест сопоставления игроков:")
    for player in betboom_players:
        match, confidence = matcher.match_players(player, scores24_players)
        print(f"  {player} -> {match} (уверенность: {confidence}%)")


def test_analyzers():
    """Тест анализаторов"""
    analyzer = LiveBettingAnalyzer()
    
    print("\nТест анализаторов:")
    
    # Тест футбола
    print("Футбол:")
    football_recs = analyzer.football_analyzer.analyze_football_matches()
    print(f"  Найдено рекомендаций: {len(football_recs)}")
    
    # Тест тенниса
    print("Теннис:")
    tennis_recs = analyzer.tennis_analyzer.analyze_tennis_matches()
    print(f"  Найдено рекомендаций: {len(tennis_recs)}")
    
    # Тест настольного тенниса
    print("Настольный теннис:")
    tt_recs = analyzer.table_tennis_analyzer.analyze_table_tennis_matches()
    print(f"  Найдено рекомендаций: {len(tt_recs)}")
    
    # Тест гандбола
    print("Гандбол:")
    handball_recs = analyzer.handball_analyzer.analyze_handball_matches()
    print(f"  Найдено рекомендаций: {len(handball_recs)}")


def test_report_generation():
    """Тест генерации отчета"""
    analyzer = LiveBettingAnalyzer()
    
    print("\nТест генерации отчета:")
    
    # Запускаем анализ
    analyzer.run_single_analysis()
    
    # Генерируем отчет
    report = analyzer.report_generator.generate_telegram_report()
    
    print(f"Размер отчета: {len(report)} символов")
    print("\nПервые 500 символов отчета:")
    print(report[:500] + "..." if len(report) > 500 else report)


def test_handball_total_calculation():
    """Тест расчета тоталов для гандбола"""
    from browser_controller import BrowserController
    
    browser = BrowserController()
    
    print("\nТест расчета тоталов гандбола:")
    
    # Тест 1: Быстрый темп
    total_data = browser.calculate_handball_total("25:23", "40")
    print(f"Быстрый темп (25:23 за 40 мин): {total_data}")
    
    # Тест 2: Медленный темп
    total_data = browser.calculate_handball_total("18:16", "50")
    print(f"Медленный темп (18:16 за 50 мин): {total_data}")
    
    # Тест 3: Нейтральный темп
    total_data = browser.calculate_handball_total("22:18", "40")
    print(f"Нейтральный темп (22:18 за 40 мин): {total_data}")


if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ СИСТЕМЫ АНАЛИЗА LIVE-СТАВОК")
    print("=" * 60)
    
    try:
        # Тест fuzzy matching
        test_fuzzy_matcher()
        
        # Тест анализаторов
        test_analyzers()
        
        # Тест генерации отчета
        test_report_generation()
        
        # Тест расчета тоталов
        test_handball_total_calculation()
        
        print("\n" + "=" * 60)
        print("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nОШИБКА В ТЕСТАХ: {e}")
        import traceback
        traceback.print_exc()