"""
Основной модуль для анализа live-ставок
"""

import time
import schedule
import logging
from datetime import datetime
from typing import List

from http_controller_demo import HTTPControllerDemo
from fuzzy_matcher import FuzzyMatcher
from report_generator import ReportGenerator
from analyzers.football_analyzer import FootballAnalyzer
from analyzers.tennis_analyzer import TennisAnalyzer
from analyzers.table_tennis_analyzer import TableTennisAnalyzer
from analyzers.handball_analyzer import HandballAnalyzer
from config import ANALYSIS_SETTINGS


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_betting_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LiveBettingAnalyzer:
    """Основной класс для анализа live-ставок"""
    
    def __init__(self):
        self.browser = HTTPControllerDemo()
        self.fuzzy_matcher = FuzzyMatcher(threshold=ANALYSIS_SETTINGS['fuzzy_match_threshold'])
        self.report_generator = ReportGenerator()
        
        # Инициализация анализаторов
        self.football_analyzer = FootballAnalyzer(self.browser, self.fuzzy_matcher)
        self.tennis_analyzer = TennisAnalyzer(self.browser, self.fuzzy_matcher)
        self.table_tennis_analyzer = TableTennisAnalyzer(self.browser, self.fuzzy_matcher)
        self.handball_analyzer = HandballAnalyzer(self.browser, self.fuzzy_matcher)
        
        self.cycle_interval = ANALYSIS_SETTINGS['cycle_interval_minutes']
        self.is_running = False
    
    def run_analysis_cycle(self):
        """Выполнение одного цикла анализа"""
        logger.info("=" * 50)
        logger.info("НАЧАЛО ЦИКЛА АНАЛИЗА")
        logger.info(f"Время: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}")
        logger.info("=" * 50)
        
        try:
            # Очищаем предыдущие рекомендации
            self.report_generator.clear_recommendations()
            
            # Анализ футбола
            logger.info("Анализ футбольных матчей...")
            football_recommendations = self.football_analyzer.analyze_football_matches()
            self.report_generator.add_football_recommendations(football_recommendations)
            logger.info(f"Найдено {len(football_recommendations)} футбольных рекомендаций")
            
            # Анализ тенниса
            logger.info("Анализ теннисных матчей...")
            tennis_recommendations = self.tennis_analyzer.analyze_tennis_matches()
            self.report_generator.add_tennis_recommendations(tennis_recommendations)
            logger.info(f"Найдено {len(tennis_recommendations)} теннисных рекомендаций")
            
            # Анализ настольного тенниса
            logger.info("Анализ матчей настольного тенниса...")
            table_tennis_recommendations = self.table_tennis_analyzer.analyze_table_tennis_matches()
            self.report_generator.add_table_tennis_recommendations(table_tennis_recommendations)
            logger.info(f"Найдено {len(table_tennis_recommendations)} рекомендаций по настольному теннису")
            
            # Анализ гандбола
            logger.info("Анализ гандбольных матчей...")
            handball_recommendations = self.handball_analyzer.analyze_handball_matches()
            self.report_generator.add_handball_recommendations(handball_recommendations)
            logger.info(f"Найдено {len(handball_recommendations)} гандбольных рекомендаций")
            
            # Генерация отчета
            logger.info("Генерация отчета...")
            report = self.report_generator.generate_telegram_report()
            
            # Вывод статистики
            counts = self.report_generator.get_recommendations_count()
            total_count = self.report_generator.get_total_recommendations_count()
            
            logger.info("СТАТИСТИКА АНАЛИЗА:")
            logger.info(f"  Футбол: {counts['football']} рекомендаций")
            logger.info(f"  Теннис: {counts['tennis']} рекомендаций")
            logger.info(f"  Настольный теннис: {counts['table_tennis']} рекомендаций")
            logger.info(f"  Гандбол: {counts['handball']} рекомендаций")
            logger.info(f"  ВСЕГО: {total_count} рекомендаций")
            
            # Сохранение отчета в файл
            self._save_report_to_file(report)
            
            # Здесь можно добавить отправку в Telegram
            # self._send_to_telegram(report)
            
            logger.info("ЦИКЛ АНАЛИЗА ЗАВЕРШЕН")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"Ошибка в цикле анализа: {e}")
            logger.exception("Детали ошибки:")
    
    def _save_report_to_file(self, report: str):
        """
        Сохранение отчета в файл
        
        Args:
            report (str): HTML-отчет
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/live_betting_report_{timestamp}.html"
            
            # Создаем папку reports если её нет
            import os
            os.makedirs("reports", exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"Отчет сохранен в файл: {filename}")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения отчета: {e}")
    
    def _send_to_telegram(self, report: str):
        """
        Отправка отчета в Telegram (заглушка)
        
        Args:
            report (str): HTML-отчет
        """
        # Здесь будет реализация отправки в Telegram
        # Пока что просто логируем
        logger.info("Отправка в Telegram (не реализовано)")
        logger.info(f"Размер отчета: {len(report)} символов")
    
    def start_analysis(self):
        """Запуск циклического анализа"""
        logger.info("Запуск системы анализа live-ставок")
        logger.info(f"Интервал анализа: {self.cycle_interval} минут")
        
        # Планируем выполнение каждые N минут
        schedule.every(self.cycle_interval).minutes.do(self.run_analysis_cycle)
        
        # Выполняем первый анализ сразу
        self.run_analysis_cycle()
        
        self.is_running = True
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Получен сигнал остановки")
            self.stop_analysis()
    
    def stop_analysis(self):
        """Остановка анализа"""
        logger.info("Остановка системы анализа")
        self.is_running = False
        self.browser.close_browser()
        logger.info("Система остановлена")
    
    def run_single_analysis(self):
        """Выполнение одного анализа (для тестирования)"""
        logger.info("Выполнение единичного анализа")
        self.run_analysis_cycle()


def main():
    """Главная функция"""
    analyzer = LiveBettingAnalyzer()
    
    try:
        # Для тестирования можно запустить один анализ
        # analyzer.run_single_analysis()
        
        # Для продакшена - циклический анализ
        analyzer.start_analysis()
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        logger.exception("Детали ошибки:")
    finally:
        analyzer.stop_analysis()


if __name__ == "__main__":
    main()