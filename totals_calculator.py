#!/usr/bin/env python3
"""
Калькулятор тоталов по улучшенной формуле
"""

import math
import logging
from typing import Dict, Optional
from multi_source_controller import MatchData

logger = logging.getLogger(__name__)

class TotalsCalculator:
    """Калькулятор тоталов для гандбола по новой формуле"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def calculate_handball_totals(self, match: MatchData) -> Dict:
        """
        Расчет тоталов для гандбола по новой формуле
        Формула: ОКРУГЛВВЕРХ((Голы1 + Голы2) / (30 + Минута_Второй_Половины) * 60)
        """
        try:
            if ':' not in match.score:
                return {}
            
            home_score, away_score = map(int, match.score.split(':'))
            minute_str = getattr(match, 'minute', '0')
            minute = int(minute_str.replace("'", "").replace("′", "")) if minute_str.replace("'", "").replace("′", "").isdigit() else 0
            
            total_goals = home_score + away_score
            
            # Проверяем, что это вторая половина (>30 мин)
            if minute <= 30:
                self.logger.info(f"Матч {match.team1} vs {match.team2}: слишком рано для расчета тоталов ({minute} мин)")
                return {}
            
            # Расчет по новой формуле
            second_half_minute = minute - 30  # Минуты во второй половине
            predicted_total_float = (total_goals / (30 + second_half_minute)) * 60
            predicted_total = math.ceil(predicted_total_float)  # ОКРУГЛВВЕРХ
            
            # Определение рекомендации
            if total_goals > minute:
                # Быстрый темп: голы больше минут
                recommendation_value = predicted_total - 4
                recommendation = f"ТБ {recommendation_value}"
                tempo = "БЫСТРЫЙ"
                reasoning = f"Быстрый темп игры: {total_goals} голов за {minute} минут"
            else:
                # Медленный темп: голы меньше минут
                recommendation_value = predicted_total + 3
                recommendation = f"ТМ {recommendation_value}"
                tempo = "МЕДЛЕННЫЙ"
                reasoning = f"Медленный темп игры: {total_goals} голов за {minute} минут"
            
            result = {
                'match': f"{match.team1} vs {match.team2}",
                'current_score': match.score,
                'minute': minute,
                'total_goals': total_goals,
                'second_half_minute': second_half_minute,
                'predicted_total': predicted_total,
                'predicted_total_float': predicted_total_float,
                'recommendation': recommendation,
                'recommendation_value': recommendation_value,
                'tempo': tempo,
                'reasoning': reasoning,
                'goals_per_minute': total_goals / minute if minute > 0 else 0
            }
            
            self.logger.info(f"📊 Тотал для {match.team1} vs {match.team2}: {recommendation} (темп: {tempo})")
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка расчета тоталов для {match.team1} vs {match.team2}: {e}")
            return {}
    
    def create_totals_recommendation(self, match: MatchData, totals_data: Dict) -> Optional[MatchData]:
        """Создает рекомендацию по тоталам"""
        if not totals_data:
            return None
        
        try:
            # Создаем рекомендацию по тоталам
            recommendation = MatchData(
                sport='handball',
                team1=match.team1,
                team2=match.team2,
                score=match.score,
                minute=getattr(match, 'minute', ''),
                league=getattr(match, 'league', ''),
                link=getattr(match, 'link', ''),
                source=getattr(match, 'source', 'totals_calculator')
            )
            
            # Настраиваем рекомендацию
            recommendation.recommendation_type = 'total'
            recommendation.recommendation_value = totals_data['recommendation']
            recommendation.probability = self._calculate_totals_confidence(totals_data)
            recommendation.justification = self._generate_totals_reasoning(totals_data)
            
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Ошибка создания рекомендации по тоталам: {e}")
            return None
    
    def _calculate_totals_confidence(self, totals_data: Dict) -> float:
        """Рассчитывает уверенность в рекомендации по тоталам"""
        try:
            goals_per_minute = totals_data.get('goals_per_minute', 0)
            minute = totals_data.get('minute', 0)
            tempo = totals_data.get('tempo', 'НЕЙТРАЛЬНЫЙ')
            
            base_confidence = 75.0  # Базовая уверенность
            
            # Бонус за четкий темп
            if tempo == "БЫСТРЫЙ" and goals_per_minute > 1.2:
                base_confidence += 10
            elif tempo == "МЕДЛЕННЫЙ" and goals_per_minute < 0.8:
                base_confidence += 10
            
            # Бонус за время матча (чем больше времени, тем надежнее)
            if minute > 50:
                base_confidence += 5
            elif minute > 40:
                base_confidence += 3
            
            # Бонус за экстремальные значения
            if goals_per_minute > 1.5 or goals_per_minute < 0.6:
                base_confidence += 5
            
            return min(base_confidence, 95.0)
            
        except Exception:
            return 75.0
    
    def _generate_totals_reasoning(self, totals_data: Dict) -> str:
        """Генерирует обоснование для рекомендации по тоталам"""
        try:
            match = totals_data.get('match', '')
            score = totals_data.get('current_score', '')
            minute = totals_data.get('minute', 0)
            total_goals = totals_data.get('total_goals', 0)
            tempo = totals_data.get('tempo', '')
            predicted_total = totals_data.get('predicted_total', 0)
            recommendation = totals_data.get('recommendation', '')
            
            reasoning = f"В матче {match} забито {total_goals} голов за {minute} минут. "
            reasoning += f"{tempo} темп игры указывает на прогнозируемый тотал {predicted_total}. "
            reasoning += f"Рекомендуется ставка {recommendation} на основе текущей динамики."
            
            return reasoning
            
        except Exception as e:
            return f"Расчет тоталов на основе текущего темпа игры: {totals_data.get('reasoning', '')}"

# Глобальный экземпляр калькулятора
totals_calculator = TotalsCalculator()