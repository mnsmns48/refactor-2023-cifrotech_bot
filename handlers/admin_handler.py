from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from filters import AdminFilter
from keyboards.admin_keyboard import admin_basic_kb

admin_ = Router()


async def start(m: Message):
    await m.answer('Admin Mode', reply_markup=admin_basic_kb)


def register_admin_handlers():
    admin_.message.filter(AdminFilter())
    admin_.message.register(start, CommandStart())
