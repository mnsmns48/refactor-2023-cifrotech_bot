import re
import time

from aiogram import F
from aiogram.types import Message
from magic_filter import MagicFilter
from sqlalchemy.sql.functions import now

from config import hv, price_range, names_intersection


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
    def pars_line(line: str) -> dict:
        result_dict = {
            'product_type': None,
            'brand': None,
            'name': None,
            'price_1': None,
            'price_2': None
        }
        price_res_match = re.findall(r"[\s\W]+\d{3,5}[\s\W]?", line)
        product_type = re.search(r"Смартфон|"
                                 r"Внешний аккумулятор|"
                                 r"Роутер|"
                                 r"Умные часы|"
                                 r"Ноутбук|"
                                 r"Планшет|"
                                 r"Фитнес Браслет|"
                                 r"Монитор|"
                                 r"пылесос|"
                                 r"Приставка|"
                                 r"наушники|"
                                 r"колонка", line)
        brand_name = re.search(r"iPhone|"
                               r"Xiaomi|"
                               r"Samsung|"
                               r"Redmi|"
                               r"JBL|"
                               r"Galaxy|"
                               r"Airpods|"
                               r"Poco|"
                               r"HOCO|"
                               r"Tecno|"
                               r"Infinix|"
                               r"Nokia|"
                               r"Realme|"
                               r"TCL|"
                               r"Яндекс|"
                               r"Pova|"
                               r"AW|"
                               r"AirPods", line)
        if len(price_res_match) > 0:
            price_res = list()
            for i in price_res_match[-1]:
                if i.isdigit():
                    price_res.append(i)
            found_price = int(''.join(price_res))
            for i in price_range:
                if i[0] <= found_price <= i[1]:
                    result_dict['price_1'] = found_price
                    result_dict['price_2'] = found_price + i[2]
            result_dict['name'] = line.replace(price_res_match[-1], '')
            if hasattr(product_type, 'group'):
                result_dict['product_type'] = product_type.group()
            if hasattr(brand_name, 'group'):
                result_dict['brand'] = brand_name.group()
        return result_dict

    def pars_price_data(self) -> list:
        result_list = list()
        for line in self.data:
            pars_data = self.pars_line(line)
            if pars_data.get('price_2'):
                result_list.append(pars_data)
        for data_set in result_list:
            data_set['seller'] = self.seller
            if data_set.get('brand') in names_intersection.keys():
                data_set.update(names_intersection[data_set.get('brand')])
        return result_list
