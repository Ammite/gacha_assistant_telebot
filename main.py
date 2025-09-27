import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ChatAction
from config import TELEGRAM_BOT_TOKEN, ADMIN_ID
from methods import (
    check_if_user_in_whitelist, send_inline_keyboard, send_message, send_keyboard, update_commands,
    get_game_info, get_banner_info, get_useful_links, format_game_message, format_banner_message, format_promocodes_message, load_game_keyboard,
    get_banner_cards_for_game, create_media_group_from_cards,
    add_to_whitelist, remove_from_whitelist, get_whitelist_users
)
from banner_manager import banner_manager
from promocodes.parsing import get_promocodes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Создание главного меню
def get_main_menu():
    """Создает главное меню бота с играми"""
    keyboard = [
        [KeyboardButton("🌟 Genshin"), KeyboardButton("🚀 HSR")],
        [KeyboardButton("⚡ ZZZ"), KeyboardButton("🌊 WuWa")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)



# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    
    # Проверяем, есть ли пользователь в whitelist
    if not check_if_user_in_whitelist(user_id):
        await update.message.reply_text(
            "❌ Извините, у вас нет доступа к этому боту.\n"
            "Обратитесь к администратору для получения доступа."
        )
        return
    
    welcome_text = (
        "🎮 Добро пожаловать в Gaming Info Bot!\n\n"
        "Выберите игру из меню ниже для получения информации:\n"
        "• Текущие баннеры и события\n"
        "• Полезные ссылки и ресурсы\n"
        "• Статистика и гайды\n\n"
        "📋 Доступные команды:\n"
        "/start - Запуск бота\n"
        "/help - Помощь"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu()
    )
    
    # Обновляем команды бота
    await update_commands(context.bot)

# Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = (
        "🆘 Помощь по использованию бота\n\n"
        "Выберите игру из главного меню:\n"
        "🌟 Genshin Impact\n"
        "🚀 Honkai: Star Rail\n"
        "⚡ Zenless Zone Zero\n"
        "🌊 Wuthering Waves\n\n"
        "Для каждой игры доступно:\n"
        "• ℹ️ Информация об игре\n"
        "• 📋 Текущие баннеры (с карточками)\n"
        "• 🔗 Полезные ссылки\n"
        "• 📊 Статистика\n\n"
        "📋 Доступные команды:\n"
        "/start - Запуск бота\n"
        "/help - Помощь\n"
        "/menu - Главное меню\n"
        "/update_banners - Обновить данные баннеров\n"
        "/banner_status - Статус баннеров\n"
        "/clear_cache - Очистить кеш изображений\n"
        "/cache_stats - Статистика кеша\n"
        "/update_commands - Обновить команды бота\n\n"
        "👑 Команды управления whitelist (только для владельца):\n"
        "/add_to_whitelist <id> - Добавить пользователя в whitelist\n"
        "/remove_from_whitelist <id> - Удалить пользователя из whitelist\n"
        "/show_whitelist - Показать список пользователей\n\n"
        "💡 Совет: Используйте кнопки меню для удобной навигации!"
    )
    
    await update.message.reply_text(help_text)

# Обработчик команды /update_banners
async def update_banners_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /update_banners - принудительное обновление данных баннеров"""
    user_id = update.effective_user.id
    
    # Проверяем, есть ли пользователь в whitelist
    if not check_if_user_in_whitelist(user_id):
        await update.message.reply_text(
            "❌ Извините, у вас нет доступа к этому боту.\n"
            "Обратитесь к администратору для получения доступа."
        )
        return
    
    await update.message.reply_text("🔄 Начинаю обновление данных баннеров...")
    
    try:
        results = banner_manager.force_update_all()
        
        message = "📊 Результаты обновления:\n\n"
        for game_key, success in results.items():
            game_info = banner_manager.games[game_key]
            status = "✅ Успешно" if success else "❌ Ошибка"
            enabled_status = "🟢 Включена" if game_info["enabled"] else "🔴 Отключена"
            message += f"• {game_info['name']}: {status} ({enabled_status})\n"
        
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Ошибка обновления баннеров: {e}")
        await update.message.reply_text("❌ Произошла ошибка при обновлении данных баннеров")


# Обработчик команды /banner_status
async def banner_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /banner_status - статус всех игр"""
    user_id = update.effective_user.id
    
    # Проверяем, есть ли пользователь в whitelist
    if not check_if_user_in_whitelist(user_id):
        await update.message.reply_text(
            "❌ Извините, у вас нет доступа к этому боту.\n"
            "Обратитесь к администратору для получения доступа."
        )
        return
    
    try:
        status = banner_manager.get_all_games_status()
        
        message = "📊 Статус баннеров по играм:\n\n"
        for game_key, game_status in status.items():
            name = game_status["name"]
            enabled = "🟢 Включена" if game_status["enabled"] else "🔴 Отключена"
            has_data = "📁 Есть данные" if game_status["has_data"] else "❌ Нет данных"
            outdated = "⚠️ Устарели" if game_status["is_outdated"] else "✅ Актуальны"
            last_update = game_status["last_update"][:10] if game_status["last_update"] else "Никогда"
            
            message += f"🎮 **{name}**\n"
            message += f"  Статус: {enabled}\n"
            message += f"  Данные: {has_data}\n"
            message += f"  Актуальность: {outdated}\n"
            message += f"  Последнее обновление: {last_update}\n\n"
        
        await update.message.reply_text(message, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Ошибка получения статуса баннеров: {e}")
        await update.message.reply_text("❌ Произошла ошибка при получении статуса баннеров")

async def clear_cache_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /clear_cache - очистка кеша изображений"""
    user_id = update.effective_user.id

    # Проверяем, есть ли пользователь в whitelist
    if not check_if_user_in_whitelist(user_id):
        await update.message.reply_text(
            "❌ Извините, у вас нет доступа к этому боту.\n"
            "Обратитесь к администратору для получения доступа."
        )
        return

    await update.message.reply_text("🧹 Очищаю кеш изображений...")

    try:
        from banner_cache import clear_cache
        deleted_count = clear_cache()

        if deleted_count > 0:
            await update.message.reply_text(f"✅ Кеш очищен! Удалено {deleted_count} файлов.")
        else:
            await update.message.reply_text("ℹ️ Кеш уже пуст или не найден.")

    except Exception as e:
        logger.error(f"Ошибка очистки кеша: {e}")
        await update.message.reply_text("❌ Ошибка очистки кеша изображений")

async def cache_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /cache_stats - статистика кеша"""
    user_id = update.effective_user.id

    # Проверяем, есть ли пользователь в whitelist
    if not check_if_user_in_whitelist(user_id):
        await update.message.reply_text(
            "❌ Извините, у вас нет доступа к этому боту.\n"
            "Обратитесь к администратору для получения доступа."
        )
        return

    try:
        from banner_cache import get_cache_stats
        stats = get_cache_stats()

        message = "📊 Статистика кеша изображений:\n\n"
        message += f"📁 Количество файлов: {stats['files_count']}\n"
        message += f"💾 Общий размер: {stats['total_size_mb']} МБ\n\n"

        if stats['files_count'] > 0:
            message += "💡 Кеш содержит изображения баннеров для быстрой загрузки."
        else:
            message += "📭 Кеш пуст."

        await update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Ошибка получения статистики кеша: {e}")
        await update.message.reply_text("❌ Ошибка получения статистики кеша")

async def update_commands_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /update_commands - обновление команд бота в Telegram"""
    user_id = update.effective_user.id

    # Проверяем, есть ли пользователь в whitelist
    if not check_if_user_in_whitelist(user_id):
        await update.message.reply_text(
            "❌ Извините, у вас нет доступа к этому боту.\n"
            "Обратитесь к администратору для получения доступа."
        )
        return

    await update.message.reply_text("🔄 Обновляю команды бота в Telegram...")

    try:
        # Список команд для установки
        commands = [
            BotCommand("start", "Запуск бота"),
            BotCommand("help", "Помощь по использованию"),
            BotCommand("menu", "Показать главное меню"),
            BotCommand("update_banners", "Принудительное обновление баннеров"),
            BotCommand("banner_status", "Статус баннеров по играм"),
            BotCommand("clear_cache", "Очистить кеш изображений"),
            BotCommand("cache_stats", "Статистика кеша"),
            BotCommand("update_commands", "Обновить команды бота"),
            BotCommand("add_to_whitelist", "👑 Добавить пользователя в whitelist"),
            BotCommand("remove_from_whitelist", "👑 Удалить пользователя из whitelist"),
            BotCommand("show_whitelist", "👑 Показать список пользователей")
        ]

        # Устанавливаем команды через API
        await context.bot.set_my_commands(commands)

        await update.message.reply_text("✅ Команды бота успешно обновлены в Telegram!")

    except Exception as e:
        logger.error(f"Ошибка обновления команд: {e}")
        await update.message.reply_text("❌ Ошибка обновления команд бота")


# Обработчик команды /menu
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /menu"""
    await update.message.reply_text(
        "🏠 Главное меню",
        reply_markup=get_main_menu()
    )


# Обработчик команды /add_to_whitelist
async def add_to_whitelist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /add_to_whitelist"""
    user_id = update.effective_user.id

    # Проверяем, что команду выполняет только владелец бота
    if str(user_id) != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
        logger.warning(f"Пользователь {user_id} попытался добавить пользователя в whitelist")
        return

    # Проверяем аргументы команды
    if not context.args or len(context.args) != 1:
        await update.message.reply_text(
            "❌ Использование: /add_to_whitelist <user_id>\n"
            "Пример: /add_to_whitelist 123456789"
        )
        return

    target_user_id = context.args[0].strip()

    # Валидация ID
    if not target_user_id.isdigit():
        await update.message.reply_text("❌ ID пользователя должен содержать только цифры")
        return

    # Добавляем пользователя
    if add_to_whitelist(target_user_id):
        await update.message.reply_text(f"✅ Пользователь {target_user_id} добавлен в whitelist")
        logger.info(f"Пользователь {user_id} добавил {target_user_id} в whitelist")
    else:
        await update.message.reply_text(f"❌ Не удалось добавить пользователя {target_user_id} в whitelist")


# Обработчик команды /remove_from_whitelist
async def remove_from_whitelist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /remove_from_whitelist"""
    user_id = update.effective_user.id

    # Проверяем, что команду выполняет только владелец бота
    if str(user_id) != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
        logger.warning(f"Пользователь {user_id} попытался удалить пользователя из whitelist")
        return

    # Проверяем аргументы команды
    if not context.args or len(context.args) != 1:
        await update.message.reply_text(
            "❌ Использование: /remove_from_whitelist <user_id>\n"
            "Пример: /remove_from_whitelist 123456789"
        )
        return

    target_user_id = context.args[0].strip()

    # Валидация ID
    if not target_user_id.isdigit():
        await update.message.reply_text("❌ ID пользователя должен содержать только цифры")
        return

    # Удаляем пользователя
    if remove_from_whitelist(target_user_id):
        await update.message.reply_text(f"✅ Пользователь {target_user_id} удален из whitelist")
        logger.info(f"Пользователь {user_id} удалил {target_user_id} из whitelist")
    else:
        await update.message.reply_text(f"❌ Не удалось удалить пользователя {target_user_id} из whitelist")


# Обработчик команды /show_whitelist
async def show_whitelist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /show_whitelist"""
    user_id = update.effective_user.id

    # Проверяем, что команду выполняет только владелец бота
    if str(user_id) != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
        logger.warning(f"Пользователь {user_id} попытался просмотреть whitelist")
        return

    users = get_whitelist_users()

    if not users:
        await update.message.reply_text("📝 Whitelist пустой")
        return

    # Форматируем список пользователей
    user_list = "\n".join(f"• {user_id}" for user_id in sorted(users))
    message = f"📝 Пользователи в whitelist ({len(users)}):\n{user_list}"

    await update.message.reply_text(message)

# Обработчик текстовых сообщений
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    text = update.message.text
    
    if text == "🌟 Genshin":
        game_data = get_game_info("genshin")
        keyboard_buttons = load_game_keyboard("genshin")
        if keyboard_buttons:
            keyboard = InlineKeyboardMarkup(keyboard_buttons)
            message = f"{game_data['emoji']} Полезные ссылки для {game_data['name']}"
            await update.message.reply_text(message, reply_markup=keyboard)
        else:
            await update.message.reply_text("❌ Ошибка загрузки ссылок для Genshin Impact")
    elif text == "🚀 HSR":
        game_data = get_game_info("hsr")
        keyboard_buttons = load_game_keyboard("hsr")
        if keyboard_buttons:
            keyboard = InlineKeyboardMarkup(keyboard_buttons)
            message = f"{game_data['emoji']} Полезные ссылки для {game_data['name']}"
            await update.message.reply_text(message, reply_markup=keyboard)
        else:
            await update.message.reply_text("❌ Ошибка загрузки ссылок для Honkai: Star Rail")
    elif text == "⚡ ZZZ":
        game_data = get_game_info("zzz")
        keyboard_buttons = load_game_keyboard("zzz")
        if keyboard_buttons:
            keyboard = InlineKeyboardMarkup(keyboard_buttons)
            message = f"{game_data['emoji']} Полезные ссылки для {game_data['name']}"
            await update.message.reply_text(message, reply_markup=keyboard)
        else:
            await update.message.reply_text("❌ Ошибка загрузки ссылок для Zenless Zone Zero")
    elif text == "🌊 WuWa":
        game_data = get_game_info("wuwa")
        keyboard_buttons = load_game_keyboard("wuwa")
        if keyboard_buttons:
            keyboard = InlineKeyboardMarkup(keyboard_buttons)
            message = f"{game_data['emoji']} Полезные ссылки для {game_data['name']}"
            await update.message.reply_text(message, reply_markup=keyboard)
        else:
            await update.message.reply_text("❌ Ошибка загрузки ссылок для Wuthering Waves")
    else:
        await update.message.reply_text(
            "🤔 Не понимаю эту команду. Используйте кнопки меню!"
        )

# Обработчик inline кнопок
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на inline кнопки"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # Обработка информации об играх
    if data.startswith("info_"):
        game_name = data.replace("info_", "")
        game_data = get_game_info(game_name)
        message = format_game_message(game_name, game_data)
        await query.edit_message_text(message)
    
    # Обработка баннеров
    elif data.startswith("banners_"):
        game_name = data.replace("banners_", "")
        logger.debug(f"Обработка баннеров для игры: {game_name}")

        banner_data = get_banner_info(game_name)
        logger.debug(f"Данные баннеров для {game_name}: has_current={banner_data.get('has_current')}, has_next={banner_data.get('has_next')}")

        # Проверяем, есть ли баннеры для показа
        if not banner_data.get("has_current") and not banner_data.get("has_next"):
            logger.debug(f"Нет баннеров для показа для {game_name}")
            message = format_banner_message(game_name, banner_data)
            await query.edit_message_text(message)
        else:
            logger.debug(f"Есть баннеры для показа для {game_name}")
            # Показываем анимацию печати
            await query.message.chat.send_action(ChatAction.TYPING)

            try:
                # Сначала отправляем текстовое сообщение
                message = format_banner_message(game_name, banner_data)
                await query.message.reply_text(message, parse_mode="HTML", disable_web_page_preview=True)

                # Затем отправляем карточки баннеров
                cards = get_banner_cards_for_game(game_name)
                if cards:
                    # Создаем медиа-группу без текста
                    media_group = []
                    for card in cards:
                        card.seek(0)  # Сбрасываем позицию в начало файла
                        media_group.append(InputMediaPhoto(media=card))

                    # Отправляем медиа-группу
                    await query.message.reply_media_group(media=media_group)

            except Exception as e:
                logger.error(f"Ошибка отправки карточек баннеров: {e}")
                # Fallback на текстовое сообщение
                message = format_banner_message(game_name, banner_data)
                await query.message.reply_text(message, parse_mode="HTML", disable_web_page_preview=True)
    
    # Обработка ссылок
    elif data.startswith("links_"):
        game_name = data.replace("links_", "")
        game_data = get_game_info(game_name)
        keyboard_buttons = load_game_keyboard(game_name)
        if keyboard_buttons:
            keyboard = InlineKeyboardMarkup(keyboard_buttons)
            message = f"{game_data['emoji']} Полезные ссылки для {game_data['name']}"
            await query.edit_message_text(message, reply_markup=keyboard)
        else:
            await query.edit_message_text(f"❌ Ошибка загрузки ссылок для {game_data['name']}")
    
    # Обработка статистики
    elif data.startswith("stats_"):
        game_name = data.replace("stats_", "")
        game_data = get_game_info(game_name)
        message = f"{game_data['emoji']} Статистика для {game_data['name']}\n\n📊 Информация о статистике будет добавлена позже"
        await query.edit_message_text(message)
    
    # Обработка истории баннеров из клавиатур ссылок
    elif data == "genshin_banners":
        logger.debug("Обработка баннеров Genshin из клавиатуры ссылок")
        banner_data = get_banner_info("genshin")
        logger.debug(f"Данные баннеров Genshin: has_current={banner_data.get('has_current')}, has_next={banner_data.get('has_next')}")

        if not banner_data.get("has_current") and not banner_data.get("has_next"):
            message = format_banner_message("genshin", banner_data)
            await query.edit_message_text(message)
        else:
            # Показываем анимацию печати
            await query.message.chat.send_action(ChatAction.TYPING)

            try:
                # Сначала отправляем текстовое сообщение
                message = format_banner_message("genshin", banner_data)
                await query.message.reply_text(message, parse_mode="HTML", disable_web_page_preview=True)

                # Затем отправляем карточки баннеров
                cards = get_banner_cards_for_game("genshin")
                if cards:
                    # Создаем медиа-группу без текста
                    media_group = []
                    for card in cards:
                        card.seek(0)  # Сбрасываем позицию в начало файла
                        media_group.append(InputMediaPhoto(media=card))

                    # Отправляем медиа-группу
                    await query.message.reply_media_group(media=media_group)

            except Exception as e:
                logger.error(f"Ошибка отправки карточек баннеров Genshin: {e}")
                # Fallback на текстовое сообщение
                message = format_banner_message("genshin", banner_data)
                await query.message.reply_text(message, parse_mode="HTML", disable_web_page_preview=True)
                
    elif data == "hsr_banners":
        logger.debug("Обработка баннеров HSR из клавиатуры ссылок")
        banner_data = get_banner_info("hsr")
        logger.debug(f"Данные баннеров HSR: has_current={banner_data.get('has_current')}, has_next={banner_data.get('has_next')}")

        if not banner_data.get("has_current") and not banner_data.get("has_next"):
            message = format_banner_message("hsr", banner_data)
            await query.edit_message_text(message)
        else:
            # Показываем анимацию печати
            await query.message.chat.send_action(ChatAction.TYPING)

            try:
                # Сначала отправляем текстовое сообщение
                message = format_banner_message("hsr", banner_data)
                await query.message.reply_text(message, parse_mode="HTML", disable_web_page_preview=True)

                # Затем отправляем карточки баннеров
                cards = get_banner_cards_for_game("hsr")
                if cards:
                    # Создаем медиа-группу без текста
                    media_group = []
                    for card in cards:
                        card.seek(0)  # Сбрасываем позицию в начало файла
                        media_group.append(InputMediaPhoto(media=card))

                    # Отправляем медиа-группу
                    await query.message.reply_media_group(media=media_group)

            except Exception as e:
                logger.error(f"Ошибка отправки карточек баннеров HSR: {e}")
                # Fallback на текстовое сообщение
                message = format_banner_message("hsr", banner_data)
                await query.message.reply_text(message, parse_mode="HTML", disable_web_page_preview=True)
                
    elif data == "zzz_banners":
        logger.debug("Обработка баннеров ZZZ из клавиатуры ссылок")
        banner_data = get_banner_info("zzz")
        logger.debug(f"Данные баннеров ZZZ: has_current={banner_data.get('has_current')}, has_next={banner_data.get('has_next')}")

        if not banner_data.get("has_current") and not banner_data.get("has_next"):
            message = format_banner_message("zzz", banner_data)
            await query.edit_message_text(message)
        else:
            # Показываем анимацию печати
            await query.message.chat.send_action(ChatAction.TYPING)

            try:
                # Сначала отправляем текстовое сообщение
                message = format_banner_message("zzz", banner_data)
                await query.message.reply_text(message, parse_mode="HTML", disable_web_page_preview=True)

                # Затем отправляем карточки баннеров
                cards = get_banner_cards_for_game("zzz")
                if cards:
                    # Создаем медиа-группу без текста
                    media_group = []
                    for card in cards:
                        card.seek(0)  # Сбрасываем позицию в начало файла
                        media_group.append(InputMediaPhoto(media=card))

                    # Отправляем медиа-группу
                    await query.message.reply_media_group(media=media_group)

            except Exception as e:
                logger.error(f"Ошибка отправки карточек баннеров ZZZ: {e}")
                # Fallback на текстовое сообщение
                message = format_banner_message("zzz", banner_data)
                await query.message.reply_text(message, parse_mode="HTML", disable_web_page_preview=True)
    elif data == "wuwa_banners":
        logger.debug("Обработка баннеров WuWa из клавиатуры ссылок")
        banner_data = get_banner_info("wuwa")
        logger.debug(f"Данные баннеров WuWa: has_current={banner_data.get('has_current')}, has_next={banner_data.get('has_next')}")

        if not banner_data.get("has_current") and not banner_data.get("has_next"):
            message = format_banner_message("wuwa", banner_data)
            await query.edit_message_text(message)
        else:
            # Показываем анимацию печати
            await query.message.chat.send_action(ChatAction.TYPING)

            try:
                # Сначала отправляем текстовое сообщение
                message = format_banner_message("wuwa", banner_data)
                await query.message.reply_text(message, parse_mode="HTML", disable_web_page_preview=True)

                # Затем отправляем карточки баннеров
                cards = get_banner_cards_for_game("wuwa")
                if cards:
                    # Создаем медиа-группу без текста
                    media_group = []
                    for card in cards:
                        card.seek(0)  # Сбрасываем позицию в начало файла
                        media_group.append(InputMediaPhoto(media=card))

                    # Отправляем медиа-группу
                    await query.message.reply_media_group(media=media_group)

            except Exception as e:
                logger.error(f"Ошибка отправки карточек баннеров WuWa: {e}")
                # Fallback на текстовое сообщение
                message = format_banner_message("wuwa", banner_data)
                await query.message.reply_text(message, parse_mode="HTML", disable_web_page_preview=True)

        
    # Обработка промокодов из клавиатур ссылок
    elif data == "genshin_codes":
        promocodes = get_promocodes("genshin")
        message = format_promocodes_message("genshin", promocodes)
        await query.edit_message_text(message, parse_mode="HTML", disable_web_page_preview=True)
    elif data == "hsr_codes":
        promocodes = get_promocodes("hsr")
        message = format_promocodes_message("hsr", promocodes)
        await query.edit_message_text(message, parse_mode="HTML", disable_web_page_preview=True)
    elif data == "zzz_codes":
        promocodes = get_promocodes("zzz")
        message = format_promocodes_message("zzz", promocodes)
        await query.edit_message_text(message, parse_mode="HTML", disable_web_page_preview=True)
    elif data == "wuwa_codes":
        promocodes = get_promocodes("wuwa")
        message = format_promocodes_message("wuwa", promocodes)
        await query.edit_message_text(message, parse_mode="HTML", disable_web_page_preview=True)
    
    # Возврат в главное меню
    elif data == "back_to_main":
        await query.edit_message_text(
            "🏠 Главное меню",
            reply_markup=get_main_menu()
        )

# Обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Основная функция запуска бота"""
    # Проверяем наличие токена
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не установлен в config.py")
        return

    # Проверяем наличие ADMIN_ID
    if not ADMIN_ID:
        logger.error("ADMIN_ID не установлен в config.py")
        return

    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("update_banners", update_banners_command))
    application.add_handler(CommandHandler("banner_status", banner_status_command))
    application.add_handler(CommandHandler("clear_cache", clear_cache_command))
    application.add_handler(CommandHandler("cache_stats", cache_stats_command))
    application.add_handler(CommandHandler("update_commands", update_commands_command))
    application.add_handler(CommandHandler("add_to_whitelist", add_to_whitelist_command))
    application.add_handler(CommandHandler("remove_from_whitelist", remove_from_whitelist_command))
    application.add_handler(CommandHandler("show_whitelist", show_whitelist_command))

    # Добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Добавляем обработчик inline кнопок
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)

    # Запускаем бота
    logger.info("Запуск бота...")
    application.run_polling()

if __name__ == '__main__':
    main()
