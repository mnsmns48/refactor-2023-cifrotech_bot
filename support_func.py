from aiogram import F
from aiogram.types import Message
from magic_filter import MagicFilter
from sqlalchemy.sql.functions import now

from config import hv


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
        result = list()
        for i in line:
            if i.isalnum() or i.isspace() or i == '+' or i == '/' or i == '\"' or i == ',':
                result.append(i)
        return ['строка ' + ''.join(result)]

    # k = -1
    # try:
    #     while result[k].isdigit():
    #         k -= 1
    # except IndexError:
    #     pass
    # try:
    #     return [self.seller,
    #             now(),
    #             ''.join(result[:k + 1]).strip(),
    #             int(''.join(result[k + 1:])),
    #             int(''.join(result[k + 1:])) + 1500
    #             ]
    # except ValueError:
    #     pass

    def pars_price_data(self) -> list:
        out = list()
        for line in self.data:
            if len(line) >= 21 or 'наличи' in line:
                out.append(tuple(self.pars_line(line.strip())))
        return out
