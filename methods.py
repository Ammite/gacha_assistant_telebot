# Тут должны быть все функции для запросов 
from tkinter import NO
import requests
from telegram import BotCommand, InlineKeyboardButton
from whitelist_manager import whitelist_manager
from banner_manager import banner_manager
from banner_card.creating_banner_card import make_banner_card_base64
from io import BytesIO
import base64
from typing import List, Optional


# Возможно как врапер или просто функция, для проверки пользователя на доступ к боту по chat_id
def check_if_user_in_whitelist(user_id: int) -> bool:
    """
    Проверяет, есть ли пользователь в whitelist

    Args:
        user_id (int): ID пользователя в Telegram

    Returns:
        bool: True если пользователь в whitelist, False иначе
    """
    return whitelist_manager.is_user_allowed(str(user_id))


def send_inline_keyboard():
    """
    Создает inline клавиатуру, которая на сообщении
    Эта функция может быть использована для создания стандартных inline клавиатур
    """
    pass


def send_message():
    """
    Отправляет сообщение пользователю
    Эта функция может быть использована для отправки стандартных сообщений
    """
    pass


def send_keyboard():
    """
    Создает глобальную клавиатуру, которая как меню
    Эта функция может быть использована для создания стандартных клавиатур
    """
    pass


async def update_commands(bot):
    """
    Обновление доступных команд у пользователя
    
    Args:
        bot: Объект бота для обновления команд
    """
    commands = [
        BotCommand("start", "🚀 Запустить бота"),
        BotCommand("help", "🆘 Получить помощь"),
        BotCommand("menu", "🏠 Главное меню"),
        BotCommand("update_banners", "🔄 Обновить данные баннеров"),
        BotCommand("banner_status", "📊 Статус баннеров")
    ]
    
    try:
        await bot.set_my_commands(commands)
        print("✅ Команды бота успешно обновлены")
    except Exception as e:
        print(f"❌ Ошибка при обновлении команд: {e}")


def get_game_info(game_name: str) -> dict:
    """
    Получает информацию об игре
    
    Args:
        game_name (str): Название игры (genshin, hsr, zzz, wuwa)
        
    Returns:
        dict: Информация об игре
    """
    games_info = {
        "genshin": {
            "name": "Genshin Impact",
            "emoji": "🌟",
            "status": "Активная игра",
            "version": "6.x",
            "developer": "HoYoverse",
            "last_update": "В разработке",
            "promocode_link": "https://genshin.hoyoverse.com/ru/gift?code="
        },
        "hsr": {
            "name": "Honkai: Star Rail",
            "emoji": "🚀",
            "status": "Активная игра",
            "version": "3.x",
            "developer": "HoYoverse",
            "last_update": "В разработке",
            "promocode_link": "https://hsr.hoyoverse.com/gift?code="
        },
        "zzz": {
            "name": "Zenless Zone Zero",
            "emoji": "⚡",
            "status": "Активная игра",
            "version": "2.X",
            "developer": "HoYoverse",
            "last_update": "В разработке",
            "promocode_link": "https://zenless.hoyoverse.com/redemption?code="
        },
        "wuwa": {
            "name": "Wuthering Waves",
            "emoji": "🌊",
            "status": "Активная игра",
            "version": "Beta",
            "developer": "Kuro Games",
            "last_update": "В разработке",
            "promocode_link": None
        }
    }
    
    return games_info.get(game_name, {})


def get_banner_info(game_name: str) -> dict:
    """
    Получает информацию о текущих баннерах игры

    Args:
        game_name (str): Название игры

    Returns:
        dict: Информация о баннерах
    """
    import logging
    from datetime import datetime

    logger = logging.getLogger(__name__)

    logger.debug(f"get_banner_info вызвана для игры: {game_name}")

    try:
        current_banners, next_banners = banner_manager.get_current_banners(game_name)

        logger.debug(f"Получено баннеров для {game_name}: current={len(current_banners)}, next={len(next_banners)}")

        # Получаем текущую дату
        current_date = datetime.now().strftime("%d.%m.%Y")

        banner_info = {
            "current_banners": current_banners,
            "next_banners": next_banners,
            "has_current": len(current_banners) > 0,
            "has_next": len(next_banners) > 0,
            "last_update": "Актуально",
            "current_date": current_date
        }

        logger.debug(f"Результат для {game_name}: has_current={banner_info['has_current']}, has_next={banner_info['has_next']}")

        return banner_info

    except Exception as e:
        logger.error(f"Ошибка получения информации о баннерах для {game_name}: {e}")
        current_date = datetime.now().strftime("%d.%m.%Y")
        return {
            "current_banners": [],
            "next_banners": [],
            "has_current": False,
            "has_next": False,
            "last_update": "Ошибка загрузки",
            "current_date": current_date
        }


def get_useful_links(category: str) -> dict:
    """
    Получает полезные ссылки по категориям
    
    Args:
        category (str): Категория ссылок (stats, maps, guides, official)
        
    Returns:
        dict: Ссылки по категории
    """
    links = {
        "stats": {
            "name": "Статистика и трекеры",
            "emoji": "📊",
            "description": "Статистика по играм и персонажам",
            "links": "Ссылки будут добавлены позже"
        },
        "maps": {
            "name": "Интерактивные карты",
            "emoji": "🗺️",
            "description": "Локации, сундуки, материалы",
            "links": "Ссылки будут добавлены позже"
        },
        "guides": {
            "name": "Гайды и ресурсы",
            "emoji": "📚",
            "description": "Сборники, билды, советы",
            "links": "Ссылки будут добавлены позже"
        },
        "official": {
            "name": "Официальные сайты",
            "emoji": "🎮",
            "description": "Сайты разработчиков и сообществ",
            "links": "Ссылки будут добавлены позже"
        }
    }
    
    return links.get(category, {})


def format_banner_message(game_name: str, banner_data: dict) -> str:
    """
    Форматирует сообщение с информацией о баннерах
    
    Args:
        game_name (str): Название игры
        banner_data (dict): Данные о баннерах
        
    Returns:
        str: Отформатированное сообщение
    """
    game_info = get_game_info(game_name)
    emoji = game_info.get("emoji", "🎮")
    name = game_info.get("name", "Игра")
    current_date = banner_data.get("current_date", "Неизвестно")

    message = f"{emoji} Текущие баннеры {name}\n"
    message += f"📅 Сегодня: {current_date}\n\n"

    if not banner_data.get("has_current") and not banner_data.get("has_next"):
        message += "❌ Информация о баннерах недоступна\n"
        message += "Возможные причины:\n"
        message += "• Парсер не готов для этой игры\n"
        message += "• Нет данных о баннерах\n"
        message += "• Ошибка загрузки данных\n\n"
        message += f"🔄 Статус: {banner_data.get('last_update', 'Неизвестно')}"
        return message

    # Текущие баннеры
    if banner_data.get("has_current"):
        message += "🟢 <b>Текущие баннеры:</b>\n"
        for banner in banner_data["current_banners"]:
            version = banner.get("version", "?")
            phase = banner.get("phase", "?")
            dates = banner.get("dates", {})
            start_date = dates.get("start", "?")
            end_date = dates.get("end", "?")

            message += f"• {version} - {phase}\n"
            message += f"  📅 {start_date} → {end_date}\n"

            # 5★ персонажи
            featured_5 = banner.get("featured_5", [])
            if featured_5:
                char_names = []
                for char in featured_5:
                    if char.get("character_url"):
                        char_names.append(f'<a href="{char["character_url"]}">{char["name"]}</a>')
                    else:
                        char_names.append(char["name"])
                message += f"  ⭐ 5★: {', '.join(char_names)}\n"

            # 4★ персонажи (если есть)
            featured_4 = banner.get("featured_4", [])
            if featured_4:
                char_names = []
                for char in featured_4:
                    if char.get("character_url"):
                        char_names.append(f'<a href="{char["character_url"]}">{char["name"]}</a>')
                    else:
                        char_names.append(char["name"])
                message += f"  ⭐ 4★: {', '.join(char_names)}\n"

            message += "\n"
    else:
        message += "❌ Нет активных баннеров\n\n"

    # Следующие баннеры
    if banner_data.get("has_next"):
        message += "🔮 <b>Следующие баннеры:</b>\n"
        for banner in banner_data["next_banners"][:2]:  # Показываем только первые 2
            version = banner.get("version", "?")
            phase = banner.get("phase", "?")
            dates = banner.get("dates", {})
            start_date = dates.get("start", "?")
            end_date = dates.get("end", "?")

            message += f"• {version} - {phase}\n"
            message += f"  📅 {start_date} → {end_date}\n"

            # 5★ персонажи
            featured_5 = banner.get("featured_5", [])
            if featured_5:
                char_names = []
                for char in featured_5:
                    if char.get("character_url"):
                        char_names.append(f'<a href="{char["character_url"]}">{char["name"]}</a>')
                    else:
                        char_names.append(char["name"])
                message += f"  ⭐ 5★: {', '.join(char_names)}\n"

            # 4★ персонажи (если есть)
            featured_4 = banner.get("featured_4", [])
            if featured_4:
                char_names = []
                for char in featured_4:
                    if char.get("character_url"):
                        char_names.append(f'<a href="{char["character_url"]}">{char["name"]}</a>')
                    else:
                        char_names.append(char["name"])
                message += f"  ⭐ 4★: {', '.join(char_names)}\n"

            message += "\n"
    else:
        message += "❓ Информация о следующих баннерах пока недоступна\n\n"

    message += f"🔄 Последнее обновление: {banner_data.get('last_update', 'Неизвестно')}"

    return message

def format_promocodes_message(game_name: str, promocode_data: list) -> str:
    """
    Форматирует сообщение с информацией о баннерах
    
    Args:
        game_name (str): Название игры
        banner_data (dict): Данные о баннерах
        
    Returns:
        str: Отформатированное сообщение
    """
    game_info = get_game_info(game_name)
    emoji = game_info.get("emoji", "🎮")
    name = game_info.get("name", "Игра")
    promocode_redemption_links = game_info.get("promocode_link", None)

    if not promocode_redemption_links:
        message = "К сожалению, на данный момент данный функционал не доступен!"
        return message
    
    message = f"{emoji} Текущие промокоды {name}\n\n"
    
    for promocode_entity in promocode_data:
        promocode = promocode_entity.get("code", None)
        promocode_reward = promocode_entity.get("rewards", None)
        promocode_redemption_link = promocode_redemption_links + str(promocode)
        if not promocode:
            continue
        message += f"📋 <a href=\"{promocode_redemption_link}\">{promocode}</a> -> {promocode_reward}\n"
    return message

def format_game_message(game_name: str, game_data: dict) -> str:
    """
    Форматирует сообщение с информацией об игре
    
    Args:
        game_name (str): Название игры
        game_data (dict): Данные об игре
        
    Returns:
        str: Отформатированное сообщение
    """
    emoji = game_data.get("emoji", "🎮")
    name = game_data.get("name", "Игра")
    status = game_data.get("status", "Неизвестно")
    version = game_data.get("version", "Неизвестно")
    developer = game_data.get("developer", "Неизвестно")
    last_update = game_data.get("last_update", "Неизвестно")
    
    message = (
        f"{emoji} {name}\n\n"
        f"📅 Последнее обновление: {last_update}\n"
        f"🎯 Статус: {status}\n"
        f"📊 Версия: {version}\n"
        f"🏢 Разработчик: {developer}\n\n"
        f"ℹ️ Информация будет добавлена позже"
    )
    
    return message


def load_game_keyboard(game_name: str):
    """
    Загружает клавиатуру с ссылками для конкретной игры
    
    Args:
        game_name (str): Название игры (genshin, hsr, zzz, wuwa)
        
    Returns:
        list: Список кнопок для клавиатуры
    """
    try:
        if game_name == "genshin":
            from links.genshin.keyboard import keyboard
        elif game_name == "hsr":
            from links.hsr.keyboard import keyboard
        elif game_name == "zzz":
            from links.zzz.keyboard import keyboard
        elif game_name == "wuwa":
            from links.wuwa.keyboard import keyboard
        else:
            return []
        
        # Добавляем кнопку возврата в главное меню
        keyboard_with_back = keyboard + [[InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main")]]
        return keyboard_with_back
    except ImportError as e:
        print(f"❌ Ошибка загрузки клавиатуры для {game_name}: {e}")
        return []


def create_banner_card(game_name: str, banner_data: dict) -> Optional[BytesIO]:
    """
    Создает карточку баннера и возвращает её как BytesIO объект
    Использует кеширование изображений

    Args:
        game_name (str): Название игры
        banner_data (dict): Данные баннера

    Returns:
        Optional[BytesIO]: Объект изображения или None при ошибке
    """
    from banner_cache import get_or_create_banner_image
    import logging
    logger = logging.getLogger(__name__)

    try:
        # Получаем base64 строку из кеша или создаем новую
        img_base64 = get_or_create_banner_image(banner_data, game_name)

        if not img_base64:
            logger.error(f"Не удалось получить изображение баннера для {game_name}")
            return None

        # Конвертируем в BytesIO
        img_bytes = BytesIO(base64.b64decode(img_base64))
        logger.debug(f"Изображение баннера создано/получено из кеша для {game_name}")

        return img_bytes

    except Exception as e:
        logger.error(f"Ошибка создания карточки баннера для {game_name}: {e}")
        return None


def get_banner_cards_for_game(game_name: str) -> List[BytesIO]:
    """
    Получает карточки для всех текущих баннеров игры
    
    Args:
        game_name (str): Название игры
        
    Returns:
        List[BytesIO]: Список карточек баннеров
    """
    try:
        current_banners, next_banners = banner_manager.get_current_banners(game_name)
        cards = []
        
        # Создаем карточки для текущих баннеров
        for banner in current_banners:
            card = create_banner_card(game_name, banner)
            if card:
                cards.append(card)
        
        # Создаем карточки для следующих баннеров (максимум 2)
        for banner in next_banners[:2]:
            card = create_banner_card(game_name, banner)
            if card:
                cards.append(card)
        
        return cards
        
    except Exception as e:
        print(f"Ошибка получения карточек баннеров для {game_name}: {e}")
        return []

def create_media_group_from_cards(cards: List[BytesIO], game_name: str) -> List:
    """
    Создает медиа-группу из карточек баннеров
    
    Args:
        cards (List[BytesIO]): Список карточек баннеров
        game_name (str): Название игры
        
    Returns:
        List: Медиа-группа для отправки
    """
    from telegram import InputMediaPhoto
    
    media_group = []
    game_info = get_game_info(game_name)
    game_emoji = game_info.get("emoji", "🎮")
    
    for i, card in enumerate(cards):
        card.seek(0)  # Сбрасываем позицию в начало файла
        caption = f"{game_emoji} Карточка баннера {i+1}" if i == 0 else None
        media_group.append(InputMediaPhoto(media=card, caption=caption))
    
    return media_group


def make_api_request(url: str, method: str = "GET", data: dict = None, headers: dict = None):
    """
    Универсальная функция для выполнения API запросов
    
    Args:
        url (str): URL для запроса
        method (str): HTTP метод (GET, POST, PUT, DELETE)
        data (dict): Данные для отправки
        headers (dict): Заголовки запроса
        
    Returns:
        dict: Ответ от API или None в случае ошибки
    """
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Неподдерживаемый HTTP метод: {method}")
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка API запроса: {e}")
        return None
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return None


def add_to_whitelist(user_id: str) -> bool:
    """
    Добавляет пользователя в whitelist

    Args:
        user_id (str): ID пользователя для добавления

    Returns:
        bool: True если успешно добавлен, False иначе
    """
    return whitelist_manager.add_user(user_id)


def remove_from_whitelist(user_id: str) -> bool:
    """
    Удаляет пользователя из whitelist

    Args:
        user_id (str): ID пользователя для удаления

    Returns:
        bool: True если успешно удален, False иначе
    """
    return whitelist_manager.remove_user(user_id)


def get_whitelist_users() -> List[str]:
    """
    Получает список всех пользователей в whitelist

    Returns:
        List[str]: Список ID пользователей
    """
    return whitelist_manager.get_all_users()

