#!/usr/bin/env python3
"""
Тест вызова Claude через Cursor с детальным анализом
"""

import subprocess
import tempfile
import os
import json

def test_cursor_claude_detailed():
    """Тестирует вызов Claude через Cursor с детальным анализом"""
    
    prompt = """
    Ты - эксперт по анализу live-ставок. СТРОГИЕ ПРАВИЛА ДЛЯ ТЕННИСА:
    1. Найди ТОЛЬКО матчи со счетом 1-0 по сетам ИЛИ разрывом ≥4 геймов в первом сете
    2. Определи, является ли игрок, ведущий в счете, объективным фаворитом
    3. Рекомендуй ТОЛЬКО если вероятность победы фаворита >80%
    
    ДЛЯ КАЖДОГО МАТЧА ПРОВЕРЬ:
    - Рейтинг ATP/WTA (разница ≥ 20 позиций)
    - Форму последних 5 матчей (≥ 4 победы у ведущего игрока)
    - Историю личных встреч (H2H: ≥ 3 победы из 5)
    - Турнир (Grand Slam, ATP 250 и т.д. — важен уровень)
    - Показатели подачи и выигранных очков на приёме
    - Психологическое преимущество после выигрыша сета
    - Статистику по сетам (процент выигранных сетов)
    
    Проанализируй следующие матчи СТРОГО по правилам выше:
    
    1. Новак Джокович vs Карлос Алькарас
       Счет: 1-0 (6-4, 3-2)
       Минута: 45
       Лига: ATP Masters 1000
       URL: https://example.com
    
    2. Рафаэль Надаль vs Янник Синнер
       Счет: 0-1 (4-6, 2-3)
       Минута: 30
       Лига: ATP 500
       URL: https://example.com
    
    3. Ига Свёнтек vs Арина Соболенко
       Счет: 1-0 (6-2, 4-1)
       Минута: 60
       Лига: WTA 1000
       URL: https://example.com
    
    Для каждого подходящего матча дай ДЕТАЛЬНОЕ обоснование, включающее:
    - Анализ счета и времени матча
    - Сравнение рейтингов/позиций
    - Анализ формы команд/игроков
    - Историю личных встреч (если применимо)
    - Качество турнира/лиги
    - Психологические факторы
    - Статистические показатели
    
    Верни ТОЛЬКО JSON массив с рекомендациями в формате:
    [
        {
            "team1": "Название команды 1",
            "team2": "Название команды 2", 
            "score": "Счет",
            "recommendation": "П1/П2/Победа игрок",
            "confidence": 0.85,
            "reasoning": "ДЕТАЛЬНОЕ обоснование с анализом рейтингов, формы, истории встреч, качества турнира и статистики"
        }
    ]
    
    Если НЕТ матчей, соответствующих строгим правилам, верни пустой массив [].
    """
    
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(prompt)
        temp_file = f.name
    
    try:
        print("🔍 Тестируем вызов Claude через Cursor с детальным анализом...")
        
        # Пробуем вызвать Claude через Cursor
        try:
            result = subprocess.run([
                'cursor', 'claude', 'analyze', temp_file
            ], capture_output=True, text=True, timeout=120)
            
            print(f"Код возврата: {result.returncode}")
            print(f"Вывод: {result.stdout}")
            print(f"Ошибка: {result.stderr}")
            
            if result.returncode == 0 and result.stdout.strip():
                print("✅ Claude вызван через Cursor!")
                return result.stdout
            else:
                print("❌ Ошибка вызова Claude через Cursor")
                return "[]"
        except Exception as e:
            print(f"❌ Cursor недоступен: {e}")
            return "[]"
        
    finally:
        # Удаляем временный файл
        if os.path.exists(temp_file):
            os.unlink(temp_file)

if __name__ == "__main__":
    result = test_cursor_claude_detailed()
    print(f"\n📋 Результат: {result}")
    
    # Пробуем парсить JSON
    try:
        parsed = json.loads(result)
        print(f"📊 Найдено рекомендаций: {len(parsed)}")
        for i, rec in enumerate(parsed, 1):
            print(f"  {i}. {rec.get('team1')} vs {rec.get('team2')}")
            print(f"     Рекомендация: {rec.get('recommendation')}")
            print(f"     Уверенность: {rec.get('confidence')}")
            print(f"     Обоснование: {rec.get('reasoning', '')[:100]}...")
    except Exception as e:
        print(f"❌ Ошибка парсинга JSON: {e}")