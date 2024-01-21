from aiogram.fsm.state import StatesGroup, State


class GetPrice(StatesGroup):
    wait_price_text = State()
