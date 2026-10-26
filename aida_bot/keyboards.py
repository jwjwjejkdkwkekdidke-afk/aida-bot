from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import PRICE_RUB
from episodes import load_episodes

def main_kb(paid: bool) -> InlineKeyboardMarkup:
    rows = []
    if not paid:
        rows.append([InlineKeyboardButton(text=f"💳 Купить сезон — {PRICE_RUB} ₽", callback_data="buy")])
    rows.append([InlineKeyboardButton(text="🎞 Список серий", callback_data="episodes")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def episodes_kb(paid: bool) -> InlineKeyboardMarkup:
    rows, row = [], []
    for ep in load_episodes():
        icon = "▶️" if paid else "🔒"
        row.append(InlineKeyboardButton(text=f"{icon} {ep['number']}", callback_data=f"ep:{ep['number']}"))
        if len(row) == 4:
            rows.append(row); row = []
    if row:
        rows.append(row)
    if not paid:
        rows.append([InlineKeyboardButton(text=f"💳 Купить сезон — {PRICE_RUB} ₽", callback_data="buy")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def episode_kb(number: int, paid: bool) -> InlineKeyboardMarkup:
    total = len(load_episodes())
    nav = []
    if number > 1:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"ep:{number-1}"))
    nav.append(InlineKeyboardButton(text="🎞 Все серии", callback_data="episodes"))
    if number < total:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"ep:{number+1}"))
    rows = [nav]
    if not paid:
        rows.insert(0, [InlineKeyboardButton(text=f"💳 Купить сезон — {PRICE_RUB} ₽", callback_data="buy")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def pay_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="paid")],
        [InlineKeyboardButton(text="🎞 Список серий", callback_data="episodes")],
    ])


def admin_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve:{user_id}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject:{user_id}"),
    ]])
