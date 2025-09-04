from typing import List
from datetime import datetime
from multi_source_controller import MatchData
import logging

logger = logging.getLogger(__name__)

class AITelegramGenerator:
    def __init__(self):
        pass
    
    def _translate_team_name(self, name: str) -> str:
        """Переводит название команды на русский язык"""
        translations = {
            'manchester city': 'Манчестер Сити',
            'manchester united': 'Манчестер Юнайтед',
            'liverpool': 'Ливерпуль',
            'chelsea': 'Челси',
            'arsenal': 'Арсенал',
            'tottenham': 'Тоттенхэм',
            'real madrid': 'Реал Мадрид',
            'barcelona': 'Барселона',
            'atletico madrid': 'Атлетико Мадрид',
            'bayern munich': 'Бавария',
            'borussia dortmund': 'Боруссия Дортмунд',
            'juventus': 'Ювентус',
            'milan': 'Милан',
            'inter': 'Интер',
            'napoli': 'Наполи',
            'psg': 'ПСЖ',
            'monaco': 'Монако',
            'lyon': 'Лион',
            'marseille': 'Марсель',
            'norway': 'Норвегия',
            'denmark': 'Дания',
            'germany': 'Германия',
            'france': 'Франция',
            'spain': 'Испания',
            'italy': 'Италия',
            'england': 'Англия',
            'brazil': 'Бразилия',
            'argentina': 'Аргентина'
        }
        
        name_lower = name.lower()
        for eng_name, rus_name in translations.items():
            if eng_name in name_lower:
                return rus_name
        return name  # Возвращаем оригинальное название, если перевод не найден

    def generate_ai_telegram_report(self, recommendations: List[MatchData]) -> str:
        """
        Генерация финального AI-отчета для Telegram из списка рекомендаций.
        """
        logger.info(f"Генерация AI-отчета для {len(recommendations)} рекомендаций")
        
        if not recommendations:
            logger.info("Нет рекомендаций, генерируем пустой отчет")
            return self._generate_empty_report()
        
        # Группировка рекомендаций по видам спорта
        sport_groups = {
            'football': [],
            'tennis': [],
            'table_tennis': [],
            'handball': []
        }
        
        for rec in recommendations:
            sport_type = rec.sport_type
            if sport_type in sport_groups:
                sport_groups[sport_type].append(rec)
            else:
                logger.warning(f"Неизвестный вид спорта: {sport_type}")
        
        # Генерация финального отчета
        final_report = self._create_final_report(sport_groups)
        
        logger.info("AI-отчет успешно сгенерирован")
        return final_report
    
    def _create_final_report(self, sport_groups: dict) -> str:
        """Создает финальный AI-отчет"""
        current_time = datetime.now()
        time_str = current_time.strftime("%H:%M МСК, %d.%m.%Y")
        
        # Заголовок отчета в соответствии с шаблоном
        report = f"🎯 <b>LIVE-ПРЕДЛОЖЕНИЯ НА</b> (<i>{time_str}</i>) 🎯\n"
        report += "—————————————\n"
        
        # Убираем общую статистику, оставляем только рекомендации
        
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
            
            if matches:
                report += f"{emoji}\n"
                report += "—————————————\n\n"
                
                for match in matches:
                    if match.recommendation_type == 'win':
                        if sport_type == 'tennis' or sport_type == 'table_tennis':
                            report += (
                                f"{global_counter}. {emoji.split(' ')[0]} <b>{match.team1} – {match.team2}</b>\n"
                                f"🎯 Счет: <b>{match.score}</b>\n"
                                f"✅ Ставка: <b>{match.recommendation_value}</b>\n"
                                f"📊 Кэф: <b>{match.coefficient:.2f}</b>\n"
                                f"📌 {match.justification}\n\n"
                            )
                        else:  # football, handball
                            # Переводим названия команд
                            team1_rus = self._translate_team_name(match.team1)
                            team2_rus = self._translate_team_name(match.team2)
                            
                            report += (
                                f"{global_counter}. {emoji.split(' ')[0]} <b>{team1_rus} – {team2_rus}</b>\n"
                                f"🏟️ Счет: <b>{match.score}</b> ({match.minute})\n"
                                f"✅ Ставка: <b>{match.recommendation_value}</b>\n"
                                f"📊 Кэф: <b>{match.coefficient:.2f}</b>\n"
                                f"📌 {match.justification}\n\n"
                            )
                    elif match.recommendation_type == 'total':
                        report += (
                            f"{global_counter}. {emoji.split(' ')[0]} <b>{match.team1} – {match.team2}</b>\n"
                            f"🏟️ Счет: <b>{match.score}</b> ({match.minute})\n"
                            f"📈 Прогнозный тотал: <b>{match.probability:.0f}</b> голов\n"
                            f"🎯 Рекомендация: <b>{match.recommendation_value}</b>\n"
                            f"📌 {match.justification}\n\n"
                        )
                    global_counter += 1
                
                report += "—————————————\n\n"
        
        # Заключение в соответствии с шаблоном
        report += "——————————————————\n"
        report += "💎 <b>TrueLiveBet – Команда экспертов всегда на Вашей стороне!</b> 💎\n\n"
        report += "⚠️ <b>Дисклеймер:</b> Наши прогнозы не являются инвестиционными рекомендациями и не гарантируют выигрыш. Команда аналитиков всегда стремится к максимальному качеству сигналов."
        
        return report
    
    def _generate_empty_report(self) -> str:
        """Генерирует пустой отчет"""
        current_time = datetime.now()
        time_str = current_time.strftime("%H:%M МСК, %d.%m.%Y")
        
        report = f"🎯 <b>LIVE-ПРЕДЛОЖЕНИЯ НА</b> (<i>{time_str}</i>) 🎯\n"
        report += "—————————————\n\n"
        report += "📊 <b>СТАТУС:</b> Нет активных матчей для анализа\n"
        report += "🔍 <b>РЕКОМЕНДАЦИЯ:</b> Попробуйте позже или проверьте другие виды спорта\n\n"
        report += "——————————————————\n"
        report += "💎 <b>TrueLiveBet – Команда экспертов всегда на Вашей стороне!</b> 💎\n\n"
        report += "⚠️ <b>Дисклеймер:</b> Наши прогнозы не являются инвестиционными рекомендациями и не гарантируют выигрыш. Команда аналитиков всегда стремится к максимальному качеству сигналов."
        
        return report