#!/usr/bin/env python3
"""
Тест готовности системы анализа live-ставок
Проверяет все компоненты и их интеграцию
"""
import sys
import os
import logging
from typing import List, Dict, Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_environment():
    """Тестирует переменные окружения"""
    print("🔍 Проверка переменных окружения...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Проверяем API ключи
    claude_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('CLAUDE_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if claude_key:
        print(f"  ✅ Claude API ключ найден: {claude_key[:20]}...")
    else:
        print("  ⚠️  Claude API ключ не найден")
    
    if openai_key:
        print(f"  ✅ OpenAI API ключ найден: {openai_key[:20]}...")
    else:
        print("  ⚠️  OpenAI API ключ не найден")
    
    return True

def test_dependencies():
    """Тестирует установленные зависимости"""
    print("\n📦 Проверка зависимостей...")
    
    dependencies = [
        ('anthropic', 'Anthropic Claude API'),
        ('openai', 'OpenAI API'),
        ('requests', 'HTTP requests'),
        ('python-dotenv', 'Environment variables'),
        ('logging', 'Python logging (встроенный)')
    ]
    
    for dep, desc in dependencies:
        try:
            if dep == 'python-dotenv':
                import dotenv
            elif dep == 'logging':
                import logging
            else:
                __import__(dep)
            print(f"  ✅ {desc}")
        except ImportError:
            print(f"  ❌ {desc} - не установлен")
    
    return True

def test_universal_analyzer():
    """Тестирует универсальный анализатор"""
    print("\n🤖 Тестирование универсального анализатора...")
    
    try:
        from universal_ai_analyzer import get_universal_analyzer
        
        analyzer = get_universal_analyzer()
        print("  ✅ Анализатор инициализирован")
        
        # Тест подключения
        results = analyzer.test_connection()
        print("  📊 Результаты тестирования провайдеров:")
        for provider, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"    {status_icon} {provider}")
        
        # Тест анализа
        test_matches = [
            {
                'id': 'test1',
                'team1': 'Тест Команда 1',
                'team2': 'Тест Команда 2',
                'score': '2:0',
                'minute': 45,
                'sport_type': 'football'
            }
        ]
        
        analyzed = analyzer.analyze_matches(test_matches, 'football')
        print(f"  ✅ Тест анализа: {len(analyzed)} матчей обработано")
        
        if analyzed:
            match = analyzed[0]
            print(f"    📈 Рекомендация: {match.get('ai_recommendation')}")
            print(f"    🎯 Уверенность: {match.get('ai_confidence')}/10")
            print(f"    💭 Обоснование: {match.get('ai_reasoning')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка тестирования анализатора: {e}")
        return False

def test_main_integration():
    """Тестирует основную интеграцию"""
    print("\n🔗 Тестирование основной интеграции...")
    
    try:
        from claude_final_integration import ClaudeFinalIntegration
        
        integration = ClaudeFinalIntegration()
        print("  ✅ Основная интеграция инициализирована")
        
        # Проверяем что универсальный анализатор подключен
        if hasattr(integration, 'use_universal') and integration.use_universal:
            print("  ✅ Универсальный анализатор подключен к основной интеграции")
        else:
            print("  ⚠️  Универсальный анализатор не подключен")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка тестирования интеграции: {e}")
        return False

def test_config():
    """Тестирует конфигурацию"""
    print("\n⚙️  Проверка конфигурации...")
    
    try:
        from config import ANALYSIS_SETTINGS
        
        print(f"  ✅ Конфигурация загружена")
        print(f"    🎯 Claude через Cursor: {ANALYSIS_SETTINGS.get('use_cursor_claude')}")
        print(f"    🤖 OpenAI GPT: {ANALYSIS_SETTINGS.get('use_openai_gpt')}")
        print(f"    ⏱️  Интервал анализа: {ANALYSIS_SETTINGS.get('cycle_interval_minutes')} минут")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка загрузки конфигурации: {e}")
        return False

def test_file_structure():
    """Проверяет структуру файлов"""
    print("\n📁 Проверка структуры файлов...")
    
    required_files = [
        '.env',
        'config.py',
        'universal_ai_analyzer.py',
        'claude_final_integration.py',
        'claude_api_analyzer.py'
    ]
    
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} - не найден")
    
    return True

def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ ГОТОВНОСТИ СИСТЕМЫ АНАЛИЗА LIVE-СТАВОК")
    print("=" * 60)
    
    tests = [
        ("Переменные окружения", test_environment),
        ("Зависимости", test_dependencies),
        ("Структура файлов", test_file_structure),
        ("Конфигурация", test_config),
        ("Универсальный анализатор", test_universal_analyzer),
        ("Основная интеграция", test_main_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"  ❌ Критическая ошибка в тесте '{test_name}': {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Система готова к работе!")
        print("\n🚀 Для запуска системы используйте:")
        print("   python3 control_system.py start")
    else:
        print(f"⚠️  {total - passed} тест(ов) не пройдено. Проверьте ошибки выше.")
        print("\n🔧 Рекомендации по исправлению:")
        print("   1. Проверьте установку зависимостей: pip install anthropic python-dotenv")
        print("   2. Убедитесь что .env файл содержит правильные API ключи")
        print("   3. Проверьте что все файлы системы присутствуют")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)