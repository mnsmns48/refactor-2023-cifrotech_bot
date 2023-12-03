from datetime import timezone, timedelta, datetime

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile

from config import bot, hv
from db_core.engine import AsyncScopedSessionPG, AsyncScopedSessionDesc
from db_core.postgres_func import get_description
from db_core.support_functions import user_spotted, date_out
from keyboards.user_keyboards import main_menu_kb, keyboard_maker

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
    # await m.answer_photo(photo='AgACAgIAAxkBAAIFuWQVrxkxJMuUdAUGfGAuXSt448I1AAKgxjEbYxGxSFOciZYzLCoJAQADAgADeQADLwQ',
    #                      caption=f'Привет, {m.from_user.full_name}, этот БОТ показывает наличие и цены '
    #                              f'в салоне мобильной связи ЦИФРОТЕХ\n\n'
    #                              f'Телеграм канал @cifrotechmobile',
    #                      reply_markup=main_menu_kb)
    await m.answer(text='usermode', reply_markup=main_menu_kb)


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


def register_user_handlers():
    user_.callback_query.register(show_product)
    user_.message.register(start, CommandStart())
    user_.message.register(main_menu, F.text == '- - - Главное меню - - -')
    user_.message.register(walking_dirs)
