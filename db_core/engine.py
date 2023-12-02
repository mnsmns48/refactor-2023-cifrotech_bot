from asyncio import current_task

from pydantic.v1 import BaseSettings
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker, async_scoped_session, AsyncSession,

)

from config import hv


class CoreConfig(BaseSettings):
    as_stocktable: str = (
        f"postgresql+asyncpg://{hv.local_db_username}:{hv.local_db_password}"
        f"@localhost:{hv.local_db_port}/{hv.local_db_name}"
    )
    phones_desc_db: str = (
        f"postgresql+asyncpg://{hv.local_db_username}:{hv.local_db_password}"
        f"@localhost:{hv.local_db_port}/{hv.description_db_name}"
    )
    db_echo: bool = False


core_config = CoreConfig()

# class LaunchDbEngine:
#     def __init__(self, url: str, echo: bool = False):
#         self.engine = create_async_engine(url=url, echo=echo)
#         self.session_factory = async_sessionmaker(
#             bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False
#         )
#
#     def get_scoped_session(self):
#         session = async_scoped_session(
#             session_factory=self.session_factory,
#             scopefunc=current_task,
#         )
#         return session
#
#
# pg_engine = LaunchDbEngine(url=core_config.as_stocktable, echo=core_config.db_echo)

async_engine_pg = create_async_engine(url=core_config.as_stocktable,
                                      echo=core_config.db_echo,
                                      poolclass=NullPool)
async_session_factory = async_sessionmaker(bind=async_engine_pg,
                                           expire_on_commit=False)
AsyncScopedSession = async_scoped_session(session_factory=async_session_factory,
                                          scopefunc=current_task)

