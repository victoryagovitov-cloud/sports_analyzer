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
from enhanced_analyzers import (
    EnhancedFootballAnalyzer,
    EnhancedTennisAnalyzer,
    EnhancedTableTennisAnalyzer,
    EnhancedHandballAnalyzer
)
from simple_report_generator import SimpleReportGenerator

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
        
    def analyze_sport(self, sport_type: str) -> List[MatchData]:
        """Анализ матчей для конкретного вида спорта"""
        logger.info(f"Начинаем анализ {sport_type}...")
        
        # Получаем live-матчи
        matches = self.controller.get_live_matches(sport_type)
        logger.info(f"Найдено {len(matches)} live-матчей для {sport_type}")
        
        if not matches:
            logger.info(f"Нет live-матчей для {sport_type}")
            return []
        
        # Анализируем матчи
        analyzer = self.analyzers.get(sport_type)
        if not analyzer:
            logger.error(f"Анализатор для {sport_type} не найден")
            return []
        
        recommendations = []
        for match in matches:
            try:
                # Анализируем матч
                recommendation = analyzer.analyze_match(match)
                if recommendation:
                    recommendations.append(recommendation)
            except Exception as e:
                logger.error(f"Ошибка при анализе матча {match.team1} - {match.team2}: {e}")
        
        logger.info(f"Получено {len(recommendations)} рекомендаций для {sport_type}")
        return recommendations
    
    def run_analysis_cycle(self):
        """Запуск одного цикла анализа"""
        logger.info("=" * 60)
        logger.info("ЗАПУСК ЦИКЛА АНАЛИЗА LIVE-СТАВОК")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        all_recommendations = []
        
        # Анализируем каждый вид спорта
        sports = ['football', 'tennis', 'table_tennis', 'handball']
        
        for sport in sports:
            try:
                recommendations = self.analyze_sport(sport)
                all_recommendations.extend(recommendations)
            except Exception as e:
                logger.error(f"Ошибка при анализе {sport}: {e}")
        
        # Генерируем отчет
        if all_recommendations:
            logger.info(f"Генерируем отчет для {len(all_recommendations)} рекомендаций...")
            report = self.report_generator.generate_report(all_recommendations)
            
            # Сохраняем отчет в файл
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"live_analysis_report_{timestamp}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"Отчет сохранен в файл: {filename}")
            
            # Выводим краткую статистику
            self.print_summary(all_recommendations)
        else:
            logger.info("Нет рекомендаций для отчета")
        
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
            sport = rec.sport_type
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
        
        # Планируем выполнение каждые 50 минут
        schedule.every(50).minutes.do(self.run_analysis_cycle)
        
        # Запускаем первый анализ сразу
        self.run_analysis_cycle()
        
        # Запускаем планировщик
        while True:
            schedule.run_pending()
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