from telegram import InlineKeyboardButton
keyboard = [
    [
        InlineKeyboardButton("📊 Ammiteus", url="https://akasha.cv/profile/720613453"),
    ],
    [InlineKeyboardButton("KQM", url="https://keqingmains.com")],
    [InlineKeyboardButton("Планер", url="https://seelie.me/characters")],
    [InlineKeyboardButton("Tier List", url="https://genshin-info.ru/top-personazhej")],
    [
        InlineKeyboardButton("Бездна", url="https://homdgcat.wiki/gi/abyss?lang=EN"),
        InlineKeyboardButton("Театр", url="https://homdgcat.wiki/gi/maze?lang=EN")
    ],
    [
        InlineKeyboardButton("Натиск", url="https://homdgcat.wiki/gi/3boss?lang=EN"),
    ],
    [InlineKeyboardButton("Сливы от HOMDGCAT", url="https://homdgcat.wiki/gi/change")],
    [
        InlineKeyboardButton("Персы", url="https://paimon.moe/characters"),
        InlineKeyboardButton("Крутки", url="https://paimon.moe/wish")
    ],
    [InlineKeyboardButton("История баннеров", callback_data="genshin_banners")],
    [InlineKeyboardButton("Промокоды", callback_data="genshin_codes")],
]