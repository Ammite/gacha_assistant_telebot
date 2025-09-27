from telegram import InlineKeyboardButton
keyboard = [
    [
        InlineKeyboardButton("📊 Ammiteus", url="https://interknot-network.com/?uid=1500130510"),
    ],
    [InlineKeyboardButton("Планер", url="https://zzz.seelie.me/planner")],
    [InlineKeyboardButton("Tier List", url="https://www.prydwen.gg/zenless/tier-list")],
    [
        InlineKeyboardButton("Шиюй", url="https://zzz3.hakush.in/shiyu"),
        InlineKeyboardButton("Штурм", url="https://zzz3.hakush.in/boss")
    ],
    [InlineKeyboardButton("Сливы", url="https://zzz3.hakush.in")],
    [
        InlineKeyboardButton("Персы", url="https://zzz3.hakush.in/character"),
        # InlineKeyboardButton("Крутки", url="")
    ],
    [InlineKeyboardButton("История баннеров", callback_data="zzz_banners")],
    [InlineKeyboardButton("Промокоды", callback_data="zzz_codes")],
]