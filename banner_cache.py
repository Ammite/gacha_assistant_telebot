"""
Кеширование изображений баннеров
Использует хэш от JSON баннера как ключ для кеширования base64 изображений
"""

import os
import json
import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)

CACHE_DIR = "cache"

def ensure_cache_dir():
    """Создает директорию кеша если её нет"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
        logger.debug(f"Создана директория кеша: {CACHE_DIR}")

def get_banner_hash(banner_data: dict) -> str:
    """
    Создает хэш от данных баннера для использования как ключа кеша

    Args:
        banner_data (dict): Данные баннера

    Returns:
        str: SHA256 хэш
    """
    # Сериализуем данные баннера в отсортированную JSON строку
    banner_json = json.dumps(banner_data, sort_keys=True, ensure_ascii=False)
    # Создаем хэш
    hash_obj = hashlib.sha256(banner_json.encode('utf-8'))
    return hash_obj.hexdigest()

def get_cached_image(banner_hash: str) -> Optional[str]:
    """
    Получает изображение из кеша

    Args:
        banner_hash (str): Хэш баннера

    Returns:
        Optional[str]: base64 строка изображения или None если не найдено
    """
    ensure_cache_dir()
    cache_file = os.path.join(CACHE_DIR, f"{banner_hash}.txt")

    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                base64_data = f.read().strip()
                logger.debug(f"Изображение найдено в кеше: {banner_hash}")
                return base64_data
        except Exception as e:
            logger.error(f"Ошибка чтения из кеша {banner_hash}: {e}")

    logger.debug(f"Изображение не найдено в кеше: {banner_hash}")
    return None

def save_image_to_cache(banner_hash: str, base64_data: str) -> bool:
    """
    Сохраняет изображение в кеш

    Args:
        banner_hash (str): Хэш баннера
        base64_data (str): base64 строка изображения

    Returns:
        bool: True если сохранено успешно
    """
    ensure_cache_dir()
    cache_file = os.path.join(CACHE_DIR, f"{banner_hash}.txt")

    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(base64_data)
        logger.debug(f"Изображение сохранено в кеш: {banner_hash}")
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения в кеш {banner_hash}: {e}")
        return False

def get_or_create_banner_image(banner_data: dict, game_name: str) -> Optional[str]:
    """
    Получает изображение баннера из кеша или создает новое

    Args:
        banner_data (dict): Данные баннера
        game_name (str): Название игры

    Returns:
        Optional[str]: base64 строка изображения
    """
    from banner_card.creating_banner_card import make_banner_card_base64

    # Создаем хэш от данных баннера
    banner_hash = get_banner_hash(banner_data)
    logger.debug(f"Хэш баннера для {game_name}: {banner_hash}")

    # Проверяем кеш
    cached_image = get_cached_image(banner_hash)
    if cached_image:
        return cached_image

    # Создаем новое изображение
    logger.debug(f"Создание нового изображения для баннера {game_name}")
    try:
        base64_image = make_banner_card_base64(banner_data, game_name)
        if base64_image:
            # Сохраняем в кеш
            save_image_to_cache(banner_hash, base64_image)
            return base64_image
        else:
            logger.error(f"Не удалось создать изображение для баннера {game_name}")
            return None
    except Exception as e:
        logger.error(f"Ошибка создания изображения баннера {game_name}: {e}")
        return None

def clear_cache() -> int:
    """
    Очищает весь кеш изображений

    Returns:
        int: Количество удаленных файлов
    """
    ensure_cache_dir()
    deleted_count = 0

    try:
        for filename in os.listdir(CACHE_DIR):
            if filename.endswith('.txt'):
                file_path = os.path.join(CACHE_DIR, filename)
                os.remove(file_path)
                deleted_count += 1

        logger.info(f"Очищено {deleted_count} файлов из кеша")
        return deleted_count
    except Exception as e:
        logger.error(f"Ошибка очистки кеша: {e}")
        return 0

def get_cache_stats() -> dict:
    """
    Получает статистику кеша

    Returns:
        dict: Статистика кеша
    """
    ensure_cache_dir()

    try:
        files = [f for f in os.listdir(CACHE_DIR) if f.endswith('.txt')]
        total_size = 0

        for filename in files:
            file_path = os.path.join(CACHE_DIR, filename)
            total_size += os.path.getsize(file_path)

        return {
            "files_count": len(files),
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
    except Exception as e:
        logger.error(f"Ошибка получения статистики кеша: {e}")
        return {"files_count": 0, "total_size_mb": 0}
