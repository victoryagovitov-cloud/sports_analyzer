"""
Простой генератор отчетов для мульти-источниковой системы
"""

from typing import List
from datetime import datetime
from multi_source_controller import MatchData

class SimpleReportGenerator:
    """Простой генератор отчетов"""
    
    def generate_report(self, recommendations: List[MatchData]) -> str:
        """Генерация отчета из рекомендаций"""
        if not recommendations:
            return "Нет рекомендаций для отчета"
        
        current_time = datetime.now()
        time_str = current_time.strftime("%H:%M МСК, %d.%m.%Y")
        
        # Группируем по видам спорта
        by_sport = {}
        for rec in recommendations:
            sport = rec.sport_type
            if sport not in by_sport:
                by_sport[sport] = []
            by_sport[sport].append(rec)
        
        report = f"""<b>🎯 LIVE-ПРЕДЛОЖЕНИЯ НА </b>(<i>{time_str}</i>)<b> 🎯</b>
<b>—————————————</b>
"""
        
        # Эмодзи для видов спорта
        sport_emojis = {
            'football': '⚽',
            'tennis': '🎾',
            'table_tennis': '🏓',
            'handball': '🤾'
        }
        
        # Названия видов спорта
        sport_names = {
            'football': 'ФУТБОЛ',
            'tennis': 'ТЕННИС',
            'table_tennis': 'НАСТ. ТЕННИС',
            'handball': 'ГАНДБОЛ'
        }
        
        for sport, recs in by_sport.items():
            emoji = sport_emojis.get(sport, '🏆')
            name = sport_names.get(sport, sport.upper())
            
            report += f"<b>{emoji} {name} {emoji}</b>\n"
            report += "<b>—————————————</b>\n"
            
            for i, rec in enumerate(recs, 1):
                report += self._format_recommendation(rec, i)
            
            report += "\n"
        
        report += """<b>——————————————————</b>
<b>💎 TrueLiveBet – Мы всегда на Вашей стороне! 💎</b>"""
        
        return report
    
    def _format_recommendation(self, rec: MatchData, number: int) -> str:
        """Форматирование одной рекомендации"""
        # Эмодзи для видов спорта
        sport_emojis = {
            'football': '⚽',
            'tennis': '🎾',
            'table_tennis': '🏓',
            'handball': '🤾'
        }
        
        emoji = sport_emojis.get(rec.sport_type, '🏆')
        
        # Форматируем в зависимости от типа рекомендации
        if rec.recommendation_type == 'win':
            if rec.sport_type == 'football':
                return f"""{number}. <b>{emoji} {rec.team1} – {rec.team2}</b>
🏟️ Счет: <b>{rec.score}</b> ({rec.minute}′)
✅ Ставка: <b>{rec.recommendation_value}</b>
📊 Кэф: <b>1.85</b>
📌 <i>{rec.justification}</i>

"""
            elif rec.sport_type in ['tennis', 'table_tennis']:
                return f"""{number}. <b>{emoji} {rec.team1} – {rec.team2}</b>
🎯 Счет: <b>{rec.score}</b>
✅ Ставка: <b>{rec.recommendation_value}</b>
📊 Кэф: <b>1.85</b>
📌 <i>{rec.justification}</i>

"""
            elif rec.sport_type == 'handball':
                return f"""{number}. <b>{emoji} {rec.team1} – {rec.team2}</b>
🏟️ Счет: <b>{rec.score}</b> ({rec.minute}′)
✅ Ставка: <b>{rec.recommendation_value}</b>
📊 Кэф: <b>1.85</b>
📌 <i>{rec.justification}</i>

"""
        
        # Для тоталов
        elif rec.recommendation_type == 'total':
            return f"""{number}. <b>{emoji} {rec.team1} – {rec.team2}</b>
🏟️ Счет: <b>{rec.score}</b> ({rec.minute}′)
📈 Прогнозный тотал: <b>{rec.recommendation_value}</b>
📌 <i>{rec.justification}</i>

"""
        
        # Общий формат
        return f"""{number}. <b>{emoji} {rec.team1} – {rec.team2}</b>
🏟️ Счет: <b>{rec.score}</b> ({rec.minute}′)
✅ Ставка: <b>{rec.recommendation_value}</b>
📊 Кэф: <b>1.85</b>
📌 <i>{rec.justification}</i>

"""