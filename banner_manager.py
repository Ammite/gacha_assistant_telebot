import os
import json
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class BannerManager:
    """Менеджер для управления баннерами игр"""
    
    def __init__(self):
        self.data_parsing_dir = "data_parsing"
        self.games = {
            "genshin": {
                "name": "Genshin Impact",
                "parser": "data_parsing/genshin/banner_history_parser.py",
                "data_file": "data_parsing/genshin/banners.json",
                "enabled": True
            },
            "hsr": {
                "name": "Honkai: Star Rail", 
                "parser": "data_parsing/hsr/banner_history_parser.py",
                "data_file": "data_parsing/hsr/banners.json",
                "enabled": True
            },
            "zzz": {
                "name": "Zenless Zone Zero",
                "parser": "data_parsing/zzz/banner_history_parser.py",
                "data_file": "data_parsing/zzz/banners.json",
                "enabled": True
            },
            "wuwa": {
                "name": "Wuthering Waves",
                "parser": "data_parsing/wuwa/banner_history_parser.py",
                "data_file": "data_parsing/wuwa/banners.json",
                "enabled": True
            }
        }
    
    def _get_file_modification_time(self, file_path: str) -> Optional[datetime]:
        """Получает время последнего изменения файла"""
        try:
            if os.path.exists(file_path):
                timestamp = os.path.getmtime(file_path)
                return datetime.fromtimestamp(timestamp)
        except Exception as e:
            logger.error(f"Ошибка получения времени файла {file_path}: {e}")
        return None
    
    def _is_data_outdated(self, file_path: str, max_age_days: int = 7) -> bool:
        """Проверяет, устарели ли данные (больше max_age_days дней)"""
        mod_time = self._get_file_modification_time(file_path)
        if not mod_time:
            return True
        
        age = datetime.now() - mod_time
        return age.days > max_age_days
    
    def _run_parser(self, parser_path: str) -> bool:
        """Запускает парсер для обновления данных"""
        try:
            logger.info(f"Запуск парсера: {parser_path}")
            result = subprocess.run(
                ["python", parser_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 минут таймаут
            )
            
            if result.returncode == 0:
                logger.info(f"Парсер {parser_path} выполнен успешно")
                return True
            else:
                logger.error(f"Ошибка парсера {parser_path}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Таймаут парсера {parser_path}")
            return False
        except Exception as e:
            logger.error(f"Ошибка запуска парсера {parser_path}: {e}")
            return False
    
    def _load_banner_data(self, file_path: str) -> List[Dict]:
        """Загружает данные баннеров из JSON файла"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"Файл {file_path} не найден")
                return []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
                
        except Exception as e:
            logger.error(f"Ошибка загрузки данных из {file_path}: {e}")
            return []
    
    def update_game_data(self, game_key: str) -> bool:
        """Обновляет данные для конкретной игры"""
        if game_key not in self.games:
            logger.error(f"Неизвестная игра: {game_key}")
            return False
        
        game_info = self.games[game_key]
        if not game_info["enabled"]:
            logger.info(f"Игра {game_key} отключена")
            return False
        
        parser_path = game_info["parser"]
        data_file = game_info["data_file"]
        
        # Проверяем, нужно ли обновлять данные
        if not self._is_data_outdated(data_file):
            logger.info(f"Данные для {game_key} актуальны")
            return True
        
        logger.info(f"Обновление данных для {game_key}")
        
        # Запускаем парсер
        if self._run_parser(parser_path):
            logger.info(f"Данные для {game_key} успешно обновлены")
            return True
        else:
            logger.error(f"Не удалось обновить данные для {game_key}")
            return False
    
    def get_current_banners(self, game_key: str) -> Tuple[List[Dict], List[Dict]]:
        """
        Получает текущие и следующие баннеры для игры

        Returns:
            Tuple[List[Dict], List[Dict]]: (текущие_баннеры, следующие_баннеры)
        """
        logger.debug(f"get_current_banners вызвана для игры: {game_key}")

        if game_key not in self.games:
            logger.error(f"Неизвестная игра: {game_key}")
            return [], []

        game_info = self.games[game_key]
        logger.debug(f"Информация об игре {game_key}: enabled={game_info['enabled']}, data_file={game_info['data_file']}")

        if not game_info["enabled"]:
            logger.info(f"Игра {game_key} отключена")
            return [], []
        
        # Обновляем данные если нужно
        self.update_game_data(game_key)
        
        # Загружаем данные
        banners = self._load_banner_data(game_info["data_file"])
        logger.debug(f"Загружено {len(banners)} баннеров для {game_key}")

        if not banners:
            logger.warning(f"Нет данных баннеров для {game_key}")
            return [], []

        current_date = datetime.now().date()
        logger.debug(f"Текущая дата: {current_date}")
        current_banners = []
        next_banners = []
        
        for i, banner in enumerate(banners):
            dates = banner.get("dates", {})
            start_date_str = dates.get("start")
            end_date_str = dates.get("end")

            logger.debug(f"Баннер {i+1}: версия {banner.get('version')}, даты {start_date_str} - {end_date_str}")

            if not start_date_str:
                logger.debug(f"Баннер {i+1}: пропускаем из-за отсутствия даты начала")
                continue

            try:
                start_date = datetime.fromisoformat(start_date_str).date()
                end_date = None
                if end_date_str:
                    end_date = datetime.fromisoformat(end_date_str).date()

                logger.debug(f"Баннер {i+1}: преобразованные даты {start_date} - {end_date}")

                # Проверяем, активен ли баннер сейчас
                if end_date and start_date <= current_date <= end_date:
                    logger.debug(f"Баннер {i+1}: ДОБАВЛЕН в текущие баннеры")
                    current_banners.append(banner)
                # Проверяем, является ли баннер следующим (если нет конечной даты или она не истекла)
                elif start_date > current_date:
                    logger.debug(f"Баннер {i+1}: ДОБАВЛЕН в следующие баннеры")
                    next_banners.append(banner)
                else:
                    logger.debug(f"Баннер {i+1}: ПРОПУЩЕН (прошедший баннер)")

            except ValueError as e:
                logger.error(f"Ошибка парсинга дат в баннере {i+1}: {e}")
                continue
        
        # Сортируем следующие баннеры по дате начала
        next_banners.sort(key=lambda x: x.get("dates", {}).get("start", ""))
        logger.debug(f"Итого: {len(current_banners)} текущих баннеров, {len(next_banners)} следующих баннеров")

        return current_banners, next_banners
    
    def get_all_games_status(self) -> Dict[str, Dict]:
        """Получает статус всех игр"""
        status = {}
        
        for game_key, game_info in self.games.items():
            data_file = game_info["data_file"]
            mod_time = self._get_file_modification_time(data_file)
            is_outdated = self._is_data_outdated(data_file)
            
            status[game_key] = {
                "name": game_info["name"],
                "enabled": game_info["enabled"],
                "has_data": os.path.exists(data_file),
                "last_update": mod_time.isoformat() if mod_time else None,
                "is_outdated": is_outdated,
                "data_file": data_file
            }
        
        return status
    
    def force_update_all(self) -> Dict[str, bool]:
        """Принудительно обновляет данные для всех игр"""
        results = {}
        
        for game_key in self.games:
            if self.games[game_key]["enabled"]:
                results[game_key] = self.update_game_data(game_key)
            else:
                results[game_key] = False
        
        return results


# Глобальный экземпляр менеджера
banner_manager = BannerManager()
