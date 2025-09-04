#!/usr/bin/env python3
"""
Тест вызова Claude через Cursor API
"""

import subprocess
import tempfile
import os

def test_claude_cursor():
    """Тестирует различные способы вызова Claude через Cursor"""
    
    prompt = """
    Проанализируй следующие футбольные матчи:
    
    1. Манчестер Сити vs Ливерпуль
       Счет: 2:1
       Минута: 67
       Лига: Премьер-лига
    
    2. Барселона vs Реал Мадрид
       Счет: 1:0
       Минута: 45
       Лига: Ла Лига
    
    Верни JSON массив с рекомендациями в формате:
    [
        {
            "team1": "Название команды 1",
            "team2": "Название команды 2", 
            "score": "Счет",
            "recommendation": "П1/П2",
            "confidence": 0.85,
            "reasoning": "Обоснование"
        }
    ]
    """
    
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(prompt)
        temp_file = f.name
    
    try:
        print("🔍 Тестируем различные способы вызова Claude...")
        
        # Способ 1: cursor CLI
        print("\n1. Пробуем cursor CLI...")
        try:
            result = subprocess.run([
                'cursor', 'claude', 'analyze', temp_file
            ], capture_output=True, text=True, timeout=30)
            
            print(f"   Код возврата: {result.returncode}")
            print(f"   Вывод: {result.stdout[:200]}...")
            print(f"   Ошибка: {result.stderr[:200]}...")
            
            if result.returncode == 0 and result.stdout.strip():
                print("   ✅ Cursor CLI работает!")
                return result.stdout
        except Exception as e:
            print(f"   ❌ Cursor CLI недоступен: {e}")
        
        # Способ 2: cursor API
        print("\n2. Пробуем cursor API...")
        try:
            result = subprocess.run([
                'cursor', 'api', 'claude', 'analyze', temp_file
            ], capture_output=True, text=True, timeout=30)
            
            print(f"   Код возврата: {result.returncode}")
            print(f"   Вывод: {result.stdout[:200]}...")
            print(f"   Ошибка: {result.stderr[:200]}...")
            
            if result.returncode == 0 and result.stdout.strip():
                print("   ✅ Cursor API работает!")
                return result.stdout
        except Exception as e:
            print(f"   ❌ Cursor API недоступен: {e}")
        
        # Способ 3: anthropic API
        print("\n3. Пробуем anthropic API...")
        try:
            import anthropic
            client = anthropic.Anthropic()
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            print("   ✅ Anthropic API работает!")
            return response.content[0].text
        except Exception as e:
            print(f"   ❌ Anthropic API недоступен: {e}")
        
        # Способ 4: curl к Claude API
        print("\n4. Пробуем curl к Claude API...")
        try:
            api_key = os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('CLAUDE_API_KEY')
            if api_key:
                import json
                curl_cmd = [
                    'curl', '-X', 'POST',
                    'https://api.anthropic.com/v1/messages',
                    '-H', f'x-api-key: {api_key}',
                    '-H', 'Content-Type: application/json',
                    '-d', json.dumps({
                        "model": "claude-3-sonnet-20240229",
                        "max_tokens": 1000,
                        "messages": [{"role": "user", "content": prompt}]
                    })
                ]
                
                result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    response_data = json.loads(result.stdout)
                    if 'content' in response_data and len(response_data['content']) > 0:
                        print("   ✅ Curl API работает!")
                        return response_data['content'][0]['text']
                else:
                    print(f"   ❌ Curl API ошибка: {result.stderr}")
            else:
                print("   ❌ Нет API ключа для curl")
        except Exception as e:
            print(f"   ❌ Curl API недоступен: {e}")
        
        print("\n❌ Все способы вызова Claude недоступны")
        return "[]"
        
    finally:
        # Удаляем временный файл
        if os.path.exists(temp_file):
            os.unlink(temp_file)

if __name__ == "__main__":
    result = test_claude_cursor()
    print(f"\n📋 Результат: {result}")