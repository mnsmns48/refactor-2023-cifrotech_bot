from dataclasses import dataclass

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from environs import Env
from yadisk import YaDisk

dir_with_desc = [80, 81, 82, 83, 84, 87, 101]
price_range = [
    [0, 4990, 500],
    [4991, 9999, 1200],
    [10000, 12499, 1500],
    [12500, 14999, 1750],
    [15000, 17499, 2000],
    [17500, 19999, 2300],
    [20000, 24999, 3000],
    [25000, 29999, 3600],
    [30000, 34999, 4900],
    [35000, 39999, 4300],
    [40000, 49999, 4500],
    [50000, 59999, 4700],
    [60000, 79999, 4900],
    [80000, 89999, 5500],
    [90000, 109999, 6500],
    [110000, 129999, 7500],
    [130000, 200000, 9500]
]


@dataclass
class Hidden:
    bot_token: str
    admin_id: list[int]
    yatoken: str
    local_db_username: str
    local_db_password: str
    local_db_port: str
    local_db_name: str
    description_db_name: str
    photo_path: str
    sellers_list: dict


def load_config(path: str = '..env'):
    env = Env()
    env.read_env()
    return Hidden(
        admin_id=list(map(int, env.list("ADMIN_ID"))),
        bot_token=env.str("BOT_TOKEN"),
        yatoken=env.str("YATOKEN"),
        local_db_username=env.str("LOCAL_DB_USERNAME"),
        local_db_password=env.str("LOCAL_DB_PASSWORD"),
        local_db_port=env.str("LOCAL_DB_PORT"),
        local_db_name=env.str("LOCAL_DB_NAME"),
        description_db_name=env.str("DESCRIPTION_DB_NAME"),
        photo_path=env.str("PHOTO_PATH"),
        sellers_list=env.dict("SELLERS_LIST", subcast_keys=int, subcast_values=str),
    )


commands = [
    BotCommand(
        command='start',
        description='Начало работы бота'
    ),
    BotCommand(
        command='admin_message',
        description='Написать админу'
    )
]

hv = load_config()
bot = Bot(token=hv.bot_token)
dp = Dispatcher()
y = YaDisk(token=hv.yatoken)

