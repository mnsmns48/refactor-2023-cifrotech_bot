import asyncio
import re
from datetime import datetime, timezone, timedelta
from typing import Any

from aiogram import F
from aiogram.types import Message
from magic_filter import MagicFilter
from sqlalchemy import Row, Table, Column, select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from config import hv, price_range, names_intersection, product_type_regexp_stmt, brand_regexp_stmt
from db_core.engine import AsyncScopedSessionPG
from db_core.models import sellers


def month_conv(m: Row[tuple[Any, ...] | Any]) -> str:
    month = {
        '01': 'Январь',
        '02': 'Февраль',
        '03': 'Март',
        '04': 'Апрель',
        '05': 'Май',
        '06': 'Июнь',
        '07': 'Июль',
        '08': 'Август',
        '09': 'Сентябрь',
        '10': 'Октябрь',
        '11': 'Ноябрь',
        '12': 'Декабрь'
    }
    return f"{month.get(m.split('-')[1])} {m.split('-')[0]}"


def resolution_conv(r: Row[tuple[Any, ...] | Any]) -> str:
    return f"{r.split(' x ')[1]}x{r.split(' x ')[0]}"


def date_out(date: datetime) -> str:
    m_date = date.astimezone(timezone(timedelta(hours=3), "Moscow"))
    out_date = m_date.strftime("%d-%m___%H:%M")
    return out_date


async def check_seller(sellers: dict) -> MagicFilter:
    chat, id_ = list(), list()
    [chat.append(k) if k < 0 else id_.append(k) for k in sellers.keys()]
    return F.forward_from.id.in_(id_) | F.forward_from_chat.id.in_(chat)


class PriceList:
    def __init__(self, m: Message):
        self.sender_id = m.forward_from.id if m.forward_from else m.forward_from_chat.id
        self.seller = hv.sellers_list.get(self.sender_id)
        self.data = m.text.split('\n')

    @staticmethod
    async def pars_line(line: str) -> dict:
        result_dict = {
            'product_type': None,
            'brand': None,
            'name': None,
            'price_1': None,
            'price_2': None
        }
        price_res_match = re.findall(r"[\s\W]+\d{3,5}[\s\W]?", line)
        product_type = re.search(product_type_regexp_stmt, line)
        brand_name = re.search(brand_regexp_stmt, line)
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

    async def pars_price_data(self) -> list:
        unknown_elements = list()
        result_list = list()
        for line in self.data:
            pars_data = await self.pars_line(line.strip())
            if pars_data.get('price_2'):
                result_list.append(pars_data)
        for data_set in result_list:
            data_set['seller'] = self.seller
            if data_set.get('brand') in names_intersection.keys():
                data_set.update(names_intersection[data_set.get('brand')])
            if data_set.get('product_type') in names_intersection.keys():
                data_set.update(names_intersection[data_set.get('product_type')])
            if data_set.get('product_type') is None or data_set.get('brand') is None:
                unknown_elements.append(data_set['name'])
        return unknown_elements
