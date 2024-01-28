from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo


admin_basic_ = [
    [KeyboardButton(text='Продажи сегодня')],
    [KeyboardButton(text='Последние гости')],
    [KeyboardButton(text='W-APP', web_app=WebAppInfo(url='https://24cifrotech.ru'))],
]

admin_basic_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=admin_basic_)

