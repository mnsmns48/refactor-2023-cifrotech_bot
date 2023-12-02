from asyncio import current_task

from pydantic.v1 import BaseSettings
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker, async_scoped_session

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

async_engine_pg = create_async_engine(url=core_config.as_stocktable,
                                      echo=core_config.db_echo,
                                      poolclass=NullPool)
async_session_factory_pg = async_sessionmaker(bind=async_engine_pg,
                                              expire_on_commit=False)
AsyncScopedSessionPG = async_scoped_session(session_factory=async_session_factory_pg,
                                            scopefunc=current_task)

async_engine_desc = create_async_engine(url=core_config.phones_desc_db,
                                        echo=core_config.db_echo,
                                        poolclass=NullPool)
async_session_factory_desc = async_sessionmaker(bind=async_engine_desc,
                                                expire_on_commit=False)
AsyncScopedSessionDesc = async_scoped_session(session_factory=async_session_factory_desc,
                                              scopefunc=current_task)
