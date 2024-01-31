from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

admin_basic_ = [
    [KeyboardButton(text='Продажи сегодня')],
    [KeyboardButton(text='Последние гости')],
    [KeyboardButton(text='W-APP', web_app=WebAppInfo(url='https://24cifrotech.ru'))],
]

admin_basic_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=admin_basic_)

send_to_channel = InlineKeyboardBuilder()
send_to_channel.add(InlineKeyboardButton(text='Отправить в канал', callback_data="send_to_channel"))
send_to_channel.add(InlineKeyboardButton(text='Пропустить отправку', callback_data="cancel_sending"))