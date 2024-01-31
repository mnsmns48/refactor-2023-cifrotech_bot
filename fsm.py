from aiogram.fsm.state import StatesGroup, State


class GetData(StatesGroup):
    price_text = State()

