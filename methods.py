# Тут должны быть все функции для запросов 
import requests
from telegram import BotCommand, InlineKeyboardButton
from config import USERS_WHITELIST


# Возможно как врапер или просто функция, для проверки пользователя на доступ к боту по chat_id
def check_if_user_in_whitelist(user_id: int) -> bool:
    """
    Проверяет, есть ли пользователь в whitelist
    
    Args:
        user_id (int): ID пользователя в Telegram
        
    Returns:
        bool: True если пользователь в whitelist, False иначе
    """
    # Если whitelist пустой, разрешаем всем
    if not USERS_WHITELIST or not any(USERS_WHITELIST):
        return True
    
    return str(user_id) in USERS_WHITELIST


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
        BotCommand("menu", "🏠 Главное меню")
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
            "version": "4.x",
            "developer": "HoYoverse",
            "last_update": "В разработке"
        },
        "hsr": {
            "name": "Honkai: Star Rail",
            "emoji": "🚀",
            "status": "Активная игра",
            "version": "2.x",
            "developer": "HoYoverse",
            "last_update": "В разработке"
        },
        "zzz": {
            "name": "Zenless Zone Zero",
            "emoji": "⚡",
            "status": "В разработке",
            "version": "Beta",
            "developer": "HoYoverse",
            "last_update": "В разработке"
        },
        "wuwa": {
            "name": "Wuthering Waves",
            "emoji": "🌊",
            "status": "В разработке",
            "version": "Beta",
            "developer": "Kuro Games",
            "last_update": "В разработке"
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
    # Заглушка - в будущем здесь будет парсинг данных
    banner_info = {
        "genshin": {
            "character_banner": "Информация будет добавлена позже",
            "weapon_banner": "Информация будет добавлена позже",
            "last_update": "В разработке"
        },
        "hsr": {
            "character_banner": "Информация будет добавлена позже",
            "light_cone_banner": "Информация будет добавлена позже",
            "last_update": "В разработке"
        },
        "zzz": {
            "character_banner": "Информация будет добавлена позже",
            "weapon_banner": "Информация будет добавлена позже",
            "last_update": "В разработке"
        },
        "wuwa": {
            "character_banner": "Информация будет добавлена позже",
            "weapon_banner": "Информация будет добавлена позже",
            "last_update": "В разработке"
        }
    }
    
    return banner_info.get(game_name, {})


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
    
    message = f"{emoji} Текущие баннеры {name}\n\n"
    
    for banner_type, banner_info in banner_data.items():
        if banner_type != "last_update":
            message += f"📋 {banner_type.replace('_', ' ').title()}: {banner_info}\n"
    
    message += f"\n🔄 Последнее обновление: {banner_data.get('last_update', 'Неизвестно')}"
    
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

