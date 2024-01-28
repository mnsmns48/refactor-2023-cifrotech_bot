from aiogram import Router, F
from aiogram.filters import CommandStart

from aiogram.types import Message

from config import hv
from db_core.engine import AsyncScopedSessionPG
from db_core.models import sellers
from db_core.DB_interaction import take_last_guests, get_today_activity, upload_price_data
from filters import AdminFilter
from keyboards.admin_keyboard import admin_basic_kb
from db_core.support_functions import check_seller, PriceList

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


async def load_prices(m: Message):
    with open('date.json', 'w', encoding='utf-8') as file:
        file.write(m.model_dump_json())
    unknown_items = bool()
    data_set = await PriceList(m).pars_price_data()
    async with AsyncScopedSessionPG() as session:
        await upload_price_data(session_pg=session, table=sellers, data=data_set)
    for i in data_set:
        if i.get('product_type') is None or i.get('brand') is None:
            unknown_items = True
    if unknown_items:
        await m.answer('Downloaded... Check UNKNOWN records !!')
    else:
        await m.answer('FULL OK')


async def register_admin_handlers():
    admin_.message.filter(AdminFilter())
    admin_.message.register(start, CommandStart())
    admin_.message.register(show_sales, F.text == 'Продажи сегодня')
    admin_.message.register(show_guests, F.text == 'Последние гости')
    admin_.message.register(load_prices, await check_seller(hv.sellers_list))
