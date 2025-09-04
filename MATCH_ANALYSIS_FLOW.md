# 🔍 Как происходит поиск и анализ матчей в TrueLiveBet AI

## 📋 Общая схема процесса

```
🚀 Запуск системы
    ↓
🔄 Цикл анализа (каждые 50 минут)
    ↓
🏆 Анализ 4 видов спорта: футбол → теннис → настольный теннис → гандбол
    ↓
📊 Для каждого вида спорта:
    1. 🌐 Сбор данных из источников
    2. 🤖 AI-анализ матчей  
    3. 📈 Генерация рекомендаций
    ↓
📱 Отправка в Telegram канал
```

## 🌐 Этап 1: Сбор данных из источников

### **MultiSourceController** - координирует сбор данных

```python
# Источники данных (в порядке приоритета):
sources = ['betzona', 'scores24']
```

#### **1.1 Betzona.ru** - основной источник
```python
urls = {
    'football': 'https://betzona.ru/live-futbol.html',
    'tennis': 'https://betzona.ru/live-tennis.html', 
    'table_tennis': 'https://betzona.ru/live-tennis.html',  # фильтруется
    'handball': 'https://betzona.ru/live-gandball.html'
}
```

**Что парсится с Betzona:**
- ✅ Названия команд/игроков
- ✅ Текущий счет  
- ✅ Минута матча
- ✅ Лига/турнир
- ✅ Статус (live/не live)
- ✅ Коэффициенты (если доступны)

**Алгоритм парсинга Betzona:**
```python
def _parse_match_data(self, match_element, sport_type):
    # 1. Проверяем, что матч live
    if match_element.get('data-is-live') != '1':
        return None
        
    # 2. Извлекаем команды
    teams = match_element.find_all('div', class_='match-scores-item__team')
    team1 = teams[0].get_text(strip=True)
    team2 = teams[1].get_text(strip=True)
    
    # 3. Извлекаем счет
    home_score = score_element.find('div', class_='match-scores-item__scores_home')
    away_score = score_element.find('div', class_='match-scores-item__scores_away') 
    score = f"{home_score.text}:{away_score.text}"
    
    # 4. Извлекаем минуту
    minute_element = match_element.find('div', class_='match-scores-item__status')
    minute = re.search(r'(\d+)', minute_text).group(1)
    
    # 5. Извлекаем лигу
    league = tournament_element.find('div', class_='match-scores-tournament__header_title')
```

#### **1.2 Scores24.live** - дополнительный источник
```python
urls = {
    'football': 'https://scores24.live/ru/soccer?matchesFilter=live',
    'tennis': 'https://scores24.live/ru/tennis?matchesFilter=live',
    'table_tennis': 'https://scores24.live/ru/table-tennis?matchesFilter=live',
    'handball': 'https://scores24.live/ru/handball?matchesFilter=live'
}
```

**Что парсится с Scores24:**
- ✅ Дополнительная статистика
- ✅ Рейтинги игроков/команд
- ✅ Форма команд (последние матчи)
- ✅ Позиции в таблице

### **1.3 Объединение данных**
```python
def get_live_matches(self, sport_type: str):
    all_matches = []
    
    # Получаем данные из Betzona
    betzona_matches = self.betzona_controller.get_live_matches(sport_type)
    all_matches.extend(betzona_matches)
    
    # Получаем данные из Scores24
    scores24_matches = self.scores24_controller.get_live_matches(sport_type)
    all_matches.extend(scores24_matches)
    
    # Удаляем дубликаты по командам и счету
    unique_matches = self._remove_duplicates(all_matches)
    
    return unique_matches
```

## 🤖 Этап 2: AI-анализ матчей

### **ClaudeFinalIntegration** - анализирует матчи

#### **2.1 Создание промпта для AI**
```python
def _create_detailed_analysis_prompt(self, matches, sport_type):
    # Строгие правила для каждого вида спорта
    rules = {
        'football': """
        СТРОГИЕ ПРАВИЛА ДЛЯ ФУТБОЛА:
        1. Найди ТОЛЬКО матчи, где одна команда ведет ≥2 голов
        2. Время матча должно быть ≥60 минут
        3. Вероятность победы фаворита >85%
        """,
        
        'tennis': """
        СТРОГИЕ ПРАВИЛА ДЛЯ ТЕННИСА:
        1. Найди ТОЛЬКО матчи, где игрок ведет по сетам ≥1
        2. Рейтинг ведущего игрока выше на ≥20 позиций
        3. Вероятность победы >80%
        """,
        
        'handball': """
        СТРОГИЕ ПРАВИЛА ДЛЯ ГАНДБОЛА:
        1. Найди ТОЛЬКО матчи, где команда ведет ≥5 голов
        2. Разница в позициях таблицы ≥3
        3. Вероятность победы >80%
        """
    }
```

#### **2.2 Анализ по видам спорта**

**⚽ Футбол:**
- Минимальное преимущество: 2 гола
- Минимальное время: 60 минута
- Анализ: позиции в таблице, форма, качество лиги
- Рекомендации: П1/П2 (победа команды)

**🎾 Теннис:**
- Минимальное преимущество: 1 сет
- Анализ: рейтинг ATP/WTA, форма, турнир
- Рекомендации: победа игрока

**🏓 Настольный теннис:**
- Аналогично теннису
- Анализ: рейтинг ITTF, форма
- Рекомендации: победа игрока

**🤾 Гандбол:**
- Минимальное преимущество: 5 голов
- Анализ: позиции в таблице, средняя результативность
- Рекомендации: П1/П2, тоталы (ТБ/ТМ)

#### **2.3 Эвристический анализ (fallback)**
```python
def _fallback_heuristic_analysis(self, prompt):
    # Если Claude API недоступен, используется упрощенный анализ
    # Проверяет только базовые критерии:
    # - Разрыв в счете
    # - Время матча
    # - Простая оценка вероятности
    return "[]"  # Пока возвращает пустой результат
```

## 📈 Этап 3: Генерация рекомендаций

### **3.1 Формат рекомендации**
```python
recommendation = {
    "team1": "Манчестер Сити",
    "team2": "Арсенал", 
    "score": "2:0",
    "minute": "67",
    "recommendation": "П1",  # Победа команды 1
    "confidence": 0.87,      # Уверенность 87%
    "reasoning": "Детальное обоснование с анализом..."
}
```

### **3.2 Критерии качественной рекомендации**
- ✅ Высокая уверенность (>80%)
- ✅ Детальное обоснование
- ✅ Учет множества факторов
- ✅ Соответствие строгим правилам

## 📊 Этап 4: Статистика анализа

### **Пример реального анализа:**
```
📊 СТАТИСТИКА ПОСЛЕДНЕГО АНАЛИЗА:
- Футбол: 23 live-матча → 0 рекомендаций
- Теннис: 105 live-матчей → 0 рекомендаций  
- Настольный теннис: 19 live-матчей → 0 рекомендаций
- Гандбол: 0 live-матчей → 0 рекомендаций

⏱️ Время анализа: 7.6 секунд
🔍 Всего проанализировано: 147 матчей
```

### **Почему мало рекомендаций?**
- 🎯 **Строгие критерии** - только высококачественные ставки
- 📈 **Высокий порог уверенности** - минимум 80-85%
- 🔍 **Детальная проверка** - множество факторов
- 🛡️ **Защита от рисков** - лучше пропустить, чем ошибиться

## 🚀 Этап 5: Отправка результатов

### **5.1 Генерация отчетов**
- **HTML отчет** - детальный анализ для архива
- **AI Telegram отчет** - краткий формат для канала
- **Логи** - полная информация о процессе

### **5.2 Отправка в Telegram**
```python
if all_recommendations:
    # Отправляем рекомендации в канал @truelivebet
    telegram_report = self.ai_telegram_generator.generate_report(recommendations)
    self.telegram_integration.send_report(telegram_report)
else:
    # Отправляем сообщение об отсутствии рекомендаций
    self.telegram_integration.send_no_recommendations_message()
```

## 🔧 Настройки анализа

### **Таймауты и ограничения:**
```python
ANALYSIS_SETTINGS = {
    'http_timeout_seconds': 30,        # Таймаут HTTP-запросов
    'analysis_timeout_seconds': 300,   # Максимальное время анализа
    'max_matches_per_sport': 100,      # Лимит матчей на спорт
    'min_confidence_threshold': 80,    # Минимальная уверенность
    'cycle_interval_minutes': 50       # Интервал между анализами
}
```

### **Мониторинг процесса:**
- 🔍 Watchdog проверяет состояние каждые 60 сек
- 📊 Логирование всех этапов
- ⚠️ Предупреждения при проблемах
- 🔄 Автоматический перезапуск при сбоях

---

## 🎯 Резюме процесса

1. **Сбор данных** - парсинг live-матчей с 2 источников
2. **Фильтрация** - только live-матчи, удаление дубликатов  
3. **AI-анализ** - строгие критерии качества
4. **Генерация рекомендаций** - только высокоуверенные ставки
5. **Отправка в Telegram** - автоматическая публикация

**Результат:** Высококачественные рекомендации с детальным обоснованием каждые 50 минут в канале @truelivebet!