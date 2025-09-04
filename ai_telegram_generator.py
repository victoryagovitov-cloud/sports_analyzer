"""
AI-генератор отчетов для Telegram с использованием Claude
"""
import logging
from typing import List, Dict, Any
from datetime import datetime
from multi_source_controller import MatchData
import json

logger = logging.getLogger(__name__)

class AITelegramGenerator:
    """AI-генератор отчетов для Telegram с использованием Claude"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def generate_ai_telegram_report(self, recommendations: List[MatchData]) -> str:
        """
        Генерирует AI-отчет для Telegram с помощью Claude
        """
        if not recommendations:
            return self._generate_empty_report()
        
        self.logger.info(f"Генерация AI-отчета для {len(recommendations)} рекомендаций")
        
        # Группируем рекомендации по видам спорта
        sport_groups = self._group_recommendations_by_sport(recommendations)
        
        # Генерируем AI-анализ для каждой группы
        ai_analysis = self._generate_ai_analysis(sport_groups)
        
        # Создаем финальный отчет
        report = self._create_final_report(ai_analysis, sport_groups)
        
        self.logger.info("AI-отчет успешно сгенерирован")
        return report
    
    def _group_recommendations_by_sport(self, recommendations: List[MatchData]) -> Dict[str, List[MatchData]]:
        """Группирует рекомендации по видам спорта"""
        groups = {
            'football': [],
            'tennis': [],
            'table_tennis': [],
            'handball': []
        }
        
        for rec in recommendations:
            if rec.sport_type in groups:
                groups[rec.sport_type].append(rec)
            else:
                self.logger.warning(f"Неизвестный вид спорта: {rec.sport_type}")
        
        return groups
    
    def _generate_ai_analysis(self, sport_groups: Dict[str, List[MatchData]]) -> Dict[str, Dict[str, Any]]:
        """
        Генерирует AI-анализ для каждой группы спорта
        В реальной реализации здесь будет вызов Claude API
        """
        ai_analysis = {}
        
        for sport_type, matches in sport_groups.items():
            if matches:
                # Пока используем эвристический анализ, но структура готова для Claude API
                ai_analysis[sport_type] = self._heuristic_sport_analysis(sport_type, matches)
            else:
                ai_analysis[sport_type] = {
                    'summary': f"Нет активных матчей по {sport_type}",
                    'confidence': 0.0,
                    'key_insights': [],
                    'recommendations_count': 0
                }
        
        return ai_analysis
    
    def _heuristic_sport_analysis(self, sport_type: str, matches: List[MatchData]) -> Dict[str, Any]:
        """
        Эвристический анализ спорта (временная замена для Claude API)
        """
        analysis = {
            'summary': '',
            'confidence': 0.0,
            'key_insights': [],
            'recommendations_count': len(matches),
            'top_matches': [],
            'risk_assessment': 'medium'
        }
        
        if sport_type == 'football':
            analysis = self._analyze_football_group(matches)
        elif sport_type == 'tennis':
            analysis = self._analyze_tennis_group(matches)
        elif sport_type == 'table_tennis':
            analysis = self._analyze_table_tennis_group(matches)
        elif sport_type == 'handball':
            analysis = self._analyze_handball_group(matches)
        
        return analysis
    
    def _analyze_football_group(self, matches: List[MatchData]) -> Dict[str, Any]:
        """Анализ группы футбольных матчей"""
        win_matches = [m for m in matches if m.recommendation_type == 'win']
        avg_confidence = sum(m.probability for m in win_matches) / len(win_matches) if win_matches else 0
        
        insights = []
        if len(win_matches) > 5:
            insights.append("Высокая активность live-матчей")
        if avg_confidence > 80:
            insights.append("Высокие показатели уверенности в прогнозах")
        
        top_matches = sorted(win_matches, key=lambda x: x.probability, reverse=True)[:3]
        
        return {
            'summary': f"Найдено {len(win_matches)} перспективных футбольных матчей с средним уровнем уверенности {avg_confidence:.1f}%",
            'confidence': avg_confidence,
            'key_insights': insights,
            'recommendations_count': len(win_matches),
            'top_matches': [{'teams': f"{m.team1} - {m.team2}", 'confidence': m.probability} for m in top_matches],
            'risk_assessment': 'low' if avg_confidence > 85 else 'medium' if avg_confidence > 75 else 'high'
        }
    
    def _analyze_tennis_group(self, matches: List[MatchData]) -> Dict[str, Any]:
        """Анализ группы теннисных матчей"""
        win_matches = [m for m in matches if m.recommendation_type == 'win']
        avg_confidence = sum(m.probability for m in win_matches) / len(win_matches) if win_matches else 0
        
        insights = []
        if len(win_matches) > 10:
            insights.append("Очень высокая активность в теннисе")
        if avg_confidence > 80:
            insights.append("Отличные возможности для ставок")
        
        top_matches = sorted(win_matches, key=lambda x: x.probability, reverse=True)[:5]
        
        return {
            'summary': f"Обнаружено {len(win_matches)} теннисных матчей с высоким потенциалом (средняя уверенность: {avg_confidence:.1f}%)",
            'confidence': avg_confidence,
            'key_insights': insights,
            'recommendations_count': len(win_matches),
            'top_matches': [{'players': f"{m.team1} - {m.team2}", 'confidence': m.probability} for m in top_matches],
            'risk_assessment': 'low' if avg_confidence > 85 else 'medium'
        }
    
    def _analyze_table_tennis_group(self, matches: List[MatchData]) -> Dict[str, Any]:
        """Анализ группы матчей настольного тенниса"""
        win_matches = [m for m in matches if m.recommendation_type == 'win']
        avg_confidence = sum(m.probability for m in win_matches) / len(win_matches) if win_matches else 0
        
        insights = []
        if len(win_matches) > 15:
            insights.append("Максимальная активность в настольном теннисе")
        if avg_confidence > 75:
            insights.append("Стабильные возможности для ставок")
        
        top_matches = sorted(win_matches, key=lambda x: x.probability, reverse=True)[:5]
        
        return {
            'summary': f"Выявлено {len(win_matches)} матчей настольного тенниса с хорошими перспективами (уверенность: {avg_confidence:.1f}%)",
            'confidence': avg_confidence,
            'key_insights': insights,
            'recommendations_count': len(win_matches),
            'top_matches': [{'players': f"{m.team1} - {m.team2}", 'confidence': m.probability} for m in top_matches],
            'risk_assessment': 'low' if avg_confidence > 80 else 'medium'
        }
    
    def _analyze_handball_group(self, matches: List[MatchData]) -> Dict[str, Any]:
        """Анализ группы гандбольных матчей"""
        win_matches = [m for m in matches if m.recommendation_type == 'win']
        total_matches = [m for m in matches if m.recommendation_type == 'total']
        
        all_matches = win_matches + total_matches
        avg_confidence = sum(m.probability for m in all_matches) / len(all_matches) if all_matches else 0
        
        insights = []
        if len(win_matches) > 0:
            insights.append(f"Найдено {len(win_matches)} матчей с прямыми победами")
        if len(total_matches) > 0:
            insights.append(f"Обнаружено {len(total_matches)} матчей с тоталами")
        
        top_matches = sorted(all_matches, key=lambda x: x.probability, reverse=True)[:3]
        
        return {
            'summary': f"Проанализировано {len(all_matches)} гандбольных матчей (победы: {len(win_matches)}, тоталы: {len(total_matches)})",
            'confidence': avg_confidence,
            'key_insights': insights,
            'recommendations_count': len(all_matches),
            'top_matches': [{'teams': f"{m.team1} - {m.team2}", 'confidence': m.probability, 'type': m.recommendation_type} for m in top_matches],
            'risk_assessment': 'medium' if avg_confidence > 70 else 'high'
        }
    
    def _create_final_report(self, ai_analysis: Dict[str, Dict[str, Any]], sport_groups: Dict[str, List[MatchData]]) -> str:
        """Создает финальный AI-отчет"""
        current_time = datetime.now()
        time_str = current_time.strftime("%H:%M МСК, %d.%m.%Y")
        
        # Заголовок отчета
        report = f"<b>🤖 AI LIVE-АНАЛИЗ </b>(<i>{time_str}</i>)<b> 🤖</b>\n"
        report += "<b>—————————————</b>\n"
        
        # Общая статистика
        total_recommendations = sum(len(matches) for matches in sport_groups.values())
        avg_confidence = sum(analysis.get('confidence', 0) for analysis in ai_analysis.values()) / len(ai_analysis) if ai_analysis else 0
        
        report += f"<b>📊 ОБЩАЯ СТАТИСТИКА:</b>\n"
        report += f"• Всего рекомендаций: <b>{total_recommendations}</b>\n"
        report += f"• Средняя уверенность: <b>{avg_confidence:.1f}%</b>\n"
        report += f"• Источники данных: <b>Betzona.ru + Scores24.live</b>\n"
        report += "<b>—————————————</b>\n\n"
        
        # Анализ по видам спорта
        sport_emojis = {
            'football': '⚽ ФУТБОЛ ⚽',
            'tennis': '🎾 ТЕННИС 🎾',
            'table_tennis': '🏓 НАСТ. ТЕННИС 🏓',
            'handball': '🤾 ГАНДБОЛ 🤾'
        }
        
        global_counter = 1
        for sport_type, emoji in sport_emojis.items():
            matches = sport_groups[sport_type]
            analysis = ai_analysis[sport_type]
            
            if matches:
                report += f"<b>{emoji}</b>\n"
                report += f"<i>AI-анализ: {analysis['summary']}</i>\n"
                
                if analysis['key_insights']:
                    report += f"<b>🔍 Ключевые инсайты:</b>\n"
                    for insight in analysis['key_insights']:
                        report += f"• {insight}\n"
                
                report += f"<b>🎯 Рекомендации ({len(matches)}):</b>\n"
                report += "<b>—————————————</b>\n"
                
                for match in matches:
                    if match.recommendation_type == 'win':
                        report += (
                            f"{global_counter}. <b>{emoji.split(' ')[0]} {match.team1} – {match.team2}</b>\n"
                            f"🏟️ Счет: <b>{match.score}</b> ({match.minute})\n"
                            f"✅ Ставка: <b>{match.recommendation_value}</b>\n"
                            f"📊 Кэф: <b>{match.coefficient:.2f}</b> | Уверенность: <b>{match.probability:.1f}%</b>\n"
                            f"📌 <i>{match.justification}</i>\n\n"
                        )
                    elif match.recommendation_type == 'total':
                        report += (
                            f"{global_counter}. <b>{emoji.split(' ')[0]} {match.team1} – {match.team2}</b>\n"
                            f"🏟️ Счет: <b>{match.score}</b> ({match.minute})\n"
                            f"📈 Прогнозный тотал: <b>{match.probability:.0f}</b> голов\n"
                            f"🎯 Рекомендация: <b>{match.recommendation_value}</b>\n"
                            f"📊 Кэф: <b>{match.coefficient:.2f}</b>\n"
                            f"📌 <i>{match.justification}</i>\n\n"
                        )
                    global_counter += 1
                
                report += "<b>—————————————</b>\n\n"
        
        # Заключение AI
        report += "<b>🤖 AI-ЗАКЛЮЧЕНИЕ:</b>\n"
        high_confidence_sports = [sport for sport, analysis in ai_analysis.items() 
                                if analysis.get('confidence', 0) > 80 and analysis.get('recommendations_count', 0) > 0]
        
        if high_confidence_sports:
            report += f"• <b>Лучшие возможности:</b> {', '.join(high_confidence_sports)}\n"
        
        if avg_confidence > 80:
            report += "• <b>Общий уровень уверенности: ВЫСОКИЙ</b> 🟢\n"
        elif avg_confidence > 70:
            report += "• <b>Общий уровень уверенности: СРЕДНИЙ</b> 🟡\n"
        else:
            report += "• <b>Общий уровень уверенности: НИЗКИЙ</b> 🔴\n"
        
        report += "• <b>Рекомендация:</b> Сосредоточьтесь на матчах с уверенностью >80%\n"
        report += "• <b>Управление рисками:</b> Не ставьте более 2-3% от банка на один матч\n\n"
        
        report += "<b>💎 TrueLiveBet AI – Умные ставки с искусственным интеллектом! 💎</b>"
        
        return report
    
    def _generate_empty_report(self) -> str:
        """Генерирует пустой отчет"""
        current_time = datetime.now()
        time_str = current_time.strftime("%H:%M МСК, %d.%m.%Y")
        
        report = f"<b>🤖 AI LIVE-АНАЛИЗ </b>(<i>{time_str}</i>)<b> 🤖</b>\n"
        report += "<b>—————————————</b>\n"
        report += "<b>📊 СТАТУС:</b> Нет активных матчей для анализа\n"
        report += "<b>🔍 РЕКОМЕНДАЦИЯ:</b> Попробуйте позже или проверьте другие виды спорта\n"
        report += "<b>—————————————</b>\n"
        report += "<b>💎 TrueLiveBet AI – Умные ставки с искусственным интеллектом! 💎</b>"
        
        return report