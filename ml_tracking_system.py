#!/usr/bin/env python3
"""
Система ведения логов для машинного обучения
Отслеживает результаты прогнозов для улучшения алгоритмов
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from moscow_time import get_moscow_time, format_moscow_time_for_telegram

logger = logging.getLogger(__name__)

@dataclass
class PredictionResult:
    """Результат прогноза для ML"""
    timestamp: str
    sport_type: str
    team1: str
    team2: str
    score_at_prediction: str
    minute_at_prediction: str
    league: str
    recommendation: str
    confidence: float
    reasoning: str
    coefficient: str
    source: str
    
    # Результат (заполняется позже)
    actual_result: str = ""  # "win", "loss", "unknown"
    final_score: str = ""
    match_duration: str = ""
    notes: str = ""

class MLTrackingSystem:
    """Система отслеживания для машинного обучения"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ml_log_file = "ml_predictions_log.json"
        self.daily_stats_file = "daily_stats.json"
        
    def log_prediction(self, recommendation, sport_type: str):
        """Записывает прогноз в ML лог"""
        try:
            moscow_time = get_moscow_time()
            
            # Создаем запись прогноза
            prediction = PredictionResult(
                timestamp=moscow_time.isoformat(),
                sport_type=sport_type,
                team1=getattr(recommendation, 'team1', ''),
                team2=getattr(recommendation, 'team2', ''),
                score_at_prediction=getattr(recommendation, 'score', ''),
                minute_at_prediction=getattr(recommendation, 'minute', ''),
                league=getattr(recommendation, 'league', ''),
                recommendation=getattr(recommendation, 'recommendation_value', ''),
                confidence=getattr(recommendation, 'probability', 0) / 100,
                reasoning=getattr(recommendation, 'justification', ''),
                coefficient=self._extract_coefficient(recommendation),
                source=getattr(recommendation, 'source', '')
            )
            
            # Сохраняем в файл
            self._append_to_ml_log(prediction)
            
            self.logger.info(f"📊 ML лог: Записан прогноз {prediction.team1} vs {prediction.team2} - {prediction.recommendation}")
            
        except Exception as e:
            self.logger.error(f"Ошибка записи ML лога: {e}")
    
    def update_prediction_result(self, team1: str, team2: str, timestamp: str, result: str, final_score: str = "", notes: str = ""):
        """Обновляет результат прогноза"""
        try:
            # Загружаем существующие логи
            predictions = self._load_ml_log()
            
            # Ищем соответствующий прогноз
            for prediction in predictions:
                if (prediction['team1'] == team1 and 
                    prediction['team2'] == team2 and 
                    prediction['timestamp'].startswith(timestamp[:10])):  # По дате
                    
                    prediction['actual_result'] = result
                    prediction['final_score'] = final_score
                    prediction['notes'] = notes
                    
                    self.logger.info(f"📊 ML лог: Обновлен результат {team1} vs {team2} - {result}")
                    break
            
            # Сохраняем обновленные логи
            self._save_ml_log(predictions)
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления результата: {e}")
    
    def add_manual_result(self, team1: str, team2: str, recommendation: str, result: str, notes: str = ""):
        """Добавляет результат вручную (как сейчас от пользователя)"""
        try:
            moscow_time = get_moscow_time()
            
            # Создаем запись с результатом
            prediction = PredictionResult(
                timestamp=moscow_time.isoformat(),
                sport_type="manual_entry",
                team1=team1,
                team2=team2,
                score_at_prediction="",
                minute_at_prediction="",
                league="",
                recommendation=recommendation,
                confidence=0.0,
                reasoning="Ручной ввод результата",
                coefficient="",
                source="manual",
                actual_result=result,
                notes=notes
            )
            
            self._append_to_ml_log(prediction)
            self.logger.info(f"📊 ML лог: Добавлен ручной результат {team1} vs {team2} - {result}")
            
        except Exception as e:
            self.logger.error(f"Ошибка добавления ручного результата: {e}")
    
    def generate_daily_stats(self) -> Dict:
        """Генерирует статистику за день"""
        try:
            moscow_time = get_moscow_time()
            today_str = moscow_time.strftime("%Y-%m-%d")
            
            # Загружаем логи
            predictions = self._load_ml_log()
            
            # Фильтруем сегодняшние прогнозы
            today_predictions = [
                p for p in predictions 
                if p['timestamp'].startswith(today_str)
            ]
            
            if not today_predictions:
                return self._empty_daily_stats(today_str)
            
            # Считаем статистику
            stats = self._calculate_daily_statistics(today_predictions, today_str)
            
            # Сохраняем дневную статистику
            self._save_daily_stats(stats)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации дневной статистики: {e}")
            return {}
    
    def _calculate_daily_statistics(self, predictions: List[Dict], date: str) -> Dict:
        """Рассчитывает детальную статистику"""
        
        # Общие показатели
        total_predictions = len(predictions)
        with_results = [p for p in predictions if p['actual_result']]
        wins = [p for p in predictions if p['actual_result'] == 'win']
        losses = [p for p in predictions if p['actual_result'] == 'loss']
        
        # По видам спорта
        by_sport = {}
        for sport in ['football', 'tennis', 'table_tennis', 'handball', 'manual_entry']:
            sport_predictions = [p for p in predictions if p['sport_type'] == sport]
            sport_wins = [p for p in sport_predictions if p['actual_result'] == 'win']
            sport_losses = [p for p in sport_predictions if p['actual_result'] == 'loss']
            
            if sport_predictions:
                by_sport[sport] = {
                    'total': len(sport_predictions),
                    'wins': len(sport_wins),
                    'losses': len(sport_losses),
                    'win_rate': len(sport_wins) / len(sport_predictions) * 100 if sport_predictions else 0,
                    'predictions': sport_predictions
                }
        
        # По уровню уверенности
        high_confidence = [p for p in predictions if p['confidence'] >= 0.85]
        medium_confidence = [p for p in predictions if 0.75 <= p['confidence'] < 0.85]
        low_confidence = [p for p in predictions if p['confidence'] < 0.75]
        
        return {
            'date': date,
            'generated_at': get_moscow_time().isoformat(),
            'total_predictions': total_predictions,
            'predictions_with_results': len(with_results),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': len(wins) / len(with_results) * 100 if with_results else 0,
            'by_sport': by_sport,
            'by_confidence': {
                'high_confidence': {'count': len(high_confidence), 'threshold': '≥85%'},
                'medium_confidence': {'count': len(medium_confidence), 'threshold': '75-84%'},
                'low_confidence': {'count': len(low_confidence), 'threshold': '<75%'}
            },
            'predictions': predictions
        }
    
    def format_daily_stats_for_telegram(self, stats: Dict) -> str:
        """Форматирует дневную статистику для Telegram"""
        if not stats or not stats.get('predictions'):
            return self._format_no_stats_message()
        
        moscow_time = get_moscow_time()
        time_str = moscow_time.strftime("%H:%M МСК, %d.%m.%Y")
        
        total = stats['total_predictions']
        with_results = stats['predictions_with_results']
        wins = stats['wins']
        losses = stats['losses']
        win_rate = stats['win_rate']
        
        report = f"""📊 <b>ДНЕВНАЯ СТАТИСТИКА</b> (<i>{time_str}</i>) 📊
<b>═══════════════════════════</b>

📈 <b>ОБЩИЕ ПОКАЗАТЕЛИ:</b>
🎯 Прогнозов сделано: <b>{total}</b>
✅ Результаты известны: <b>{with_results}</b>
🏆 Выигрышных: <b>{wins}</b>
❌ Проигрышных: <b>{losses}</b>
📊 Винрейт: <b>{win_rate:.1f}%</b>

"""
        
        # Статистика по видам спорта
        by_sport = stats.get('by_sport', {})
        if by_sport:
            report += "<b>📊 ПО ВИДАМ СПОРТА:</b>\n"
            
            sport_names = {
                'football': '⚽ Футбол',
                'tennis': '🎾 Теннис', 
                'table_tennis': '🏓 Настольный теннис',
                'handball': '🤾 Гандбол',
                'manual_entry': '📝 Ручной ввод'
            }
            
            for sport, data in by_sport.items():
                if data['total'] > 0:
                    sport_name = sport_names.get(sport, sport)
                    report += f"{sport_name}: {data['wins']}/{data['total']} ({data['win_rate']:.1f}%)\n"
        
        # Детализация прогнозов
        report += f"""
<b>📋 ДЕТАЛИЗАЦИЯ ПРОГНОЗОВ:</b>
"""
        
        prediction_count = 1
        for prediction in stats['predictions']:
            if prediction['actual_result']:
                result_emoji = "✅" if prediction['actual_result'] == 'win' else "❌"
                sport_emoji = {"football": "⚽", "tennis": "🎾", "table_tennis": "🏓", "handball": "🤾"}.get(prediction['sport_type'], "🏆")
                
                report += f"{prediction_count}. {sport_emoji} {prediction['team1']} vs {prediction['team2']}\n"
                report += f"   Прогноз: {prediction['recommendation']} | Результат: {result_emoji}\n"
                if prediction['notes']:
                    report += f"   Заметка: {prediction['notes']}\n"
                report += "\n"
                prediction_count += 1
        
        # Выводы для ML
        report += f"""<b>🤖 ВЫВОДЫ ДЛЯ МАШИННОГО ОБУЧЕНИЯ:</b>
• Наиболее успешный спорт: {self._get_best_sport(by_sport)}
• Оптимальная уверенность: {self._get_optimal_confidence(stats)}
• Рекомендации для улучшения: {self._get_ml_recommendations(stats)}

<b>═══════════════════════════</b>
💎 <b>TrueLiveBet AI – Учимся на результатах!</b> 💎"""
        
        return report
    
    def _get_best_sport(self, by_sport: Dict) -> str:
        """Определяет наиболее успешный вид спорта"""
        best_sport = "Недостаточно данных"
        best_rate = 0
        
        sport_names = {
            'football': 'Футбол',
            'tennis': 'Теннис', 
            'table_tennis': 'Настольный теннис',
            'handball': 'Гандбол'
        }
        
        for sport, data in by_sport.items():
            if data['total'] >= 2 and data['win_rate'] > best_rate:  # Минимум 2 прогноза
                best_rate = data['win_rate']
                best_sport = f"{sport_names.get(sport, sport)} ({data['win_rate']:.1f}%)"
        
        return best_sport
    
    def _get_optimal_confidence(self, stats: Dict) -> str:
        """Анализирует оптимальный уровень уверенности"""
        predictions = stats['predictions']
        if not predictions:
            return "Недостаточно данных"
        
        # Анализируем винрейт по уровням уверенности
        high_conf = [p for p in predictions if p['confidence'] >= 0.85 and p['actual_result']]
        medium_conf = [p for p in predictions if 0.75 <= p['confidence'] < 0.85 and p['actual_result']]
        
        high_wins = len([p for p in high_conf if p['actual_result'] == 'win'])
        medium_wins = len([p for p in medium_conf if p['actual_result'] == 'win'])
        
        high_rate = high_wins / len(high_conf) * 100 if high_conf else 0
        medium_rate = medium_wins / len(medium_conf) * 100 if medium_conf else 0
        
        if high_rate > medium_rate:
            return f"Высокая уверенность (≥85%): {high_rate:.1f}%"
        else:
            return f"Средняя уверенность (75-84%): {medium_rate:.1f}%"
    
    def _get_ml_recommendations(self, stats: Dict) -> str:
        """Генерирует рекомендации для улучшения"""
        win_rate = stats['win_rate']
        
        if win_rate >= 70:
            return "Система работает отлично, продолжать текущую стратегию"
        elif win_rate >= 50:
            return "Хорошие результаты, можно немного ужесточить критерии"
        elif win_rate >= 30:
            return "Средние результаты, нужно пересмотреть критерии анализа"
        else:
            return "Низкий винрейт, требуется серьезная корректировка алгоритмов"
    
    def _append_to_ml_log(self, prediction: PredictionResult):
        """Добавляет прогноз в ML лог"""
        try:
            # Загружаем существующие логи
            predictions = self._load_ml_log()
            
            # Добавляем новый прогноз
            predictions.append(asdict(prediction))
            
            # Сохраняем
            self._save_ml_log(predictions)
            
        except Exception as e:
            self.logger.error(f"Ошибка добавления в ML лог: {e}")
    
    def _load_ml_log(self) -> List[Dict]:
        """Загружает ML логи"""
        try:
            if os.path.exists(self.ml_log_file):
                with open(self.ml_log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"Ошибка загрузки ML лога: {e}")
            return []
    
    def _save_ml_log(self, predictions: List[Dict]):
        """Сохраняет ML логи"""
        try:
            with open(self.ml_log_file, 'w', encoding='utf-8') as f:
                json.dump(predictions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Ошибка сохранения ML лога: {e}")
    
    def _save_daily_stats(self, stats: Dict):
        """Сохраняет дневную статистику"""
        try:
            with open(self.daily_stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Ошибка сохранения дневной статистики: {e}")
    
    def _extract_coefficient(self, recommendation) -> str:
        """Извлекает коэффициент из рекомендации"""
        try:
            odds = getattr(recommendation, 'odds', {})
            if odds and 'main' in odds:
                return str(odds['main'])
            return "неизвестен"
        except Exception:
            return "неизвестен"
    
    def _empty_daily_stats(self, date: str) -> Dict:
        """Возвращает пустую статистику"""
        return {
            'date': date,
            'generated_at': get_moscow_time().isoformat(),
            'total_predictions': 0,
            'predictions_with_results': 0,
            'wins': 0,
            'losses': 0,
            'win_rate': 0,
            'by_sport': {},
            'predictions': []
        }
    
    def _format_no_stats_message(self) -> str:
        """Сообщение когда нет статистики"""
        moscow_time = get_moscow_time()
        time_str = moscow_time.strftime("%H:%M МСК, %d.%m.%Y")
        
        return f"""📊 <b>ДНЕВНАЯ СТАТИСТИКА</b> (<i>{time_str}</i>) 📊

📋 Сегодня не было прогнозов с известными результатами.

🔄 Система продолжает работу, статистика будет доступна завтра.

💎 <b>TrueLiveBet AI – Качество превыше количества!</b> 💎"""

# Глобальный экземпляр
ml_tracker = MLTrackingSystem()