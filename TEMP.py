import asyncio
import time

from db_core.engine import AsyncScopedSessionPG, AsyncScopedSessionDesc

from db_core.postgres_func import get_description


async def main():
    async with AsyncScopedSessionPG() as session_pg:
        async with AsyncScopedSessionDesc() as session_desc:
            d = await get_description(code='18910', session_pg=session_pg, session_desc=session_desc)
    print(d)

if __name__ == '__main__':
    asyncio.run(main())
