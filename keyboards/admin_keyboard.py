from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import hv

admin_basic_ = [
    [KeyboardButton(text='Продажи сегодня')],
    [KeyboardButton(text='Последние гости')],
    [KeyboardButton(text='W-APP', web_app=WebAppInfo(url='https://24cifrotech.ru'))],
    [KeyboardButton(text='Загрузка прайсов')],
]

admin_basic_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=admin_basic_)

seller_keys = [
    [InlineKeyboardButton(text=v, callback_data=v) for k, v in hv.sellers_list.items()]
]
sellers_kb = InlineKeyboardBuilder(seller_keys)
