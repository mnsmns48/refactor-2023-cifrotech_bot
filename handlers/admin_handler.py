from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from filters import AdminFilter
from keyboards.admin_keyboard import admin_basic_kb

admin_ = Router()


async def start(m: Message):
    await m.answer('Admin Mode', reply_markup=admin_basic_kb)


async def show_sales(m: Message):
    text = get_today_activity()
    await m.answer(text)


async def show_guests(m: Message):
    text = take_last_guests()
    await m.answer(text)


async def upload_pic(m: Message):
    id_photo = m.photo[-1].file_id
    await m.answer('ID на сервере Telegram:')
    await m.answer(id_photo)


# async def web_app_data_recieve(m: Message):
#    await message.answer(message.web_app_data.data)


def register_admin_handlers():
    admin_.message.filter(AdminFilter())
    admin_.message.register(start, CommandStart())
    admin_.message.register(show_sales, F.text == 'Продажи сегодня')
    admin_.message.register(show_guests, F.text == 'Последние гости')
    admin_.message.register(upload_pic, F.photo)
#    admin_.message.register(web_app_data_recieve, F.content_type == ContentType.WEB_APP_DATA)
