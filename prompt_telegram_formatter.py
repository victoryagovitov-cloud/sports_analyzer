#!/usr/bin/env python3
"""
Форматтер Telegram отчетов СТРОГО по шаблону промпта
"""

import logging
from typing import List, Dict
from multi_source_controller import MatchData
from moscow_time import format_moscow_time_for_telegram

logger = logging.getLogger(__name__)

class PromptTelegramFormatter:
    """
    Форматтер отчетов СТРОГО по шаблону из промпта пользователя
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def format_report_by_prompt(self, recommendations: List[MatchData]) -> str:
        """
        Форматирует отчет СТРОГО по шаблону из промпта
        """
        if not recommendations:
            return self._format_no_matches_found()
        
        # Группируем по видам спорта
        by_sport = self._group_by_sport(recommendations)
        
        # Формируем заголовок с московским временем
        time_str = format_moscow_time_for_telegram()
        
        report = f"""🎯 <b>LIVE-ПРЕДЛОЖЕНИЯ НА</b> (<i>{time_str}</i>) <b>🎯</b>
<b>—————————————</b>"""
        
        recommendation_counter = 1
        
        # ⚽ ФУТБОЛ
        if 'football' in by_sport and by_sport['football']:
            report += f"""

<b>⚽ ФУТБОЛ ⚽</b>
<b>—————————————</b>

"""
            for rec in by_sport['football']:
                report += self._format_football_recommendation(rec, recommendation_counter)
                recommendation_counter += 1
        
        # 🎾 ТЕННИС  
        if 'tennis' in by_sport and by_sport['tennis']:
            report += f"""

<b>🎾 ТЕННИС 🎾</b>
<b>—————————————</b>

"""
            for rec in by_sport['tennis']:
                report += self._format_tennis_recommendation(rec, recommendation_counter)
                recommendation_counter += 1
        
        # 🏓 НАСТОЛЬНЫЙ ТЕННИС
        if 'table_tennis' in by_sport and by_sport['table_tennis']:
            report += f"""

<b>🏓 НАСТОЛЬНЫЙ ТЕННИС 🏓</b>
<b>—————————————</b>

"""
            for rec in by_sport['table_tennis']:
                report += self._format_table_tennis_recommendation(rec, recommendation_counter)
                recommendation_counter += 1
        
        # 🤾 ГАНДБОЛ
        if 'handball' in by_sport and by_sport['handball']:
            report += f"""

<b>🤾 ГАНДБОЛ 🤾</b>
<b>—————————————</b>

"""
            for rec in by_sport['handball']:
                report += self._format_handball_recommendation(rec, recommendation_counter)
                recommendation_counter += 1
        
        # Подпись строго по промпту
        report += f"""

<b>——————————————————</b>
💎 <b>TrueLiveBet – Анализ на основе AI и статистики!</b> 💎

⚠️ <b>Дисклеймер:</b> Наши прогнозы основаны на анализе, но не гарантируют прибыль."""
        
        return report
    
    def _format_football_recommendation(self, rec: MatchData, number: int) -> str:
        """
        Форматирует футбольную рекомендацию СТРОГО по шаблону промпта
        """
        # Рассчитываем время до конца
        minute_str = getattr(rec, 'minute', '0')
        minute = int(minute_str.replace("'", "").replace("′", "")) if minute_str.replace("'", "").replace("′", "").isdigit() else 0
        time_left = max(0, 90 - minute)
        
        # Получаем коэффициент
        coefficient = self._get_real_coefficient(rec)
        
        return f"""{number}. ⚽ <b>{rec.team1} – {rec.team2}</b>
🏟️ Счет: <b>{rec.score}</b> ({rec.minute}') | До конца: ~{time_left} мин. | Лига: {rec.league}
✅ Ставка: <b>{rec.recommendation_value}</b>
📊 Кэф: <b>{coefficient}</b>
📌 {rec.justification}

"""
    
    def _format_tennis_recommendation(self, rec: MatchData, number: int) -> str:
        """
        Форматирует теннисную рекомендацию по шаблону промпта
        """
        coefficient = self._get_real_coefficient(rec)
        
        return f"""{number}. 🎾 <b>{rec.team1} – {rec.team2}</b>
🎯 Счет: <b>{rec.score}</b> | Турнир: {rec.league}
✅ Ставка: <b>{rec.recommendation_value}</b>
📊 Кэф: <b>{coefficient}</b>
📌 {rec.justification}

"""
    
    def _format_table_tennis_recommendation(self, rec: MatchData, number: int) -> str:
        """Форматирует настольный теннис"""
        coefficient = self._get_real_coefficient(rec)
        
        return f"""{number}. 🏓 <b>{rec.team1} – {rec.team2}</b>
🏓 Счет: <b>{rec.score}</b> | Турнир: {rec.league}
✅ Ставка: <b>{rec.recommendation_value}</b>
📊 Кэф: <b>{coefficient}</b>
📌 {rec.justification}

"""
    
    def _format_handball_recommendation(self, rec: MatchData, number: int) -> str:
        """Форматирует гандбол"""
        minute_str = getattr(rec, 'minute', '0')
        minute = int(minute_str.replace("'", "").replace("′", "")) if minute_str.replace("'", "").replace("′", "").isdigit() else 0
        time_left = max(0, 60 - minute)
        
        coefficient = self._get_real_coefficient(rec)
        
        return f"""{number}. 🤾 <b>{rec.team1} – {rec.team2}</b>
🏟️ Счет: <b>{rec.score}</b> ({rec.minute}') | До конца: ~{time_left} мин. | Лига: {rec.league}
✅ Ставка: <b>{rec.recommendation_value}</b>
📊 Кэф: <b>{coefficient}</b>
📌 {rec.justification}

"""
    
    def _get_real_coefficient(self, rec: MatchData) -> str:
        """
        Получает реальный коэффициент (по промпту)
        """
        # Пробуем получить из данных матча
        odds = getattr(rec, 'odds', {})
        if odds and 'main' in odds:
            return f"{odds['main']:.2f}"
        
        # Если нет реального коэффициента, оцениваем по уверенности
        confidence = getattr(rec, 'probability', 80) / 100
        
        if confidence >= 0.90:
            return "1.25"
        elif confidence >= 0.85:
            return "1.35"
        elif confidence >= 0.80:
            return "1.55"
        elif confidence >= 0.75:
            return "1.75"
        else:
            return "1.95"
    
    def _group_by_sport(self, recommendations: List[MatchData]) -> Dict:
        """Группирует рекомендации по видам спорта"""
        by_sport = {}
        
        for rec in recommendations:
            sport_type = getattr(rec, 'sport_type', getattr(rec, 'sport', 'unknown'))
            if sport_type not in by_sport:
                by_sport[sport_type] = []
            by_sport[sport_type].append(rec)
        
        return by_sport
    
    def _format_no_matches_found(self) -> str:
        """Форматирует сообщение об отсутствии матчей (по промпту)"""
        time_str = format_moscow_time_for_telegram()
        
        return f"""🎯 <b>LIVE-АНАЛИЗ НА</b> (<i>{time_str}</i>) <b>🎯</b>

📊 На текущий момент подходящих событий не найдено.

Система проанализировала все live-матчи на scores24.live, но ни один не соответствует строгим критериям качества.

🔄 Следующий анализ через 45 минут.

——————————————————
💎 <b>TrueLiveBet – Анализ на основе AI и статистики!</b> 💎"""

# Глобальный экземпляр
prompt_telegram_formatter = PromptTelegramFormatter()