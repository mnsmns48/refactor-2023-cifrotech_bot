import asyncio

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import hv
from db_core.engine import AsyncScopedSessionPG
from db_core.models import sellers
from db_core.DB_interaction import take_last_guests, get_today_activity, load_price_data, get_lack_data
from filters import AdminFilter
from fsm import GetPrice
from keyboards.admin_keyboard import admin_basic_kb, sellers_kb
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
    k = PriceList(m)
    unknown = await k.pars_price_data()
    async with AsyncScopedSessionPG() as session:
        result = await get_lack_data(session=session, table=sellers, name=unknown)
    for line in result:
        print(line.product_type, line.brand, line.name)
    # for data_set in await k.pars_price_data():
    #     for k, v in data_set.items():
    #         print(f'{k}: {v}')
    #     print('\n---------------------\n')

    # with open('test.json', 'w', encoding='utf-8') as file:
    #     file.write(m.model_dump_json())

    # async with AsyncScopedSessionPG() as session_pg:
    #     await load_price_data(session_pg=session_pg, table=sellers, data=k)
    # for data_set in k:
    #     for k, v in data_set.items():
    #         print(f'{k}: {v}')
    #     print('\n---------------------\n')
    # k = m.text
    # f = m.text.split('\n')
    # for line in f:
    #     print(line)

    # async with AsyncScopedSessionPG() as session_pg:
    #     await load_price_data(session_pg=session_pg, table=sellers, data=k.pars_price_data())


# async def load_prices(m: Message, state=FSMContext):
#     await m.answer('Выбери необходимого поставщика', reply_markup=sellers_kb.as_markup())
#     await state.set_state(GetPrice.wait_price_text)


# async def get_price(c: CallbackQuery, state=FSMContext):
#     await c.answer(text=f'Добавляем в базу данные от {c.data}')
#     # await m.answer(m.text)
#     await state.clear()


async def register_admin_handlers():
    admin_.message.filter(AdminFilter())
    admin_.message.register(start, CommandStart())
    admin_.message.register(show_sales, F.text == 'Продажи сегодня')
    admin_.message.register(show_guests, F.text == 'Последние гости')
    admin_.message.register(load_prices, await check_seller(hv.sellers_list))
    # admin_.message.register(load_prices, F.text == 'Загрузка прайсов')
    # admin_.callback_query.register(get_price, GetPrice.wait_price_text)
