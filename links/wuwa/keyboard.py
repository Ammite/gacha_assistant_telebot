from telegram import InlineKeyboardButton
keyboard = [
    # [
    #     InlineKeyboardButton("📊 Ammiteus", url="https://fribbels.github.io/hsr-optimizer#showcase?id=700592438"),
    #     InlineKeyboardButton("📊 Getsuga", url="https://fribbels.github.io/hsr-optimizer#showcase?id=719764104")
    # ],
    [InlineKeyboardButton("Tools/Calcs", url="https://phro.love")],
    [InlineKeyboardButton("Tier List", url="https://www.prydwen.gg/wuthering-waves/tier-list")],
    # [
    #     InlineKeyboardButton("Апок", url="https://homdgcat.wiki/sr/shadow?lang=EN"),
    #     InlineKeyboardButton("MOC", url="https://homdgcat.wiki/sr/chaos?lang=EN")
    # ],
    # [
    #     InlineKeyboardButton("ПФ", url="https://homdgcat.wiki/sr/fiction?lang=EN"),
    #     InlineKeyboardButton("Арбитраж", url="https://homdgcat.wiki/sr/arbitration/?lang=EN")
    # ],
    # [InlineKeyboardButton("Сливы от HOMDGCAT", url="https://homdgcat.wiki/sr/future")],
    [
        InlineKeyboardButton("Персы", url="https://www.prydwen.gg/wuthering-waves/characters"),
        InlineKeyboardButton("Крутки", url="https://wuwatracker.com/tracker")
    ],
    [InlineKeyboardButton("История баннеров", callback_data="wuwa_banners")],
    # [InlineKeyboardButton("Промокоды", callback_data="wuwa_codes")],
]