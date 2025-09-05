#!/usr/bin/env python3
"""
Улучшенный форматтер для Telegram отчетов по новому промпту
"""

import logging
from typing import List, Dict
from datetime import datetime
from multi_source_controller import MatchData

logger = logging.getLogger(__name__)

class EnhancedTelegramFormatter:
    """Улучшенный форматтер отчетов для Telegram"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def format_enhanced_report(self, recommendations: List[MatchData]) -> str:
        """
        Форматирует отчет по новому шаблону промпта
        """
        if not recommendations:
            return self._format_no_recommendations()
        
        # Группируем по видам спорта
        by_sport = self._group_by_sport(recommendations)
        
        # Формируем заголовок
        current_time = datetime.now()
        time_str = current_time.strftime("%H:%M МСК, %d.%m.%Y")
        
        report = f"""🎯 <b>LIVE-ПРЕДЛОЖЕНИЯ НА</b> (<i>{time_str}</i>) <b>🎯</b>
<b>—————————————</b>
"""
        
        # Добавляем разделы по видам спорта
        sport_order = ['football', 'tennis', 'table_tennis', 'handball']
        sport_names = {
            'football': '⚽ ФУТБОЛ ⚽',
            'tennis': '🎾 ТЕННИС 🎾', 
            'table_tennis': '🏓 НАСТОЛЬНЫЙ ТЕННИС 🏓',
            'handball': '🤾 ГАНДБОЛ 🤾'
        }
        
        recommendation_counter = 1
        
        for sport_type in sport_order:
            if sport_type in by_sport and by_sport[sport_type]:
                report += f"\n<b>{sport_names[sport_type]}</b>\n"
                report += "<b>—————————————</b>\n\n"
                
                for rec in by_sport[sport_type]:
                    formatted_rec = self._format_single_recommendation(rec, recommendation_counter, sport_type)
                    report += formatted_rec + "\n"
                    recommendation_counter += 1
        
        # Добавляем подпись
        report += """
<b>——————————————————</b>
💎 <b>TrueLiveBet – Анализ на основе AI и статистики!</b> 💎

⚠️ <b>Дисклеймер:</b> Наши прогнозы основаны на анализе, но не гарантируют прибыль."""
        
        return report
    
    def _group_by_sport(self, recommendations: List[MatchData]) -> Dict:
        """Группирует рекомендации по видам спорта"""
        by_sport = {}
        
        for rec in recommendations:
            sport_type = getattr(rec, 'sport_type', getattr(rec, 'sport', 'unknown'))
            if sport_type not in by_sport:
                by_sport[sport_type] = []
            by_sport[sport_type].append(rec)
        
        return by_sport
    
    def _format_single_recommendation(self, rec: MatchData, number: int, sport_type: str) -> str:
        """Форматирует одну рекомендацию по новому шаблону"""
        
        if sport_type == 'football':
            return f"""{number}. ⚽ <b>{rec.team1} – {rec.team2}</b>
🏟️ Счет: <b>{rec.score}</b> ({rec.minute}') | До конца: ~{self._calculate_time_left(rec.minute, 90)} мин. | Лига: {rec.league}
✅ Ставка: <b>{rec.recommendation_value}</b>
📊 Кэф: <b>{self._get_coefficient_estimate(rec)}</b>
📌 {rec.justification}"""
            
        elif sport_type == 'tennis':
            return f"""{number}. 🎾 <b>{rec.team1} – {rec.team2}</b>
🎯 Счет: <b>{rec.score}</b> | Турнир: {rec.league}
✅ Ставка: <b>{rec.recommendation_value}</b>
📊 Кэф: <b>{self._get_coefficient_estimate(rec)}</b>
📌 {rec.justification}"""
            
        elif sport_type == 'table_tennis':
            return f"""{number}. 🏓 <b>{rec.team1} – {rec.team2}</b>
🏓 Счет: <b>{rec.score}</b> | Турнир: {rec.league}
✅ Ставка: <b>{rec.recommendation_value}</b>
📊 Кэф: <b>{self._get_coefficient_estimate(rec)}</b>
📌 {rec.justification}"""
            
        elif sport_type == 'handball':
            time_left = self._calculate_time_left(rec.minute, 60)
            return f"""{number}. 🤾 <b>{rec.team1} – {rec.team2}</b>
🏟️ Счет: <b>{rec.score}</b> ({rec.minute}') | До конца: ~{time_left} мин. | Лига: {rec.league}
✅ Ставка: <b>{rec.recommendation_value}</b>
📊 Кэф: <b>{self._get_coefficient_estimate(rec)}</b>
📌 {rec.justification}"""
        
        else:
            return f"""{number}. 🏆 <b>{rec.team1} – {rec.team2}</b>
Счет: <b>{rec.score}</b> | Ставка: <b>{rec.recommendation_value}</b>
📌 {rec.justification}"""
    
    def _calculate_time_left(self, current_minute: str, total_minutes: int) -> int:
        """Рассчитывает оставшееся время матча"""
        try:
            minute = int(current_minute.replace("'", "").replace("′", "")) if current_minute.replace("'", "").replace("′", "").isdigit() else 0
            time_left = max(0, total_minutes - minute)
            return time_left
        except Exception:
            return 0
    
    def _get_coefficient_estimate(self, rec: MatchData) -> str:
        """Получает примерный коэффициент на основе уверенности"""
        try:
            confidence = getattr(rec, 'probability', 80) / 100
            
            # Примерная формула коэффициента на основе вероятности
            if confidence >= 0.90:
                return "1.15-1.25"
            elif confidence >= 0.85:
                return "1.25-1.40"
            elif confidence >= 0.80:
                return "1.40-1.60"
            elif confidence >= 0.75:
                return "1.60-1.85"
            else:
                return "1.85-2.20"
                
        except Exception:
            return "1.50-1.80"
    
    def _format_no_recommendations(self) -> str:
        """Форматирует сообщение об отсутствии рекомендаций"""
        current_time = datetime.now()
        time_str = current_time.strftime("%H:%M МСК, %d.%m.%Y")
        
        return f"""🎯 <b>LIVE-АНАЛИЗ НА</b> (<i>{time_str}</i>) <b>🎯</b>

📊 На текущий момент подходящих событий не найдено.

Система проанализировала все доступные live-матчи, но ни один не соответствует строгим критериям качества.

🔄 Следующий анализ через 45 минут.

——————————————————
💎 <b>TrueLiveBet – Качество превыше количества!</b> 💎"""

    def escape_markdown_v2(self, text: str) -> str:
        """Экранирует текст для MarkdownV2"""
        # Символы, которые нужно экранировать в MarkdownV2
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    def format_for_markdown_v2(self, report: str) -> str:
        """Форматирует отчет для MarkdownV2"""
        # Заменяем HTML теги на MarkdownV2
        report = report.replace('<b>', '*').replace('</b>', '*')
        report = report.replace('<i>', '_').replace('</i>', '_')
        
        # Экранируем специальные символы
        lines = report.split('\n')
        escaped_lines = []
        
        for line in lines:
            if line.strip():
                # Не экранируем строки с markdown разметкой
                if '*' in line or '_' in line:
                    escaped_lines.append(line)
                else:
                    escaped_lines.append(self.escape_markdown_v2(line))
            else:
                escaped_lines.append(line)
        
        return '\n'.join(escaped_lines)

# Глобальный экземпляр форматтера
enhanced_formatter = EnhancedTelegramFormatter()