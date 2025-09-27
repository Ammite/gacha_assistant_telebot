import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, USERS_WHITELIST
from methods import (
    check_if_user_in_whitelist, send_inline_keyboard, send_message, send_keyboard, update_commands,
    get_game_info, get_banner_info, get_useful_links, format_game_message, format_banner_message,
    load_game_keyboard
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
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
        "• 📋 Текущие баннеры\n"
        "• 🔗 Полезные ссылки\n"
        "• 📊 Статистика\n\n"
        "💡 Совет: Используйте кнопки меню для удобной навигации!"
    )
    
    await update.message.reply_text(help_text)

# Обработчик команды /menu
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /menu"""
    await update.message.reply_text(
        "🏠 Главное меню",
        reply_markup=get_main_menu()
    )

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
        banner_data = get_banner_info(game_name)
        message = format_banner_message(game_name, banner_data)
        await query.edit_message_text(message)
    
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
        banner_data = get_banner_info("genshin")
        message = format_banner_message("genshin", banner_data)
        await query.edit_message_text(message)
    elif data == "hsr_banners":
        banner_data = get_banner_info("hsr")
        message = format_banner_message("hsr", banner_data)
        await query.edit_message_text(message)
    elif data == "zzz_banners":
        banner_data = get_banner_info("zzz")
        message = format_banner_message("zzz", banner_data)
        await query.edit_message_text(message)
    elif data == "wuwa_banners":
        banner_data = get_banner_info("wuwa")
        message = format_banner_message("wuwa", banner_data)
        await query.edit_message_text(message)
    
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
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))
    
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
