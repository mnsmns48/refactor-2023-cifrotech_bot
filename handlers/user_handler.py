from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from db_core.engine import AsyncScopedSession, async_session_factory

from keyboards.user_keyboards import main_menu_kb, kb_maker

user_ = Router()


async def start(m: Message):
    await m.answer('user mode', reply_markup=main_menu_kb)


async def menu(m: Message):
    async with AsyncScopedSession() as session:
        kb = await kb_maker(path=str(m.text), session=session)
    await m.answer('В наличии:', reply_markup=kb)


def register_admin_handlers():
    user_.message.register(start, CommandStart())
    user_.message.register(callback=menu)
