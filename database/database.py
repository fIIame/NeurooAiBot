import logging
from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from core.exceptions.database import InitializationError
from core.lexicon import LOGGING_LEXICON


logger = logging.getLogger(__name__)


class DatabaseConfig:
    __async_engine: Optional["AsyncEngine"] = None
    __async_session_maker: Optional["async_sessionmaker"] = None

    @classmethod
    def init_db(cls, database_url: str):
        cls.__async_engine = create_async_engine(
            database_url,
            echo=False
        )
        cls.__async_session_maker = async_sessionmaker(cls.__async_engine)

    @classmethod
    def get_engine(cls) -> AsyncEngine:
        if cls.__async_engine:
            return cls.__async_engine
        logger.critical(LOGGING_LEXICON["logging"]["database"]["init"]["fail"])
        raise InitializationError()

    @classmethod
    def get_session(cls) -> AsyncSession:
        if cls.__async_session_maker:
            return cls.__async_session_maker()
        logger.critical(LOGGING_LEXICON["logging"]["database"]["init"]["fail"])
        raise InitializationError()


class Base(DeclarativeBase):
    pass