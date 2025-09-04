#!/usr/bin/env python3
"""
Демонстрация работы с Claude для анализа матчей
"""

import json
import logging
from typing import List, Dict, Any
from multi_source_controller import MatchData

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def create_tennis_analysis_prompt(matches: List[MatchData]) -> str:
    """Создает промпт для анализа теннисных матчей"""
    
    matches_text = ""
    for i, match in enumerate(matches, 1):
        matches_text += f"{i}. {match.team1} vs {match.team2}\n"
        matches_text += f"   Счет: {match.score}\n"
        matches_text += f"   Минута: {match.minute}\n"
        matches_text += f"   Лига: {match.league}\n\n"
    
    prompt = f"""
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
    
    {matches_text}
    
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
        {{
            "team1": "Название команды 1",
            "team2": "Название команды 2", 
            "score": "Счет",
            "recommendation": "П1/П2/Победа игрок",
            "confidence": 0.85,
            "reasoning": "ДЕТАЛЬНОЕ обоснование с анализом рейтингов, формы, истории встреч, качества турнира и статистики"
        }}
    ]
    
    Если НЕТ матчей, соответствующих строгим правилам, верни пустой массив [].
    """
    
    return prompt

def demo_tennis_analysis():
    """Демонстрация анализа теннисных матчей"""
    
    # Создаем тестовые данные
    test_matches = [
        MatchData(
            sport="tennis",
            team1="Новак Джокович",
            team2="Карлос Алькарас",
            score="1-0 (6-4, 3-2)",
            minute="45",
            league="ATP Masters 1000"
        ),
        MatchData(
            sport="tennis",
            team1="Рафаэль Надаль",
            team2="Янник Синнер",
            score="0-1 (4-6, 2-3)",
            minute="30",
            league="ATP 500"
        ),
        MatchData(
            sport="tennis",
            team1="Ига Свёнтек",
            team2="Арина Соболенко",
            score="1-0 (6-2, 4-1)",
            minute="60",
            league="WTA 1000"
        )
    ]
    
    # Создаем промпт
    prompt = create_tennis_analysis_prompt(test_matches)
    
    print("🎾 ДЕМОНСТРАЦИЯ АНАЛИЗА ТЕННИСНЫХ МАТЧЕЙ")
    print("=" * 50)
    print("\n📋 Промпт для Claude:")
    print("-" * 30)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    
    print("\n🔍 Тестовые матчи:")
    print("-" * 30)
    for i, match in enumerate(test_matches, 1):
        print(f"{i}. {match.team1} vs {match.team2}")
        print(f"   Счет: {match.score}")
        print(f"   Лига: {match.league}")
    
    print("\n💡 Инструкции для использования:")
    print("-" * 30)
    print("1. Скопируйте промпт выше")
    print("2. Вставьте его в чат с Claude в Cursor")
    print("3. Получите JSON ответ с рекомендациями")
    print("4. Вставьте ответ обратно в систему")
    
    return prompt

def demo_football_analysis():
    """Демонстрация анализа футбольных матчей"""
    
    # Создаем тестовые данные
    test_matches = [
        MatchData(
            sport="football",
            team1="Манчестер Сити",
            team2="Ливерпуль",
            score="2:1",
            minute="67",
            league="Премьер-лига"
        ),
        MatchData(
            sport="football",
            team1="Барселона",
            team2="Реал Мадрид",
            score="1:0",
            minute="45",
            league="Ла Лига"
        ),
        MatchData(
            sport="football",
            team1="Бавария",
            team2="Боруссия Дортмунд",
            score="3:0",
            minute="80",
            league="Бундеслига"
        )
    ]
    
    matches_text = ""
    for i, match in enumerate(test_matches, 1):
        matches_text += f"{i}. {match.team1} vs {match.team2}\n"
        matches_text += f"   Счет: {match.score}\n"
        matches_text += f"   Минута: {match.minute}\n"
        matches_text += f"   Лига: {match.league}\n\n"
    
    prompt = f"""
    Ты - эксперт по анализу live-ставок. СТРОГИЕ ПРАВИЛА ДЛЯ ФУТБОЛА:
    1. Найди ТОЛЬКО матчи с НЕ ничейным счетом (1:0, 2:1, 0:1, etc.) - НЕ ничья
    2. Определи, является ли команда, ведущая в счете, объективным фаворитом
    3. Рекомендуй ТОЛЬКО если вероятность победы фаворита >80%
    
    ДЛЯ КАЖДОГО МАТЧА ПРОВЕРЬ:
    - Время матча (чем больше времени, тем выше вероятность удержания преимущества)
    - Разница в счете (чем больше разница, тем выше вероятность победы)
    - Качество лиги (высшие лиги = более стабильные результаты)
    - Форма команд (последние 5 матчей)
    - Позиция в таблице
    
    Проанализируй следующие матчи СТРОГО по правилам выше:
    
    {matches_text}
    
    Верни ТОЛЬКО JSON массив с рекомендациями в формате:
    [
        {{
            "team1": "Название команды 1",
            "team2": "Название команды 2", 
            "score": "Счет",
            "recommendation": "П1/П2",
            "confidence": 0.85,
            "reasoning": "ДЕТАЛЬНОЕ обоснование с анализом времени матча, разницы в счете, качества лиги, формы команд и позиции в таблице"
        }}
    ]
    
    Если НЕТ матчей, соответствующих строгим правилам, верни пустой массив [].
    """
    
    print("\n⚽ ДЕМОНСТРАЦИЯ АНАЛИЗА ФУТБОЛЬНЫХ МАТЧЕЙ")
    print("=" * 50)
    print("\n📋 Промпт для Claude:")
    print("-" * 30)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    
    print("\n🔍 Тестовые матчи:")
    print("-" * 30)
    for i, match in enumerate(test_matches, 1):
        print(f"{i}. {match.team1} vs {match.team2}")
        print(f"   Счет: {match.score} ({match.minute}')")
        print(f"   Лига: {match.league}")
    
    return prompt

if __name__ == "__main__":
    print("🚀 ДЕМОНСТРАЦИЯ РАБОТЫ С CLAUDE ДЛЯ АНАЛИЗА МАТЧЕЙ")
    print("=" * 60)
    
    # Демонстрация тенниса
    tennis_prompt = demo_tennis_analysis()
    
    # Демонстрация футбола
    football_prompt = demo_football_analysis()
    
    print("\n" + "=" * 60)
    print("✅ Демонстрация завершена!")
    print("\n📝 Следующие шаги:")
    print("1. Используйте промпты выше для анализа с Claude")
    print("2. Получите JSON ответы")
    print("3. Интегрируйте ответы в систему")
    print("4. Настройте автоматический вызов Claude API")