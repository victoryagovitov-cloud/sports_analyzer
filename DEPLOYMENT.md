# Инструкции по развертыванию системы анализа live-ставок

## Обзор системы

Система автоматически анализирует live-ставки с сайтов Betboom и Scores24, используя Browser MCP для получения данных. Анализ выполняется циклически каждые 50 минут.

## Структура проекта

```
live-betting-analyzer/
├── main.py                          # Основной модуль
├── config.py                        # Конфигурация
├── browser_controller.py            # Управление браузером
├── fuzzy_matcher.py                # Fuzzy matching
├── report_generator.py             # Генерация отчетов
├── analyzers/                      # Анализаторы по видам спорта
│   ├── __init__.py
│   ├── football_analyzer.py
│   ├── tennis_analyzer.py
│   ├── table_tennis_analyzer.py
│   └── handball_analyzer.py
├── reports/                        # Папка с отчетами
├── requirements.txt                # Зависимости
├── .env.example                   # Пример конфигурации
├── test_analyzer.py               # Тесты
├── run_example.py                 # Примеры запуска
├── browser_mcp_integration.py     # Интеграция с Browser MCP
└── README.md                      # Документация
```

## Установка

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd live-betting-analyzer
```

### 2. Установка зависимостей
```bash
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка пакетов
pip install -r requirements.txt
```

### 3. Настройка конфигурации
```bash
# Копирование файла конфигурации
cp .env.example .env

# Редактирование настроек
nano .env
```

### 4. Настройка Browser MCP
1. Установите Browser MCP расширение
2. Обновите методы в `browser_controller.py` для работы с реальным Browser MCP
3. Настройте селекторы в `config.py` под реальную структуру сайтов

## Запуск

### Единичный анализ (для тестирования)
```bash
python run_example.py single
```

### Непрерывный анализ
```bash
python run_example.py continuous
```

### Запуск в фоне (Linux/Mac)
```bash
nohup python run_example.py continuous > live_betting.log 2>&1 &
```

### Запуск как сервис (systemd)
Создайте файл `/etc/systemd/system/live-betting.service`:

```ini
[Unit]
Description=Live Betting Analyzer
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/live-betting-analyzer
ExecStart=/path/to/live-betting-analyzer/venv/bin/python run_example.py continuous
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Затем:
```bash
sudo systemctl daemon-reload
sudo systemctl enable live-betting
sudo systemctl start live-betting
```

## Мониторинг

### Просмотр логов
```bash
# Логи системы
tail -f live_betting_analysis.log

# Логи сервиса (если запущен как сервис)
sudo journalctl -u live-betting -f
```

### Проверка статуса
```bash
# Статус сервиса
sudo systemctl status live-betting

# Процессы Python
ps aux | grep python
```

## Настройка

### Основные параметры (config.py)

```python
ANALYSIS_SETTINGS = {
    'cycle_interval_minutes': 50,           # Интервал анализа
    'fuzzy_match_threshold': 70,            # Минимальный процент совпадения
    'favorite_probability_threshold': 80,   # Минимальная вероятность фаворита
    'handball_goal_difference': 5,          # Минимальная разница в голаx
    'handball_analysis_minute_start': 10,   # Начало анализа тоталов
    'handball_analysis_minute_end': 45,     # Конец анализа тоталов
    'handball_total_margin': 4              # Отступ для тоталов
}
```

### URL-адреса сайтов

```python
BETBOOM_URLS = {
    'football': 'https://betboom.ru/sport/football?type=live',
    'tennis': 'https://betboom.ru/sport/tennis?type=live',
    'table_tennis': 'https://betboom.ru/sport/table-tennis?type=live',
    'handball': 'https://betboom.ru/sport/handball?type=live'
}

SCORES24_URLS = {
    'football': 'https://scores24.live/ru/soccer?matchesFilter=live',
    'tennis': 'https://scores24.live/ru/tennis?matchesFilter=live',
    'table_tennis': 'https://scores24.live/ru/table-tennis?matchesFilter=live',
    'handball': 'https://scores24.live/ru/handball'
}
```

## Интеграция с Browser MCP

### 1. Установка Browser MCP
Следуйте инструкциям по установке Browser MCP расширения.

### 2. Обновление browser_controller.py
Замените заглушки на реальные вызовы Browser MCP:

```python
def navigate_to_page(self, url: str) -> bool:
    try:
        # Реальный вызов Browser MCP
        result = browser_mcp.navigate(url)
        return result.get('success', False)
    except Exception as e:
        print(f"Ошибка навигации: {e}")
        return False
```

### 3. Настройка селекторов
Обновите селекторы в `config.py` под реальную структуру сайтов:

```python
BETBOOM_SELECTORS = {
    'match_container': '.actual-selector-for-match',
    'team_names': '.actual-selector-for-teams',
    'score': '.actual-selector-for-score',
    'minute': '.actual-selector-for-minute',
    'coefficient': '.actual-selector-for-coefficient',
    'locked': '.actual-selector-for-locked'
}
```

## Тестирование

### Запуск тестов
```bash
python test_analyzer.py
```

### Проверка работы анализаторов
```bash
python -c "
from main import LiveBettingAnalyzer
analyzer = LiveBettingAnalyzer()
analyzer.run_single_analysis()
"
```

## Отчеты

### Просмотр отчетов
Отчеты сохраняются в папке `reports/` в формате HTML:
- `live_betting_report_YYYYMMDD_HHMMSS.html`

### Структура отчета
```html
🎯 LIVE-ПРЕДЛОЖЕНИЯ НА (время) 🎯

⚽ ФУТБОЛ ⚽
[рекомендации по футболу]

🎾 ТЕННИС 🎾
[рекомендации по теннису]

🏓 НАСТ. ТЕННИС 🏓
[рекомендации по настольному теннису]

🤾 ГАНДБОЛ 🤾
[рекомендации по гандболу]

💎 TrueLiveBet – Мы всегда на Вашей стороне! 💎
```

## Устранение неполадок

### Частые проблемы

1. **Ошибка импорта модулей**
   ```bash
   # Убедитесь, что находитесь в корневой папке проекта
   cd /path/to/live-betting-analyzer
   python run_example.py single
   ```

2. **Ошибка Browser MCP**
   - Проверьте установку Browser MCP
   - Обновите методы в `browser_controller.py`
   - Проверьте селекторы в `config.py`

3. **Ошибка fuzzy matching**
   ```bash
   # Установите python-Levenshtein для ускорения
   pip install python-Levenshtein
   ```

4. **Ошибка доступа к файлам**
   ```bash
   # Проверьте права доступа
   chmod +x run_example.py
   chmod -R 755 reports/
   ```

### Логирование

Все ошибки записываются в `live_betting_analysis.log`. Для отладки:

```bash
# Просмотр последних ошибок
tail -n 100 live_betting_analysis.log | grep ERROR

# Мониторинг в реальном времени
tail -f live_betting_analysis.log
```

## Производительность

### Рекомендации по серверу
- **CPU**: 2+ ядра
- **RAM**: 2+ GB
- **Диск**: 10+ GB свободного места
- **Сеть**: Стабильное подключение к интернету

### Оптимизация
- Используйте `python-Levenshtein` для ускорения fuzzy matching
- Настройте таймауты в Browser MCP
- Очищайте старые отчеты периодически

## Безопасность

### Рекомендации
- Запускайте под отдельным пользователем
- Ограничьте права доступа к файлам
- Используйте виртуальное окружение
- Регулярно обновляйте зависимости

### Мониторинг
- Следите за использованием ресурсов
- Проверяйте логи на подозрительную активность
- Настройте алерты при критических ошибках

## Поддержка

При возникновении проблем:
1. Проверьте логи
2. Запустите тесты
3. Проверьте конфигурацию
4. Обратитесь к документации Browser MCP