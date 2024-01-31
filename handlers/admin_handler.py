from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from aiogram.types import Message, CallbackQuery

from config import hv, bot
from db_core.engine import AsyncScopedSessionPG
from db_core.models import sellers
from db_core.DB_interaction import take_last_guests, get_today_activity, upload_price_data
from filters import AdminFilter
from fsm import GetData
from keyboards.admin_keyboard import admin_basic_kb, send_to_channel
from db_core.support_functions import check_seller, PriceList
from keyboards.user_keyboards import choose_order

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


async def load_prices(m: Message, state: FSMContext):
    unknown_items = bool()
    data_set = await PriceList(m).pars_price_data()
    async with AsyncScopedSessionPG() as session:
        await upload_price_data(session_pg=session, table=sellers, data=data_set)
    for i in data_set:
        if i.get('product_type') is None or i.get('brand') is None:
            unknown_items = True
    if unknown_items:
        await m.answer('Downloaded... Check UNKNOWN records !!', reply_markup=send_to_channel.as_markup())
    else:
        await m.answer('FULL OK', reply_markup=send_to_channel.as_markup())
    await state.update_data(message=data_set)
    await state.set_state(GetData.price_text)


async def send_to_channel_(c: CallbackQuery, state: FSMContext):
    await c.answer('ок')
    if c.data == "cancel_sending":
        await state.clear()
    if c.data == "send_to_channel":
        text = str()
        data = await state.get_data()
        for line in data.get('message'):
            text = text + ''.join(f"✷ {line.get('name')} ➛ {line.get('price_2')} ₽\n")
        if len(text) > 4096:
            for i in range(0, len(text), 4096):
                part_mess = text[i: i + 4096]
                await bot.send_message(chat_id=hv.channel_id, text=part_mess)
        else:
            await bot.send_message(chat_id=hv.channel_id, text=text)
        await bot.send_message(chat_id=hv.channel_id,
                               text='Связаться для заказа ⤵️',
                               reply_markup=choose_order.as_markup())
        await state.clear()


async def register_admin_handlers():
    admin_.message.filter(AdminFilter())
    admin_.callback_query.register(send_to_channel_, GetData.price_text)
    admin_.message.register(start, CommandStart())
    admin_.message.register(show_sales, F.text == 'Продажи сегодня')
    admin_.message.register(show_guests, F.text == 'Последние гости')
    admin_.message.register(load_prices, await check_seller(hv.sellers_list))
