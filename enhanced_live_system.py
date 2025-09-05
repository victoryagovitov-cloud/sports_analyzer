#!/usr/bin/env python3
"""
Улучшенная система live-анализа ставок с мульти-источниковым контроллером
"""

import logging
import schedule
import time
from datetime import datetime
from typing import List
from multi_source_controller import MultiSourceController, MatchData
from scores24_only_controller import scores24_only_controller
from enhanced_analyzers import (
    EnhancedFootballAnalyzer,
    EnhancedTennisAnalyzer,
    EnhancedTableTennisAnalyzer,
    EnhancedHandballAnalyzer
)
from simple_report_generator import SimpleReportGenerator
from ai_analyzer import AIAnalyzer
from claude_final_integration import ClaudeFinalIntegration
from ai_telegram_generator import AITelegramGenerator
from telegram_integration import TelegramIntegration
from system_watchdog import system_watchdog
from enhanced_telegram_formatter import enhanced_formatter
from prompt_telegram_formatter import prompt_telegram_formatter
from totals_calculator import totals_calculator
from moscow_time import filter_live_matches_by_time, log_moscow_time, format_moscow_time_for_filename

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedLiveSystem:
    def __init__(self):
        self.controller = MultiSourceController()
        self.analyzers = {
            'football': EnhancedFootballAnalyzer(),
            'tennis': EnhancedTennisAnalyzer(),
            'table_tennis': EnhancedTableTennisAnalyzer(),
            'handball': EnhancedHandballAnalyzer()
        }
        self.report_generator = SimpleReportGenerator()
        self.ai_analyzer = AIAnalyzer()
        self.claude_analyzer = ClaudeFinalIntegration()
        self.ai_telegram_generator = AITelegramGenerator()
        self.telegram_integration = TelegramIntegration()
        
    def analyze_sport(self, sport_type: str) -> List[MatchData]:
        """AI-анализ матчей для конкретного вида спорта"""
        logger.info(f"Начинаем AI-анализ {sport_type}...")
        
        # Получаем live-матчи ТОЛЬКО с scores24.live (по промпту)
        matches = scores24_only_controller.get_live_matches(sport_type)
        logger.info(f"Найдено {len(matches)} live-матчей для {sport_type}")
        
        # Фильтруем завершившиеся матчи
        active_matches = filter_live_matches_by_time(matches, sport_type)
        
        if len(active_matches) < len(matches):
            logger.info(f"📊 Исключено {len(matches) - len(active_matches)} завершившихся матчей для {sport_type}")
        
        if not active_matches:
            logger.info(f"Нет активных live-матчей для {sport_type}")
            return []
        
        # AI-анализ всех матчей
        try:
            ai_recommendations = self.claude_analyzer.analyze_matches_with_claude(active_matches, sport_type)
            logger.info(f"AI сгенерировал {len(ai_recommendations)} рекомендаций для {sport_type}")
            return ai_recommendations
        except Exception as e:
            logger.error(f"Ошибка AI-анализа для {sport_type}: {e}")
            return []
    
    def _analyze_handball_totals(self, handball_matches: List[MatchData]) -> List[MatchData]:
        """Анализирует тоталы для гандбольных матчей"""
        totals_recommendations = []
        
        for match in handball_matches:
            try:
                # Рассчитываем тоталы по новой формуле
                totals_data = totals_calculator.calculate_handball_totals(match)
                
                if totals_data:
                    # Создаем рекомендацию по тоталам
                    totals_rec = totals_calculator.create_totals_recommendation(match, totals_data)
                    if totals_rec:
                        totals_recommendations.append(totals_rec)
                        
            except Exception as e:
                logger.error(f"Ошибка анализа тоталов для {match.team1} vs {match.team2}: {e}")
        
        if totals_recommendations:
            logger.info(f"📊 Найдено {len(totals_recommendations)} рекомендаций по тоталам")
        
        return totals_recommendations
    
    def run_analysis_cycle(self):
        """Запуск одного цикла анализа"""
        logger.info("=" * 60)
        logger.info("ЗАПУСК ЦИКЛА АНАЛИЗА LIVE-СТАВОК")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        all_recommendations = []
        
        # Обновляем heartbeat
        system_watchdog.heartbeat()
        
        # Анализируем каждый вид спорта
        sports = ['football', 'tennis', 'table_tennis', 'handball']
        
        for sport in sports:
            try:
                recommendations = self.analyze_sport(sport)
                all_recommendations.extend(recommendations)
                
                # Добавляем анализ тоталов для гандбола
                if sport == 'handball' and recommendations:
                    totals_recommendations = self._analyze_handball_totals(recommendations)
                    all_recommendations.extend(totals_recommendations)
                
                system_watchdog.heartbeat()  # Обновляем heartbeat после каждого спорта
            except Exception as e:
                logger.error(f"Ошибка при анализе {sport}: {e}")
        
        # Генерируем AI-отчет
        if all_recommendations:
            logger.info(f"Генерируем AI-отчет для {len(all_recommendations)} рекомендаций...")
            
            # Генерируем обычный HTML отчет
            html_report = self.report_generator.generate_report(all_recommendations)
            
            # Генерируем отчет СТРОГО по шаблону промпта (с московским временем и фильтрацией)
            ai_telegram_report = prompt_telegram_formatter.format_report_by_prompt(all_recommendations)
            
            # Сохраняем отчеты в файлы
            timestamp = format_moscow_time_for_filename()
            
            # HTML отчет
            html_filename = f"live_analysis_report_{timestamp}.html"
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html_report)
            
            # AI Telegram отчет
            telegram_filename = f"ai_telegram_report_{timestamp}.html"
            with open(telegram_filename, 'w', encoding='utf-8') as f:
                f.write(ai_telegram_report)
            
            logger.info(f"HTML отчет сохранен в файл: {html_filename}")
            logger.info(f"AI Telegram отчет сохранен в файл: {telegram_filename}")
            
            # Отправляем в Telegram канал
            logger.info("Отправка AI-рекомендаций в Telegram канал...")
            # Используем форматтер СТРОГО по промпту
            prompt_telegram_report = prompt_telegram_formatter.format_report_by_prompt(all_recommendations)
            telegram_success = self.telegram_integration.send_formatted_report(prompt_telegram_report)
            
            if telegram_success:
                logger.info("✅ AI-рекомендации успешно отправлены в Telegram канал")
            else:
                logger.error("❌ Не удалось отправить рекомендации в Telegram канал")
            
            # Выводим краткую статистику
            self.print_summary(all_recommendations)
        else:
            logger.info("Нет рекомендаций для отчета")
            # Отправляем сообщение об отсутствии рекомендаций в Telegram
            self.telegram_integration.send_no_recommendations_message()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Цикл анализа завершен за {duration:.2f} секунд")
        logger.info("=" * 60)
    
    def print_summary(self, recommendations: List[MatchData]):
        """Вывод краткой статистики"""
        logger.info("КРАТКАЯ СТАТИСТИКА:")
        
        # Группируем по видам спорта
        by_sport = {}
        for rec in recommendations:
            sport = getattr(rec, 'sport_type', getattr(rec, 'sport', 'unknown'))
            if sport not in by_sport:
                by_sport[sport] = []
            by_sport[sport].append(rec)
        
        for sport, recs in by_sport.items():
            logger.info(f"{sport.upper()}: {len(recs)} рекомендаций")
            
            # Показываем первые 3 рекомендации
            for i, rec in enumerate(recs[:3]):
                logger.info(f"  {i+1}. {rec.team1} - {rec.team2} ({rec.score})")
                if rec.recommendation_type:
                    logger.info(f"     Рекомендация: {rec.recommendation_value}")
        
        # Статистика по источникам
        sources = {}
        for rec in recommendations:
            source = getattr(rec, 'source', 'unknown')
            if source not in sources:
                sources[source] = 0
            sources[source] += 1
        
        logger.info("Источники данных:")
        for source, count in sources.items():
            logger.info(f"  {source.upper()}: {count} матчей")
    
    def run_continuous(self):
        """Запуск непрерывного анализа"""
        logger.info("Запуск непрерывного анализа live-ставок...")
        logger.info("Анализ будет выполняться каждые 50 минут")
        
        # Запуск системного watchdog
        system_watchdog.start()
        
        # Отправляем сообщение о запуске в Telegram
        logger.info("Отправка сообщения о запуске в Telegram канал...")
        self.telegram_integration.send_startup_message()
        
        # Планируем выполнение каждые 45 минут (по новому промпту)
        schedule.every(45).minutes.do(self.run_analysis_cycle)
        
        # Запускаем первый анализ сразу
        self.run_analysis_cycle()
        
        # Запускаем планировщик с обработкой ошибок
        while True:
            try:
                schedule.run_pending()
            except Exception as e:
                logger.error(f"Ошибка в планировщике: {e}")
                logger.exception("Детали ошибки планировщика:")
                # Продолжаем работу, не останавливаемся из-за одной ошибки
            time.sleep(60)  # Проверяем каждую минуту
    
    def run_single(self):
        """Запуск одного анализа"""
        logger.info("Запуск единичного анализа live-ставок...")
        self.run_analysis_cycle()

def main():
    """Главная функция"""
    import sys
    
    system = EnhancedLiveSystem()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        system.run_continuous()
    else:
        system.run_single()

if __name__ == "__main__":
    main()