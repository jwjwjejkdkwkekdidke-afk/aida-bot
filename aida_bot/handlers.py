import html

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, FSInputFile

import db
from config import IMAGES_DIR, PRICE_RUB, SEASON_TITLE, ADMIN_IDS, CARD_NUMBER
from episodes import get_episode, load_episodes
from keyboards import main_kb, episodes_kb, episode_kb, pay_kb, admin_kb

router = Router()


class Pay(StatesGroup):
    waiting_receipt = State()


WELCOME = (
    f"🎬 <b>{SEASON_TITLE}</b>\n\n"
    f"Весь первый сезон — {len(load_episodes())} серий.\n"
    f"Чтобы смотреть, оплатите доступ: <b>{PRICE_RUB} ₽</b> (разово, навсегда).\n\n"
    "Нажмите «Список серий», чтобы увидеть превью."
)


@router.message(CommandStart())
async def start(m: Message, state: FSMContext):
    await state.clear()
    db.add_user(m.from_user.id, m.from_user.username)
    paid = db.has_access(m.from_user.id)
    await m.answer_photo(
        FSInputFile(IMAGES_DIR / "ep1.jpg"),
        caption=WELCOME if not paid else f"🎬 <b>{SEASON_TITLE}</b>\n\n✅ Доступ открыт. Приятного просмотра!",
        reply_markup=main_kb(paid),
    )


@router.callback_query(F.data == "episodes")
async def show_episodes(c: CallbackQuery):
    paid = db.has_access(c.from_user.id)
    await c.message.answer("Выберите серию:", reply_markup=episodes_kb(paid))
    await c.answer()


@router.callback_query(F.data.startswith("ep:"))
async def show_episode(c: CallbackQuery):
    number = int(c.data.split(":")[1])
    ep = get_episode(number)
    if not ep:
        await c.answer("Серия не найдена", show_alert=True)
        return
    paid = db.has_access(c.from_user.id)
    caption = f"<b>{SEASON_TITLE}</b> — {ep['title']}"

    if not paid:
        await c.message.answer_photo(
            FSInputFile(IMAGES_DIR / ep["preview"]),
            caption=caption + f"\n\n🔒 Для просмотра оплатите сезон: {PRICE_RUB} ₽",
            reply_markup=episode_kb(number, False),
        )
    elif ep.get("video"):
        await c.message.answer_video(
            ep["video"],
            caption=caption,
            protect_content=True,  # запрет пересылки/сохранения
            reply_markup=episode_kb(number, True),
        )
    else:
        await c.message.answer_photo(
            FSInputFile(IMAGES_DIR / ep["preview"]),
            caption=caption + "\n\n⏳ Серия скоро будет доступна.",
            reply_markup=episode_kb(number, True),
        )
    await c.answer()


# ---------- Оплата переводом на карту ----------
@router.callback_query(F.data == "buy")
async def buy(c: CallbackQuery):
    if db.has_access(c.from_user.id):
        await c.answer("У вас уже есть доступ ✅", show_alert=True)
        return
    await c.message.answer(
        f"💳 <b>Реквизиты:</b>\n<code>{CARD_NUMBER}</code>\n\n"
        f"Сумма: <b>{PRICE_RUB} ₽</b>\n\n"
        "После перевода нажмите кнопку «✅ Я оплатил».",
        reply_markup=pay_kb(),
    )
    await c.answer()


@router.callback_query(F.data == "paid")
async def paid_pressed(c: CallbackQuery, state: FSMContext):
    if db.has_access(c.from_user.id):
        await c.answer("У вас уже есть доступ ✅", show_alert=True)
        return
    await state.set_state(Pay.waiting_receipt)
    await c.message.answer("📸 Пришлите скриншот или чек перевода одним сообщением.")
    await c.answer()


@router.message(Pay.waiting_receipt, F.photo | F.document)
async def receipt(m: Message, state: FSMContext, bot: Bot):
    u = m.from_user
    name = html.escape(u.full_name)
    uname = f"@{u.username}" if u.username else "без username"
    caption = (
        f"💰 <b>Новая оплата</b>\n"
        f"Пользователь: {name} ({uname})\n"
        f"ID: <code>{u.id}</code>\n"
        f"Сумма: {PRICE_RUB} ₽"
    )
    sent = 0
    for admin_id in ADMIN_IDS:
        try:
            await bot.copy_message(
                chat_id=admin_id, from_chat_id=m.chat.id, message_id=m.message_id,
                caption=caption, reply_markup=admin_kb(u.id),
            )
            sent += 1
        except Exception:
            pass
    await state.clear()
    if sent:
        await m.answer("⏳ Спасибо! Платёж отправлен на проверку. Обычно это занимает несколько минут — "
                       "как только подтвердим, я пришлю уведомление.")
    else:
        await m.answer("Не удалось отправить заявку администратору. Попробуйте позже.")


@router.message(Pay.waiting_receipt)
async def receipt_wrong(m: Message):
    await m.answer("Пожалуйста, пришлите именно скриншот или чек (фото/файл).")


@router.callback_query(F.data.startswith("approve:"))
async def approve(c: CallbackQuery, bot: Bot):
    if c.from_user.id not in ADMIN_IDS:
        await c.answer("Нет доступа", show_alert=True)
        return
    uid = int(c.data.split(":")[1])
    if not db.has_access(uid):
        db.add_purchase(uid, PRICE_RUB, "card")
    await c.message.edit_caption(caption=(c.message.caption or "") + "\n\n✅ <b>Подтверждено</b>", reply_markup=None)
    try:
        await bot.send_message(uid, "✅ Оплата подтверждена! Доступ к 1 сезону открыт.\nВыберите серию:",
                               reply_markup=episodes_kb(True))
    except Exception:
        pass
    await c.answer("Доступ выдан")


@router.callback_query(F.data.startswith("reject:"))
async def reject(c: CallbackQuery, bot: Bot):
    if c.from_user.id not in ADMIN_IDS:
        await c.answer("Нет доступа", show_alert=True)
        return
    uid = int(c.data.split(":")[1])
    await c.message.edit_caption(caption=(c.message.caption or "") + "\n\n❌ <b>Отклонено</b>", reply_markup=None)
    try:
        await bot.send_message(uid, "❌ Платёж не найден. Проверьте перевод и пришлите чек ещё раз.",
                               reply_markup=pay_kb())
    except Exception:
        pass
    await c.answer("Отклонено")


# ---------- Админ ----------
@router.message(Command("stats"))
async def stats(m: Message):
    if m.from_user.id not in ADMIN_IDS:
        return
    users, buyers, total = db.stats()
    await m.answer(f"👥 Пользователей: {users}\n💰 Покупателей: {buyers}\n💵 Выручка: {total} ₽")


@router.message(Command("grant"))
async def grant(m: Message):
    """/grant 123456789 — выдать доступ вручную"""
    if m.from_user.id not in ADMIN_IDS:
        return
    parts = (m.text or "").split()
    if len(parts) != 2 or not parts[1].isdigit():
        await m.answer("Использование: /grant USER_ID")
        return
    db.add_purchase(int(parts[1]), 0, "manual")
    await m.answer("Доступ выдан ✅")


@router.message(F.video, F.from_user.id.in_(ADMIN_IDS))
async def get_file_id(m: Message):
    """Админ присылает видео боту — бот отвечает file_id для episodes.json"""
    await m.answer(f"file_id:\n<code>{m.video.file_id}</code>")
