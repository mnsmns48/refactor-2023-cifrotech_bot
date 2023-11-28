from pydantic.v1 import BaseSettings
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
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


core_config = CoreConfig()
async_engine = create_async_engine(url=core_config.as_stocktable, poolclass=NullPool)
async_session_pg = async_sessionmaker(bind=async_engine, expire_on_commit=False)
