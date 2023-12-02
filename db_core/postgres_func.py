from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Sequence

from sqlalchemy import select, func, Result, RowMapping, Row
from sqlalchemy.ext.asyncio import AsyncSession

from db_core.models import activity, StockTable


async def get_forward_(pathname: str, session: AsyncSession) -> dict[str, bool | Sequence[Row | RowMapping]]:
    if pathname == 'Назад':
        subquery = select(StockTable.code).where(StockTable.parent == 0).scalar_subquery()
    else:
        subquery = select(StockTable.code).where(StockTable.name == pathname).scalar_subquery()
    stmt = select(StockTable).where(StockTable.code.in_(subquery))
    result: Result = await session.execute(stmt)
    response = result.scalars().all()
    destination_folder = bool()
    for line in response:
        destination_folder = False if line.code < 1000 else True
        print(line.name)
    output = {'product_list': response, 'destination_folder': destination_folder}
    return output


async def get_today_activity(session: AsyncSession) -> str:
    today = datetime.now().date()
    stmt = select(activity).filter(func.DATE(activity.c.time_) == today).order_by(activity.c.time_)
    result: Result = await session.execute(stmt)
    response = result.fetchall()
    print(response)
