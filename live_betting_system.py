"""
Полная система live-анализа ставок с циклическим запуском
"""

import requests
import time
import json
import schedule
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import logging
from datetime import datetime
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_betting.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class MatchData:
    """Структура данных о матче"""
    team1: str
    team2: str
    score: str
    minute: str
    coefficient: float
    is_locked: bool
    sport_type: str
    league: str = ""
    url: str = ""
    status: str = ""


class LiveBettingSystem:
    """Полная система live-анализа ставок"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        # URL-адреса
        self.urls = {
            'scores24': {
                'football': 'https://scores24.live/ru/soccer?matchesFilter=live',
                'tennis': 'https://scores24.live/ru/tennis?matchesFilter=live',
                'table_tennis': 'https://scores24.live/ru/table-tennis?matchesFilter=live',
                'handball': 'https://scores24.live/ru/handball?matchesFilter=live'
            }
        }
        
        # Настройки
        self.cycle_interval = 50  # минут
        self.min_probability = 80  # минимальная вероятность для рекомендации
        
    def get_page_content(self, url: str, timeout: int = 30) -> Optional[str]:
        """Получение содержимого страницы"""
        try:
            logger.info(f"Запрос к: {url}")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            if response.encoding == 'ISO-8859-1':
                response.encoding = 'utf-8'
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка HTTP запроса к {url}: {e}")
            return None
    
    def parse_scores24_matches(self, html: str, sport_type: str) -> List[MatchData]:
        """Парсинг матчей с Scores24.live"""
        if not html:
            return []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            matches = []
            
            # Ищем контейнеры матчей
            match_containers = soup.select('.sc-17qxh4e-0.dHxDFU')
            
            for container in match_containers:
                match_data = self._extract_scores24_match(container, sport_type)
                if match_data:
                    matches.append(match_data)
            
            return matches
            
        except Exception as e:
            logger.error(f"Ошибка парсинга Scores24: {e}")
            return []
    
    def _extract_scores24_match(self, container, sport_type: str) -> Optional[MatchData]:
        """Извлечение данных матча из контейнера Scores24"""
        try:
            # Названия команд
            team_elements = container.select('.sc-17qxh4e-10.esbhnW')
            if len(team_elements) < 2:
                return None
            
            team1 = team_elements[0].get_text(strip=True)
            team2 = team_elements[1].get_text(strip=True)
            
            # Счет
            score = ""
            score_elements = container.select('.sc-pvs6fr-1.bAhpay')
            if len(score_elements) >= 2:
                score = f"{score_elements[0].get_text(strip=True)}:{score_elements[1].get_text(strip=True)}"
            
            # Минута/статус
            minute = ""
            status = ""
            
            minute_elements = [
                container.select_one('.sc-1p31vt4-0.ghrzJz'),
                container.select_one('.sc-w3d8cd-0.iLWJDQ'),
                container.select_one('.sc-oh2bsf-0.fUZLA span')
            ]
            
            for elem in minute_elements:
                if elem:
                    text = elem.get_text(strip=True)
                    if text and ('\'' in text or 'минут' in text or 'сет' in text or 'партия' in text):
                        minute = text
                        status = text
                        break
            
            # Лига
            league = ""
            league_element = container.select_one('.sc-5a92rz-5.knTRcb')
            if league_element:
                league = league_element.get_text(strip=True)
            
            # URL матча
            url = ""
            url_element = container.select_one('a[href*="/soccer/m-"], a[href*="/tennis/m-"], a[href*="/table-tennis/m-"], a[href*="/handball/m-"]')
            if url_element:
                url = urljoin("https://scores24.live", url_element.get('href', ''))
            
            return MatchData(
                team1=team1,
                team2=team2,
                score=score,
                minute=minute,
                coefficient=0.0,
                is_locked=False,
                sport_type=sport_type,
                league=league,
                url=url,
                status=status
            )
            
        except Exception as e:
            logger.error(f"Ошибка извлечения данных матча Scores24: {e}")
            return None
    
    def get_live_matches(self, site: str, sport_type: str) -> List[MatchData]:
        """Получение live-матчей с сайта"""
        url = self.urls.get(site, {}).get(sport_type)
        if not url:
            return []
        
        html = self.get_page_content(url)
        if not html:
            return []
        
        if site == 'scores24':
            matches = self.parse_scores24_matches(html, sport_type)
        else:
            matches = []
        
        return matches
    
    def analyze_football_matches(self) -> List[Dict]:
        """Анализ футбольных матчей для рекомендаций"""
        matches = self.get_live_matches('scores24', 'football')
        recommendations = []
        
        for match in matches:
            if ':' in match.score and match.score != '0:0':
                home_score, away_score = match.score.split(':')
                try:
                    home_score = int(home_score.strip())
                    away_score = int(away_score.strip())
                    
                    if home_score > away_score:
                        leader = match.team1
                        leader_score = home_score
                        follower = match.team2
                        follower_score = away_score
                        bet_type = "П1"
                    elif away_score > home_score:
                        leader = match.team2
                        leader_score = away_score
                        follower = match.team1
                        follower_score = home_score
                        bet_type = "П2"
                    else:
                        continue
                    
                    score_difference = abs(leader_score - follower_score)
                    minute_num = 0
                    
                    if match.minute and '\'' in match.minute:
                        try:
                            minute_num = int(match.minute.replace('\'', ''))
                        except:
                            pass
                    
                    if score_difference >= 1 and minute_num >= 60:
                        probability = min(85, 70 + score_difference * 5 + (minute_num - 60) * 0.5)
                        
                        if probability >= self.min_probability:
                            recommendation = {
                                'match': match,
                                'leader': leader,
                                'follower': follower,
                                'score': match.score,
                                'minute': match.minute,
                                'bet_type': bet_type,
                                'coefficient': 1.5,
                                'probability': probability,
                                'reasoning': f"Лидер ведет {score_difference} мячом на {minute_num}-й минуте"
                            }
                            recommendations.append(recommendation)
                
                except (ValueError, AttributeError):
                    continue
        
        return recommendations
    
    def analyze_tennis_matches(self) -> List[Dict]:
        """Анализ теннисных матчей для рекомендаций"""
        matches = self.get_live_matches('scores24', 'tennis')
        recommendations = []
        
        for match in matches:
            if ':' in match.score:
                home_sets, away_sets = match.score.split(':')
                try:
                    home_sets = int(home_sets.strip())
                    away_sets = int(away_sets.strip())
                    
                    if home_sets > away_sets:
                        leader = match.team1
                        leader_sets = home_sets
                        follower = match.team2
                        follower_sets = away_sets
                    elif away_sets > home_sets:
                        leader = match.team2
                        leader_sets = away_sets
                        follower = match.team1
                        follower_sets = home_sets
                    else:
                        continue
                    
                    if leader_sets >= 1 and (leader_sets - follower_sets) >= 1:
                        probability = min(80, 60 + (leader_sets - follower_sets) * 15)
                        
                        if probability >= self.min_probability:
                            recommendation = {
                                'match': match,
                                'leader': leader,
                                'follower': follower,
                                'score': match.score,
                                'minute': match.minute,
                                'bet_type': f"Победа {leader}",
                                'coefficient': 1.8,
                                'probability': probability,
                                'reasoning': f"Лидер ведет {leader_sets}:{follower_sets} по сетам"
                            }
                            recommendations.append(recommendation)
                
                except (ValueError, AttributeError):
                    continue
        
        return recommendations
    
    def analyze_table_tennis_matches(self) -> List[Dict]:
        """Анализ матчей настольного тенниса для рекомендаций"""
        matches = self.get_live_matches('scores24', 'table_tennis')
        recommendations = []
        
        for match in matches:
            if ':' in match.score:
                home_sets, away_sets = match.score.split(':')
                try:
                    home_sets = int(home_sets.strip())
                    away_sets = int(away_sets.strip())
                    
                    if home_sets > away_sets:
                        leader = match.team1
                        leader_sets = home_sets
                        follower = match.team2
                        follower_sets = away_sets
                    elif away_sets > home_sets:
                        leader = match.team2
                        leader_sets = away_sets
                        follower = match.team1
                        follower_sets = home_sets
                    else:
                        continue
                    
                    if leader_sets >= 1 and (leader_sets - follower_sets) >= 1:
                        probability = min(80, 60 + (leader_sets - follower_sets) * 15)
                        
                        if probability >= self.min_probability:
                            recommendation = {
                                'match': match,
                                'leader': leader,
                                'follower': follower,
                                'score': match.score,
                                'minute': match.minute,
                                'bet_type': f"Победа {leader}",
                                'coefficient': 1.7,
                                'probability': probability,
                                'reasoning': f"Лидер ведет {leader_sets}:{follower_sets} по партиям"
                            }
                            recommendations.append(recommendation)
                
                except (ValueError, AttributeError):
                    continue
        
        return recommendations
    
    def generate_telegram_report(self) -> str:
        """Генерация отчета для Telegram"""
        now = datetime.now()
        time_str = now.strftime("%H:%M МСК, %d.%m.%Y")
        
        # Собираем рекомендации
        football_recs = self.analyze_football_matches()
        tennis_recs = self.analyze_tennis_matches()
        table_tennis_recs = self.analyze_table_tennis_matches()
        
        # Генерируем отчет
        report = f"""<b>🎯 LIVE-ПРЕДЛОЖЕНИЯ НА </b>(<i>{time_str}</i>)<b> 🎯</b>

<b>—————————————</b>
<b>⚽ ФУТБОЛ ⚽</b>
<b>—————————————</b>
"""
        
        if football_recs:
            for i, rec in enumerate(football_recs[:5], 1):
                report += f"""
<b>⚽ {rec['leader']} – {rec['follower']}</b>
🏟️ Счет: <b>{rec['score']}</b> ({rec['minute']})
✅ Ставка: <b>{rec['bet_type']}</b>
📊 Кэф: <b>{rec['coefficient']}</b>
📌 <i>{rec['reasoning']}</i>
"""
        else:
            report += "\n<i>Нет подходящих матчей</i>\n"
        
        report += """
<b>—————————————</b>
<b>🎾 ТЕННИС 🎾</b>
<b>—————————————</b>
"""
        
        if tennis_recs:
            for i, rec in enumerate(tennis_recs[:5], 1):
                report += f"""
<b>🎾 {rec['leader']} – {rec['follower']}</b>
🎯 Счет: <b>{rec['score']}</b> ({rec['minute']})
✅ Ставка: <b>{rec['bet_type']}</b>
📊 Кэф: <b>{rec['coefficient']}</b>
📌 <i>{rec['reasoning']}</i>
"""
        else:
            report += "\n<i>Нет подходящих матчей</i>\n"
        
        report += """
<b>—————————————</b>
<b>🏓 НАСТ. ТЕННИС 🏓</b>
<b>—————————————</b>
"""
        
        if table_tennis_recs:
            for i, rec in enumerate(table_tennis_recs[:5], 1):
                report += f"""
<b>🏓 {rec['leader']} – {rec['follower']}</b>
🎯 Счет: <b>{rec['score']}</b> ({rec['minute']})
✅ Ставка: <b>{rec['bet_type']}</b>
📊 Кэф: <b>{rec['coefficient']}</b>
📌 <i>{rec['reasoning']}</i>
"""
        else:
            report += "\n<i>Нет подходящих матчей</i>\n"
        
        report += """
<b>—————————————</b>
<b>🤾 ГАНДБОЛ 🤾</b>
<b>—————————————</b>

<i>Нет подходящих матчей</i>

<b>——————————————————</b>
<b>💎 TrueLiveBet – Мы всегда на Вашей стороне! 💎</b>
"""
        
        return report
    
    def save_report(self, report: str) -> str:
        """Сохранение отчета в файл"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"live_report_{timestamp}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return filename
    
    def run_analysis_cycle(self):
        """Запуск одного цикла анализа"""
        logger.info("=" * 60)
        logger.info("ЗАПУСК ЦИКЛА АНАЛИЗА")
        logger.info("=" * 60)
        
        try:
            # Генерируем отчет
            report = self.generate_telegram_report()
            
            # Сохраняем отчет
            filename = self.save_report(report)
            
            logger.info(f"✅ Отчет сгенерирован: {filename}")
            logger.info(f"📊 Размер отчета: {len(report)} символов")
            
            # Выводим краткую статистику
            football_recs = self.analyze_football_matches()
            tennis_recs = self.analyze_tennis_matches()
            table_tennis_recs = self.analyze_table_tennis_matches()
            
            logger.info(f"📈 Статистика рекомендаций:")
            logger.info(f"   ⚽ Футбол: {len(football_recs)}")
            logger.info(f"   🎾 Теннис: {len(tennis_recs)}")
            logger.info(f"   🏓 Наст. теннис: {len(table_tennis_recs)}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка в цикле анализа: {e}")
    
    def start_continuous_analysis(self):
        """Запуск непрерывного анализа"""
        logger.info("🚀 Запуск системы непрерывного анализа")
        logger.info(f"⏰ Интервал: {self.cycle_interval} минут")
        logger.info(f"🎯 Минимальная вероятность: {self.min_probability}%")
        
        # Планируем выполнение каждые 50 минут
        schedule.every(self.cycle_interval).minutes.do(self.run_analysis_cycle)
        
        # Запускаем первый анализ сразу
        self.run_analysis_cycle()
        
        # Основной цикл
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Проверяем каждую минуту
            except KeyboardInterrupt:
                logger.info("🛑 Остановка системы по запросу пользователя")
                break
            except Exception as e:
                logger.error(f"❌ Ошибка в основном цикле: {e}")
                time.sleep(60)
    
    def close(self):
        """Закрытие сессии"""
        self.session.close()


def main():
    """Основная функция"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'single':
        # Единичный анализ
        logger.info("🔍 Запуск единичного анализа")
        system = LiveBettingSystem()
        try:
            system.run_analysis_cycle()
        finally:
            system.close()
    
    elif len(sys.argv) > 1 and sys.argv[1] == 'continuous':
        # Непрерывный анализ
        logger.info("🔄 Запуск непрерывного анализа")
        system = LiveBettingSystem()
        try:
            system.start_continuous_analysis()
        finally:
            system.close()
    
    else:
        # По умолчанию - единичный анализ
        logger.info("🔍 Запуск единичного анализа (по умолчанию)")
        system = LiveBettingSystem()
        try:
            system.run_analysis_cycle()
        finally:
            system.close()


if __name__ == "__main__":
    main()