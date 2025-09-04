"""
Модуль для формирования финального отчета для Telegram
"""

from typing import List, Dict
from datetime import datetime
from analyzers.football_analyzer import FootballRecommendation
from analyzers.tennis_analyzer import TennisRecommendation
from analyzers.table_tennis_analyzer import TableTennisRecommendation
from analyzers.handball_analyzer import HandballRecommendation


class ReportGenerator:
    """Генератор отчетов для Telegram"""
    
    def __init__(self):
        self.recommendations = {
            'football': [],
            'tennis': [],
            'table_tennis': [],
            'handball': []
        }
    
    def add_football_recommendations(self, recommendations: List[FootballRecommendation]):
        """Добавление футбольных рекомендаций"""
        self.recommendations['football'] = recommendations
    
    def add_tennis_recommendations(self, recommendations: List[TennisRecommendation]):
        """Добавление теннисных рекомендаций"""
        self.recommendations['tennis'] = recommendations
    
    def add_table_tennis_recommendations(self, recommendations: List[TableTennisRecommendation]):
        """Добавление рекомендаций по настольному теннису"""
        self.recommendations['table_tennis'] = recommendations
    
    def add_handball_recommendations(self, recommendations: List[HandballRecommendation]):
        """Добавление гандбольных рекомендаций"""
        self.recommendations['handball'] = recommendations
    
    def generate_telegram_report(self) -> str:
        """
        Генерация финального отчета для Telegram
        
        Returns:
            str: HTML-форматированный отчет
        """
        current_time = datetime.now()
        time_str = current_time.strftime("%H:%M МСК, %d.%m.%Y")
        
        report = f"""<b>🎯 LIVE-ПРЕДЛОЖЕНИЯ НА </b>(<i>{time_str}</i>)<b> 🎯</b>

<b>—————————————</b>
<b>⚽ ФУТБОЛ ⚽</b>
<b>—————————————</b>

{self._format_football_recommendations()}

<b>—————————————</b>
<b>🎾 ТЕННИС 🎾</b>
<b>—————————————</b>

{self._format_tennis_recommendations()}

<b>—————————————</b>
<b>🏓 НАСТ. ТЕННИС 🏓</b>
<b>—————————————</b>

{self._format_table_tennis_recommendations()}

<b>—————————————</b>
<b>🤾 ГАНДБОЛ 🤾</b>
<b>—————————————</b>

{self._format_handball_recommendations()}

<b>——————————————————</b>
<b>💎 TrueLiveBet – Мы всегда на Вашей стороне! 💎</b>"""
        
        return report
    
    def _format_football_recommendations(self) -> str:
        """Форматирование футбольных рекомендаций"""
        if not self.recommendations['football']:
            return "<i>Нет подходящих матчей</i>"
        
        formatted = []
        for i, rec in enumerate(self.recommendations['football'], 1):
            formatted.append(f"""<b>⚽ {rec.team1} – {rec.team2}</b>
🏟️ Счет: <b>{rec.score}</b> ({rec.minute})
✅ Ставка: <b>{rec.bet_type}</b>
📊 Кэф: <b>{rec.coefficient}</b>
📌 <i>{rec.justification}</i>""")
        
        return "\n\n".join(formatted)
    
    def _format_tennis_recommendations(self) -> str:
        """Форматирование теннисных рекомендаций"""
        if not self.recommendations['tennis']:
            return "<i>Нет подходящих матчей</i>"
        
        formatted = []
        for i, rec in enumerate(self.recommendations['tennis'], 1):
            formatted.append(f"""<b>🎾 {rec.player1} – {rec.player2}</b>
🎯 Счет: <b>{rec.score}</b> ({rec.games})
✅ Ставка: <b>{rec.bet_type}</b>
📊 Кэф: <b>{rec.coefficient}</b>
📌 <i>{rec.justification}</i>""")
        
        return "\n\n".join(formatted)
    
    def _format_table_tennis_recommendations(self) -> str:
        """Форматирование рекомендаций по настольному теннису"""
        if not self.recommendations['table_tennis']:
            return "<i>Нет подходящих матчей</i>"
        
        formatted = []
        for i, rec in enumerate(self.recommendations['table_tennis'], 1):
            formatted.append(f"""<b>🏓 {rec.player1} – {rec.player2}</b>
🎯 Счет: <b>{rec.score}</b>
✅ Ставка: <b>{rec.bet_type}</b>
📊 Кэф: <b>{rec.coefficient}</b>
📌 <i>{rec.justification}</i>""")
        
        return "\n\n".join(formatted)
    
    def _format_handball_recommendations(self) -> str:
        """Форматирование гандбольных рекомендаций"""
        if not self.recommendations['handball']:
            return "<i>Нет подходящих матчей</i>"
        
        formatted = []
        for i, rec in enumerate(self.recommendations['handball'], 1):
            if rec.recommendation_type == "win":
                # Формат для прямых побед
                formatted.append(f"""<b>🤾 {rec.team1} – {rec.team2}</b>
🏟️ Счет: <b>{rec.score}</b> ({rec.minute})
✅ Ставка: <b>{rec.bet_type}</b>
📊 Кэф: <b>{rec.coefficient}</b>
📌 <i>{rec.justification}</i>""")
            elif rec.recommendation_type == "total":
                # Формат для тоталов
                formatted.append(f"""<b>🤾 {rec.team1} – {rec.team2}</b>
🏟️ Счет: <b>{rec.score}</b> ({rec.minute})
📈 Прогнозный тотал: <b>{rec.predicted_total}</b> голов
🎯 Рекомендация: <b>{rec.bet_type}</b>
📌 <i>{rec.justification}</i>""")
        
        return "\n\n".join(formatted)
    
    def get_recommendations_count(self) -> Dict[str, int]:
        """
        Получение количества рекомендаций по видам спорта
        
        Returns:
            Dict[str, int]: Словарь с количеством рекомендаций
        """
        return {
            'football': len(self.recommendations['football']),
            'tennis': len(self.recommendations['tennis']),
            'table_tennis': len(self.recommendations['table_tennis']),
            'handball': len(self.recommendations['handball'])
        }
    
    def get_total_recommendations_count(self) -> int:
        """
        Получение общего количества рекомендаций
        
        Returns:
            int: Общее количество рекомендаций
        """
        return sum(self.get_recommendations_count().values())
    
    def clear_recommendations(self):
        """Очистка всех рекомендаций"""
        self.recommendations = {
            'football': [],
            'tennis': [],
            'table_tennis': [],
            'handball': []
        }