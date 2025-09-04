# 🎮 Управление системой TrueLiveBet AI

## 🛑 **СИСТЕМА ОСТАНОВЛЕНА**

✅ Все процессы TrueLiveBet AI успешно остановлены  
✅ Нет активных анализаторов  
✅ Telegram бот не отправляет сообщения  
✅ OpenAI API запросы не выполняются  

## 🎮 **Команды управления системой**

### **Проверка статуса:**
```bash
python3 control_system.py status
```

### **Остановка системы:**
```bash
python3 control_system.py stop
```

### **Одиночный анализ (безопасно):**
```bash
python3 control_system.py single
```

### **Запуск в фоне (непрерывная работа):**
```bash
python3 control_system.py start
```

### **Перезапуск системы:**
```bash
python3 control_system.py restart
```

## 🔧 **Альтернативные способы управления**

### **Прямые команды:**
```bash
# Одиночный анализ
python3 start_improved.py single

# Непрерывная работа (ВНИМАНИЕ: будет работать постоянно!)
python3 start_improved.py continuous

# Остановка (если запущено в терминале)
Ctrl + C
```

### **Системные команды:**
```bash
# Поиск процессов
ps aux | grep python | grep -E "(start_improved|enhanced_live)"

# Принудительная остановка (если нужно)
pkill -f "start_improved\|enhanced_live"

# Проверка портов (если используются)
netstat -tulpn | grep python
```

## 📋 **Мониторинг системы**

### **Просмотр логов в реальном времени:**
```bash
# Основные логи
tail -f improved_production.log

# Поиск ошибок
grep -E "ERROR|❌|Exception" improved_production.log

# Поиск рекомендаций
grep -E "рекомендаций|РЕКОМЕНДАЦИИ|✅.*матч" improved_production.log
```

### **Проверка отчетов:**
```bash
# Последние отчеты
ls -la *report*$(date +%Y%m%d)* | tail -5

# Просмотр последнего отчета
cat $(ls -t ai_telegram_report_*.html | head -1)
```

### **Системные ресурсы:**
```bash
# Использование ресурсов
python3 diagnose.py

# Память и CPU
htop

# Место на диске
df -h
```

## ⚠️ **Важные замечания**

### **Перед запуском убедитесь:**
- ✅ OpenAI API ключ настроен: `echo $OPENAI_API_KEY`
- ✅ Зависимости установлены: `python3 diagnose.py`
- ✅ Telegram бот работает: `python3 test_telegram.py`
- ✅ Достаточно места на диске: `df -h`

### **Стоимость работы:**
- **Одиночный анализ:** ~$0.20
- **Непрерывная работа:** ~$10/день (~$300/месяц)
- **Рекомендация:** Используйте одиночный анализ для тестов

### **Безопасность:**
- Система автоматически останавливается при критических ошибках
- Максимальное время работы одного анализа: 5 минут
- Автоматический перезапуск при сбоях (до 5 попыток)

## 🚀 **Быстрые команды**

### **Для ежедневного использования:**
```bash
# Утренняя проверка
python3 control_system.py status

# Тестовый анализ
python3 control_system.py single

# Запуск на день
python3 control_system.py start

# Вечерняя остановка
python3 control_system.py stop
```

### **Для отладки:**
```bash
# Диагностика проблем
python3 diagnose.py --test

# Тест OpenAI
python3 test_new_football_rules.py

# Проверка Telegram
python3 test_telegram.py
```

---

## 📞 **Техподдержка**

### **Если система не запускается:**
1. Проверьте API ключи: `python3 diagnose.py`
2. Проверьте зависимости: `pip3 install -r requirements.txt`
3. Проверьте логи: `tail -20 improved_production.log`

### **Если система зависла:**
1. Остановите: `python3 control_system.py stop`
2. Проверьте ресурсы: `htop`
3. Перезапустите: `python3 control_system.py restart`

### **Если нет рекомендаций:**
1. Проверьте источники: `curl -I https://betzona.ru/live-futbol.html`
2. Проверьте OpenAI: `python3 test_new_football_rules.py`
3. Посмотрите логи: `grep "подходящих матчей" improved_production.log`

---

## 🎯 **Текущий статус: СИСТЕМА ОСТАНОВЛЕНА И ГОТОВА К УПРАВЛЕНИЮ**

Используйте команды выше для безопасного управления TrueLiveBet AI! 🛡️