import re
from datetime import datetime, timezone, timedelta
from typing import Any

from aiogram import F
from aiogram.types import Message
from magic_filter import MagicFilter
from sqlalchemy import Row, Table, select, Result, and_, text, func
from sqlalchemy.ext.asyncio import AsyncSession

from config import hv, price_range, names_intersection, product_type_regexp_stmt, brand_regexp_stmt, cfg_order_category_
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


async def check_seller(sellers_dict: dict) -> MagicFilter:
    chat, id_ = list(), list()
    [chat.append(k) if k < 0 else id_.append(k) for k in sellers_dict.keys()]
    return F.forward_from.id.in_(id_) | F.forward_from_chat.id.in_(chat)


async def get_lack_data(session: AsyncSession, table: Table, names: set):
    query = select(table).filter(table.c.name.in_(names))
    data: Result = await session.execute(query)
    return data.fetchall()


class PriceList:
    def __init__(self, m: Message):
        self.sender_id = m.forward_from.id if m.forward_from else m.forward_from_chat.id
        self.seller = hv.sellers_list.get(self.sender_id)
        self.data = m.text.split('\n')
        self.date = m.forward_date.replace(hour=m.forward_date.hour + 3).replace(tzinfo=None)

    @staticmethod
    async def pars_line(line: str) -> dict:
        result_dict = {
            'product_type': None,
            'brand': None,
            'name': None,
            'price_1': None,
            'price_2': None
        }
        price_res_match = re.findall(r"[\s\W]+\d{3,6}[\s\W]?", line)
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
        unknown_items = set()
        result_list = list()
        for line in self.data:
            pars_data = await self.pars_line(line.strip())
            if pars_data.get('price_2'):
                result_list.append(pars_data)
        for data_set in result_list:
            data_set['time_'] = self.date
            data_set['seller'] = self.seller
            if data_set.get('brand') in names_intersection.keys():
                data_set.update(names_intersection[data_set.get('brand')])
            if data_set.get('product_type') in names_intersection.keys():
                data_set.update(names_intersection[data_set.get('product_type')])
            if data_set.get('product_type') is None or data_set.get('product_type') is None:
                unknown_items.add(data_set.get('name'))
        if unknown_items:
            async with AsyncScopedSessionPG() as session_pg:
                db_search_res = await get_lack_data(session=session_pg, table=sellers, names=unknown_items)
            unknown_items.clear()
            founded_items_from_db = dict()
            for item in db_search_res:
                founded_items_from_db[item.name] = [item.product_type, item.brand]
            for data_set in result_list:
                if data_set.get('product_type') is None:
                    try:
                        data_set['product_type'] = founded_items_from_db.get(data_set['name'])[0]
                    except TypeError:
                        pass
                if data_set.get('brand') is None:
                    try:
                        data_set['brand'] = founded_items_from_db.get(data_set.get('name'))[1]
                    except TypeError:
                        pass
        return result_list


async def price_list_formation(message: str) -> str:
    output_str = str()
    if cfg_order_category_.get(message) == 'main':
        return 'main'
    else:
        if cfg_order_category_.get(message) == 'apple':
            sub = select(func.max(sellers.c.time_).filter(sellers.c.brand == 'Apple')).scalar_subquery()
            stmt = select(sellers).filter(and_(sellers.c.time_ == sub), (sellers.c.brand == 'Apple')) \
                .order_by(sellers.c.name, sellers.c.price_2)

        if cfg_order_category_.get(message) == 'samsung':
            # sub = select(func.max(sellers.c.time_)
            #              .filter(and_(sellers.c.brand == 'Samsung'),
            #                      (sellers.c.product_type.in_(['Планшет', 'Умные часы'])))).scalar_subquery()
            # stmt = (select(sellers)
            #         .filter(and_(sellers.c.brand == 'Samsung'),
            #                 (sellers.c.time_ >= sub))
            #         .order_by(sellers.c.product_type, sellers.c.price_2))
            stmt = (select(sellers)
                    .filter(and_(sellers.c.brand == 'Samsung'),
                            (func.DATE(sellers.c.time_) >= datetime.now() - timedelta(5)))
                    .order_by(sellers.c.price_2))

        if cfg_order_category_.get(message) == 'android':
            stmt = (select(sellers)
                    .filter(and_(sellers.c.product_type == 'Смартфон'),
                            (sellers.c.brand.not_in(['Samsung', 'Apple'])),
                            (func.DATE(sellers.c.time_) >= datetime.now() - timedelta(5)))
                    .order_by(sellers.c.price_2))

        if cfg_order_category_.get(message) == 'xiaomi':
            stmt = (select(sellers)
                    .filter(and_(sellers.c.product_type.not_in(['Смартфон', 'Планшет', 'Телевизор'])),
                            (sellers.c.brand.in_(['Xiaomi', 'HOCO'])),
                            (func.DATE(sellers.c.time_) >= datetime.now() - timedelta(5)))
                    .order_by(sellers.c.product_type, sellers.c.price_2))

        if cfg_order_category_.get(message) == 'audio':
            stmt = (select(sellers)
                    .filter(and_(sellers.c.product_type == 'Аудиотовар'),
                            (func.DATE(sellers.c.time_) >= datetime.now() - timedelta(10)))
                    .order_by(sellers.c.brand, sellers.c.price_2))

        if cfg_order_category_.get(message) == 'tv':
            stmt = (select(sellers)
                    .filter(and_(sellers.c.product_type.in_
                                 (['Телевизор', 'Игровая приставка', 'Смарт приставки'])),
                            (func.DATE(sellers.c.time_) >= datetime.now() - timedelta(10)))
                    .order_by(sellers.c.name, sellers.c.price_2))

        async with AsyncScopedSessionPG() as session:
            response = await session.execute(stmt)
        result = response.fetchall()
        if result:
            for line in result:
                output_str = output_str + ''.join(f"✷ {line.name} ➛ {line.price_2} ₽\n")
        else:
            output_str = 'На данный момент нет хороших предложений в этой категории товаров'

    return output_str
