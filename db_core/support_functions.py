from datetime import datetime, timezone, timedelta
from typing import Any
from sqlalchemy import Row, insert
from sqlalchemy.ext.asyncio import AsyncSession

from db_core.models import guests


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


async def user_spotted(time_: datetime, id_: int, fullname: str, username: str, session_pg: AsyncSession) -> None:
    insert_data = {
        'time_': time_,
        'id_': id_,
        'fullname': fullname,
        'username': username
    }
    await session_pg.execute(insert(guests), insert_data)
    await session_pg.commit()

