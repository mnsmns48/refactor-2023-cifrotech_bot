import re
from aiogram import F
from aiogram.types import Message
from magic_filter import MagicFilter
from sqlalchemy.sql.functions import now

from config import hv, price_range


def check_seller(sellers: dict) -> MagicFilter:
    chat, id_ = list(), list()
    [chat.append(k) if k < 0 else id_.append(k) for k in sellers.keys()]
    return F.forward_from.id.in_(id_) | F.forward_from_chat.id.in_(chat)


class PriceList:
    def __init__(self, m: Message):
        self.sender_id = m.forward_from.id if m.forward_from else m.forward_from_chat.id
        self.seller = hv.sellers_list.get(self.sender_id)
        self.data = m.text.split('\n')

    @staticmethod
    def pars_line(line: str):
        match = re.findall(r"[\s\W]+\d{3,5}[\s\W]?", line)
        result = list()
        if match:
            for i in match[-1]:
                if i.isdigit():
                    result.append(i)
        name = line.replace(match[-1], '')
        price = int(''.join(result))
        for i in price_range:
            if i[0] <= price <= i[1]:
                print(name, price, price + i[2])

    def pars_price_data(self) -> list:
        out = list()
        for line in self.data:
            out.append(self.pars_line(line.strip()))
        # return out
