from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

from config import hv

admin_basic_ = [
    [KeyboardButton(text='Продажи сегодня')],
    [KeyboardButton(text='Последние гости')],
    [KeyboardButton(text='W-APP', web_app=WebAppInfo(url='https://24cifrotech.ru'))],
    [KeyboardButton(text='Загрузка прайсов')],
]

admin_basic_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=admin_basic_)


sellers_keys = [
    [KeyboardButton(text=i) for i in hv.sellers_list]
]
sellers_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=sellers_keys)