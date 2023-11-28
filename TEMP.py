import asyncio
from db_core.engine import async_session_pg
from db_core.postgres_func import get_today_activity


async def main():
    async with async_session_pg() as session:
        await get_today_activity(session_pg=session)


if __name__ == '__main__':
    asyncio.run(main())
