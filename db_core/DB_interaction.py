from datetime import datetime
from typing import Sequence

from sqlalchemy import select, func, Result, RowMapping, Row, and_, desc, insert, Table
from sqlalchemy.ext.asyncio import AsyncSession

from db_core.description_models import s_main, display, energy, camera, performance
from db_core.models import activity, StockTable, guests
from config import dir_with_desc, hv
from db_core.support_functions import month_conv, resolution_conv


async def get_dirs_(pathname: str, session_pg: AsyncSession) -> dict[str, bool | Sequence[Row | RowMapping]]:
    subquery = select(StockTable.code).where(StockTable.name == pathname).scalar_subquery()
    stmt = select(StockTable).where(StockTable.parent.in_(subquery)).order_by(StockTable.price)
    result: Result = await session_pg.execute(stmt)
    response = result.scalars().all()
    destination_folder = bool()
    for line in response:
        destination_folder = False if line.code < 1000 else True
    output = {'product_list': response, 'destination_folder': destination_folder}
    return output


async def get_description(code: str, session_pg: AsyncSession, session_desc: AsyncSession):
    stmt = select(StockTable).where(StockTable.code == int(code))
    result: Result = await session_pg.execute(stmt)
    response = result.scalar()
    temp_dict_ = {
        'product_name': response.name,
        'link': f'{hv.photo_path}{response.code}.jpg',
        'quantity': str(response.quantity) + ' шт',
        'price': str(response.price) + ' руб',
    }
    if response.parent in dir_with_desc:
        model = response.name.rsplit(' ', maxsplit=2)[0].split(' ', maxsplit=1)[1]
        description_stmt = select(
            s_main.c.title,
            s_main.c.category,
            s_main.c.release_date,
            display.c.d_size,
            display.c.display_type,
            display.c.refresh_rate,
            display.c.resolution,
            energy.c.capacity,
            energy.c.max_charge_power,
            energy.c.fast_charging,
            camera.c.lenses,
            camera.c.megapixels_front,
            performance.c.chipset,
            performance.c.total_score,
            s_main.c.advantage,
            s_main.c.disadvantage) \
            .where(
            and_(
                s_main.c.title == model,
                s_main.c.title == display.c.title,
                s_main.c.title == energy.c.title,
                s_main.c.title == camera.c.title,
                s_main.c.title == performance.c.title)
        )
        result: Result = await session_desc.execute(description_stmt)
        description = result.fetchall()[0]
        advantages = str()
        for line in description[14]:
            advantages += '+ ' + line + '\n'
        disadvantages = str()
        for line in description[15]:
            disadvantages += '- ' + line + '\n'
        temp_dict_.update(
            {
                'full_desc':
                    f"Дата выхода: {month_conv(description[2])}\n"
                    f"Класс: {description[1]}\n"
                    f"Дисплей: {description[3]} {description[4]} "
                    f"{resolution_conv(description[6])} {description[5]} Hz\n"
                    f"АКБ: {description[7]}, мощность заряда: {description[8]} W\n"
                    f"Быстрая зарядка: {description[9]}\n"
                    f"Основные камеры: {description[10]}\n"
                    f"Фронтальная: {description[11]} Мп\n"
                    f"Процессор: {description[12]}\n"
                    f"Оценка производительности: {description[13]}\n"
                    f"\nПреимущества\n"
                    f"{advantages}"
                    f"\nНедостатки\n"
                    f"{disadvantages}"
            }
        )
    return temp_dict_


async def get_today_activity(session_pg: AsyncSession) -> str:
    sales, returns, cardpay, amount = list(), list(), list(), list()
    today = datetime.now().date()
    stmt = select(activity).filter(func.DATE(activity.c.time_) == today).order_by(activity.c.time_)
    result: Result = await session_pg.execute(stmt)
    response = result.fetchall()
    for line in response:
        if not line[8]:
            amount.append(line[6])
        if line[7]:
            cardpay.append(line[6])
        l_temp_ = [
            str(line[1]).split(' ')[1][:5],
            line[3],
            line[4],
            int(line[5]) if str(line[5]).split('.')[1] == '0' else line[5],
            int(line[6]) if str(line[6]).split('.')[1] == '0' else line[6],
            '--C--' if line[7] else ''
        ]
        if line[8]:
            returns.append(l_temp_)
        else:
            sales.append(l_temp_)
    res = str()
    for line in sales:
        for i in line:
            res += ''.join(str(i) + ' ')
        res += '\n'
    if returns:
        res += '---Возвраты:\n'
        for line in returns:
            for i in line:
                res += ''.join(str(i) + ' ')
            res += '\n'
    res += f'Всего {sum(amount)}\n' \
           f'Наличные {sum(amount) - sum(cardpay)}\n'
    if sum(cardpay):
        res += f'Картой {sum(cardpay)}'
    return res


async def take_last_guests(session_pg: AsyncSession) -> str:
    res = str()
    stmt = select(guests).order_by(desc(guests.c.time_)).limit(10)
    result: Result = await session_pg.execute(stmt)
    response = result.fetchall()
    for line in response:
        res += ''.join(f"{str(line[0])} {line[1:-1]} {line[-1] if line[-1] is not None else ''}")
        res += '\n'
    return res


async def user_spotted(time_: datetime, id_: int, fullname: str, username: str, session_pg: AsyncSession) -> None:
    insert_data = {
        'time_': time_,
        'id_': id_,
        'fullname': fullname,
        'username': username
    }
    await session_pg.execute(insert(guests), insert_data)
    await session_pg.commit()


async def upload_price_data(session_pg: AsyncSession, table: Table, data: list):
    await session_pg.execute(insert(table), data)
    await session_pg.commit()


