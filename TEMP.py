import asyncio
import time

from db_core.engine import AsyncScopedSession

from db_core.postgres_func import get_today_activity, get_kb
from keyboards.user_keyboards import kb_maker


async def main():
    await kb_maker(path='Смартфоны')

if __name__ == '__main__':
    asyncio.run(main())
