# Руководство по переходу на HTTP-запросы

## Обзор изменений

Система была успешно адаптирована для работы с HTTP-запросами вместо Browser MCP. Теперь используются прямые HTTP-запросы к сайтам букмекеров.

## Что изменилось

### 1. Новые файлы
- `http_controller.py` - HTTP-контроллер для реальных запросов
- `http_controller_demo.py` - Демо-контроллер с тестовыми данными
- `test_http_controller.py` - Тесты HTTP-функциональности

### 2. Обновленные файлы
- `main.py` - использует HTTPControllerDemo вместо BrowserController
- `config.py` - добавлены URL для HTTP-запросов
- Все анализаторы обновлены для работы с HTTP-контроллером

## Текущее состояние

### ✅ Работает
- Система полностью функциональна с демо-данными
- Все анализаторы работают корректно
- Генерация отчетов работает
- Циклический анализ работает

### ⚠️ Требует настройки
- Селекторы для парсинга реальных сайтов
- Обработка защиты от ботов (Cloudflare, QRATOR)
- Настройка User-Agent и заголовков

## Переход на реальные данные

### Шаг 1: Анализ структуры сайтов

Для каждого сайта нужно определить правильные селекторы:

```python
# Пример для betboom.ru
selectors = {
    'match_container': '.event-item, .match-item, .sport-event',
    'team_names': '.team-name, .participant-name, .competitor-name',
    'score': '.score, .result, .current-score',
    'minute': '.minute, .time, .match-time',
    'coefficient': '.coefficient, .odds, .bet-value',
    'locked': '.locked, .disabled, .unavailable',
    'league': '.league, .tournament, .competition'
}
```

### Шаг 2: Обработка защиты

Добавить обработку различных типов защиты:

```python
# Cloudflare
if 'cloudflare' in response.headers.get('server', '').lower():
    # Использовать selenium или undetected-chromedriver
    
# QRATOR
if 'qrator' in response.headers.get('server', '').lower():
    # Добавить специальные заголовки
```

### Шаг 3: Настройка User-Agent

```python
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0'
})
```

### Шаг 4: Обработка JavaScript

Если сайты требуют JavaScript:

```python
# Использовать selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_page_with_selenium(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return html
```

## Рекомендуемые сайты для начала

### 1. Winline.ru 🥇
- ✅ Менее строгая защита QRATOR
- ✅ Есть live-ссылки в HTML
- ✅ Хорошая SEO-оптимизация

### 2. Betboom.ru 🥈
- ✅ Доступен через HTTP
- ⚠️ Cloudflare защита
- ✅ Много live-контента

### 3. Baltbet.ru 🥉
- ✅ Менее защищен
- ⚠️ Меньше контента
- ✅ Простая структура

## Пошаговая миграция

### Этап 1: Тестирование доступности
```bash
python3 test_http_controller.py
```

### Этап 2: Настройка селекторов
1. Откройте сайт в браузере
2. Найдите элементы с матчами
3. Обновите селекторы в `http_controller.py`
4. Протестируйте парсинг

### Этап 3: Обработка защиты
1. Добавьте обработку Cloudflare/QRATOR
2. Настройте User-Agent
3. Добавьте задержки между запросами

### Этап 4: Переход на реальные данные
1. Замените `HTTPControllerDemo` на `HTTPController`
2. Обновите `main.py`
3. Протестируйте полную систему

## Примеры селекторов

### Betboom.ru
```python
selectors = {
    'match_container': '.sport-event-item, .event-card',
    'team_names': '.team-name, .participant-name',
    'score': '.score, .current-score',
    'minute': '.minute, .match-time',
    'coefficient': '.coefficient, .odds-value',
    'locked': '.locked, .disabled',
    'league': '.league-name, .tournament'
}
```

### Winline.ru
```python
selectors = {
    'match_container': '.event-item, .match-card',
    'team_names': '.team-name, .participant',
    'score': '.score, .result',
    'minute': '.minute, .time',
    'coefficient': '.coefficient, .odds',
    'locked': '.locked, .disabled',
    'league': '.league, .tournament'
}
```

## Мониторинг и отладка

### Логирование запросов
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Проверка ответов
```python
def debug_response(response):
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Content length: {len(response.text)}")
```

### Сохранение HTML для анализа
```python
with open(f'debug_{site}_{sport}.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
```

## Рекомендации

1. **Начните с Winline.ru** - наименее защищенный
2. **Используйте задержки** между запросами (1-2 секунды)
3. **Ротируйте User-Agent** для избежания блокировок
4. **Мониторьте логи** на предмет ошибок
5. **Тестируйте регулярно** - сайты могут изменить структуру

## Заключение

Система готова к работе с HTTP-запросами. Основная работа заключается в настройке правильных селекторов и обработке защиты сайтов. Демо-версия позволяет протестировать всю логику анализа без необходимости настройки реальных запросов.