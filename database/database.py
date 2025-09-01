import logging
from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from core.exceptions.database import InitializationError


logger = logging.getLogger(__name__)


class DatabaseConfig:
    __async_engine: Optional["AsyncEngine"] = None
    __async_session_maker: Optional["async_sessionmaker"] = None

    @classmethod
    def init_db(cls, database_url: str):
        cls.__async_engine = create_async_engine(
            database_url,
            echo=True
        )
        cls.__async_session_maker = async_sessionmaker(cls.__async_engine)

    @classmethod
    def get_engine(cls) -> AsyncEngine:
        if cls.__async_engine:
            return cls.__async_engine
        logger.critical("Движок базы данных не инициализирован. Попытка обращения к базе без инициализации")
        raise InitializationError()

    @classmethod
    def get_session(cls) -> AsyncSession:
        if cls.__async_session_maker:
            return cls.__async_session_maker()
        logger.critical("Движок базы данных не инициализирован. Попытка обращения к базе без инициализации")
        raise InitializationError()


class Base(DeclarativeBase):
    pass