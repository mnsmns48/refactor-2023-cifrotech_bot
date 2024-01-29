from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from db_core.DB_interaction import get_dirs_

main_menu_ = [
    [KeyboardButton(text='Запуск приложения', web_app=WebAppInfo(url='https://24cifrotech.ru'))],
    [KeyboardButton(text='🧾 Под заказ 🚀')],
]

main_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True,
                                   is_persistent=True,
                                   keyboard=main_menu_)


async def keyboard_maker(path: str, session_pg: AsyncSession) -> InlineKeyboardMarkup | ReplyKeyboardMarkup:
    buttons_dict_ = await get_dirs_(pathname=path, session_pg=session_pg)
    if buttons_dict_.get('destination_folder'):
        builder = InlineKeyboardBuilder()
        for line in buttons_dict_.get('product_list'):
            builder.row(InlineKeyboardButton(text=f"{line.price}₽ {line.name.split(' ', maxsplit=1)[1]}",
                                             callback_data=str(line.code)
                                             )
                        )
        return builder.as_markup()
    else:
        builder = ReplyKeyboardBuilder()
        builder.add(KeyboardButton(text='- - - Главное меню - - -')
                    )
        for line in buttons_dict_.get('product_list'):
            button = KeyboardButton(text=line.name)
            builder.add(button)
            builder.adjust(1)
        return builder.as_markup(resize_keyboard=True,
                                 is_persistent=True)
