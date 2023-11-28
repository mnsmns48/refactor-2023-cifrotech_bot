from datetime import datetime

from sqlalchemy import select, func, Result
from sqlalchemy.ext.asyncio import AsyncSession

from db_core.models import activity


async def get_today_activity(session_pg: AsyncSession) -> str:
    today = datetime.now().date()
    stmt = select(activity).filter(func.DATE(activity.c.time_) == today).order_by(activity.c.time_)
    result: Result = await session_pg.execute(stmt)
    response = result.fetchall()
    print(response)