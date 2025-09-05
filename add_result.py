#!/usr/bin/env python3
"""
Скрипт для добавления результатов прогнозов вручную
"""

import sys
import logging
from ml_tracking_system import ml_tracker

logging.basicConfig(level=logging.INFO)

def add_match_result():
    """Добавляет результат матча вручную"""
    
    if len(sys.argv) < 6:
        print("📊 ДОБАВЛЕНИЕ РЕЗУЛЬТАТА ПРОГНОЗА")
        print("=" * 35)
        print()
        print("Использование:")
        print('python3 add_result.py "Команда1" "Команда2" "Рекомендация" "Результат" "Заметки"')
        print()
        print("Примеры:")
        print('python3 add_result.py "Dinthar FC" "Пекхэм Таун" "П1" "loss" "Матч завершился 2:3"')
        print('python3 add_result.py "Маркус Уолтерс" "Энрике Бого" "Победа игрока" "win" "Выиграл 2:1 по сетам"')
        print()
        print("Результат:")
        print("  win   - выигрыш")
        print("  loss  - проигрыш")
        print("  push  - возврат")
        print()
        return False
    
    team1 = sys.argv[1]
    team2 = sys.argv[2] 
    recommendation = sys.argv[3]
    result = sys.argv[4]
    notes = sys.argv[5] if len(sys.argv) > 5 else ""
    
    print(f"📊 Добавление результата:")
    print(f"Матч: {team1} vs {team2}")
    print(f"Прогноз: {recommendation}")
    print(f"Результат: {result}")
    print(f"Заметки: {notes}")
    
    # Проверяем корректность результата
    if result not in ['win', 'loss', 'push']:
        print("❌ Ошибка: результат должен быть 'win', 'loss' или 'push'")
        return False
    
    try:
        # Добавляем в ML систему
        ml_tracker.add_manual_result(team1, team2, recommendation, result, notes)
        print("✅ Результат добавлен в ML лог")
        
        # Показываем текущую статистику
        stats = ml_tracker.generate_daily_stats()
        if stats:
            total = stats['total_predictions']
            wins = stats['wins'] 
            losses = stats['losses']
            win_rate = stats['win_rate']
            
            print(f"\n📈 Текущая статистика за день:")
            print(f"Прогнозов: {total}")
            print(f"Выигрышей: {wins}")
            print(f"Проигрышей: {losses}")
            print(f"Винрейт: {win_rate:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка добавления результата: {e}")
        return False

def show_daily_stats():
    """Показывает текущую дневную статистику"""
    try:
        stats = ml_tracker.generate_daily_stats()
        
        if not stats or stats['total_predictions'] == 0:
            print("📊 Статистика за сегодня пока пуста")
            return
        
        print("📊 СТАТИСТИКА ЗА ДЕНЬ:")
        print("=" * 25)
        print(f"Всего прогнозов: {stats['total_predictions']}")
        print(f"С результатами: {stats['predictions_with_results']}")
        print(f"Выигрышей: {stats['wins']}")
        print(f"Проигрышей: {stats['losses']}")
        print(f"Винрейт: {stats['win_rate']:.1f}%")
        
        # По видам спорта
        by_sport = stats.get('by_sport', {})
        if by_sport:
            print("\nПо видам спорта:")
            for sport, data in by_sport.items():
                if data['total'] > 0:
                    print(f"  {sport}: {data['wins']}/{data['total']} ({data['win_rate']:.1f}%)")
        
    except Exception as e:
        print(f"❌ Ошибка получения статистики: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "stats":
        show_daily_stats()
    else:
        add_match_result()