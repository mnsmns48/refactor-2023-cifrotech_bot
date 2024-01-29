from datetime import timezone, timedelta

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile

from config import bot, hv, cfg_order_category_
from db_core.engine import AsyncScopedSessionPG, AsyncScopedSessionDesc
from db_core.DB_interaction import get_description, user_spotted
from db_core.support_functions import date_out, price_list_formation
from keyboards.user_keyboards import main_menu_kb, keyboard_maker, order_kb

user_ = Router()


async def start(m: Message):
    date = m.date.astimezone(timezone(timedelta(hours=3), "Moscow")).replace(tzinfo=None)
    async with AsyncScopedSessionPG() as session_pg:
        await user_spotted(time_=date,
                           id_=m.from_user.id,
                           fullname=m.from_user.full_name,
                           username=m.from_user.username,
                           session_pg=session_pg)
    await bot.send_message(chat_id=hv.admin_id[0],
                           text=f"new user spotted\n"
                                f"{date_out(m.date)} "
                                f"{m.from_user.full_name} "
                                f"{m.from_user.username}\n"
                                f"{m.from_user.id}",
                           disable_notification=True
                           )
    await m.answer_photo(photo='AgACAgIAAxkBAAIFuWQVrxkxJMuUdAUGfGAuXSt448I1AAKgxjEbYxGxSFOciZYzLCoJAQADAgADeQADLwQ',
                         caption=f'Привет, {m.from_user.full_name}, этот БОТ показывает наличие и цены '
                                 f'в салоне мобильной связи ЦИФРОТЕХ\n\n'
                                 f'Телеграм канал @cifrotechmobile\n\n'
                                 f'Управление через кнопки ↓ ↓ ↓ ↓ ↓ ↓ ',
                         reply_markup=main_menu_kb)
    # await m.answer(text='usermode', reply_markup=main_menu_kb)


async def main_menu(m: Message):
    await m.answer('Навигация по кнопкам ❂', reply_markup=main_menu_kb)


async def walking_dirs(m: Message):
    async with AsyncScopedSessionPG() as session_pg:
        kb = await keyboard_maker(path=str(m.text), session_pg=session_pg)
    await m.answer('⤡', reply_markup=kb)


async def show_product(c: CallbackQuery):
    async with AsyncScopedSessionPG() as session_pg:
        async with AsyncScopedSessionDesc() as session_desc:
            answer = await get_description(code=c.data, session_pg=session_pg, session_desc=session_desc)
    text = f"{answer.get('product_name')}\n{answer.get('price')}\nв наличии {answer.get('quantity')}\n\n"
    if answer.get('full_desc'):
        text += answer.get('full_desc')
    photo = FSInputFile(answer['link'])
    await c.message.answer_photo(photo=photo, caption=text)


async def get_category_by_order(m: Message):
    await m.answer(f"Товары доставляются от 1-ого до 10-дней (в редких случаях)\n"
                   f"В среднем, по опыту этот срок 3-5 дней", reply_markup=order_kb)


async def get_order_list(m: Message):
    if await price_list_formation(m.text) == 'main':
        await m.answer('Главное меню', reply_markup=main_menu_kb)
    else:
        text = await price_list_formation(m.text)
        await m.answer(text=text)


async def register_user_handlers():
    user_.callback_query.register(show_product)
    user_.message.register(start, CommandStart())
    user_.message.register(get_category_by_order, F.text == '🧾 Под заказ 🚀 [СПЕЦ ЦЕНЫ]')
    user_.message.register(get_order_list, F.text.in_(cfg_order_category_.keys()))

    # user_.message.register(main_menu, F.text == '- - - Главное меню - - -')
    # user_.message.register(walking_dirs)
