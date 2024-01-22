from aiogram import F
from magic_filter import MagicFilter


def check_seller(sellers: dict) -> MagicFilter:
    chat, id_ = set(), set()
    [chat.add(k) if k < 0 else id_.add(k) for k in sellers.keys()]
    return F.forward_from.id.in_(id_) | F.forward_from_chat.id.in_(chat)
