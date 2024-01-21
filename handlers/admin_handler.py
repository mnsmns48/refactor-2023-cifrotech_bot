from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import hv
from db_core.engine import AsyncScopedSessionPG
from db_core.postgres_func import take_last_guests, get_today_activity
from filters import AdminFilter
from fsm import GetPrice
from keyboards.admin_keyboard import admin_basic_kb, sellers_kb

admin_ = Router()


async def start(m: Message):
    await m.answer('Admin Mode', reply_markup=admin_basic_kb)


async def upload_pic(m: Message):
    id_photo = m.photo[-1].file_id
    await m.answer('ID на сервере Telegram:')
    await m.answer(id_photo)


async def show_sales(m: Message):
    async with AsyncScopedSessionPG() as session_pg:
        answer = await get_today_activity(session_pg=session_pg)
    await m.answer(text=answer)


async def show_guests(m: Message):
    async with AsyncScopedSessionPG() as session_pg:
        answer = await take_last_guests(session_pg=session_pg)
    await m.answer(text=answer)


async def load_prices(m: Message, state=FSMContext):
    await m.answer('Выбери необходимого поставщика', reply_markup=sellers_kb)
    await state.set_state(GetPrice.wait_price_text)


async def get_price(m: Message, state=FSMContext):
    await m.answer(f'ты нажал на {m.text}')
    await state.clear()


def register_admin_handlers():
    admin_.message.filter(AdminFilter())
    admin_.message.register(start, CommandStart())
    admin_.message.register(upload_pic, F.photo)
    admin_.message.register(show_sales, F.text == 'Продажи сегодня')
    admin_.message.register(show_guests, F.text == 'Последние гости')
    admin_.message.register(load_prices, F.text == 'Загрузка прайсов')
    admin_.message.register(get_price, GetPrice.wait_price_text)
