from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from db_core.postgres_func import get_forward_

main_menu_ = [
    [KeyboardButton(text='Смартфоны')],
    [KeyboardButton(text='Смарт часы, фитнес трекеры ')],
    [KeyboardButton(text='Планшеты')],
    [KeyboardButton(text='Кнопочные телефоны')],
    [KeyboardButton(text='Умные товары Xiaomi')],
    [KeyboardButton(text='Наушники')],
    [KeyboardButton(text='Портативная аккустика')],
    [KeyboardButton(text='Хранение информации(флешки, карты памяти, диски)')],
    [KeyboardButton(text='Аксессуары для компьютера')],
    [KeyboardButton(text='Кабеля и адаптеры')],
    [KeyboardButton(text='Сетевое оборудование')],
    [KeyboardButton(text='Авто товары')],
    [KeyboardButton(text='Внешние аккумуляторы (POWERBANK)')],
    [KeyboardButton(text='Зарядные устройства')],
    [KeyboardButton(text='Батареи и аккумуляторы ')],
]

main_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True,
                                   is_persistent=True,
                                   keyboard=main_menu_)


async def kb_maker(path: str, session: AsyncSession) -> ReplyKeyboardMarkup:

    buttons_dict_ = await get_forward_(pathname=path, session=session)
    builder = ReplyKeyboardBuilder()
    for line in buttons_dict_.get('product_list'):
        button = KeyboardButton(text=line.name)
        builder.add(button)
    builder.add(KeyboardButton(text='Назад'))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True,
                             is_persistent=True,
                             )
