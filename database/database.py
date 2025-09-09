import logging
from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from core.exceptions.database import InitializationError
from core.lexicon import LOGGING_LEXICON


logger = logging.getLogger(__name__)


class DatabaseConfig:
    """
    Конфигурация базы данных для асинхронного взаимодействия через SQLAlchemy.

    Атрибуты класса:
        __async_engine (Optional[AsyncEngine]): Асинхронный движок SQLAlchemy.
        __async_session_maker (Optional[async_sessionmaker]): Фабрика сессий для работы с базой.
    """

    __async_engine: Optional[AsyncEngine] = None
    __async_session_maker: Optional[async_sessionmaker] = None

    @classmethod
    def init_db(cls, database_url: str) -> None:
        """
        Инициализация подключения к базе данных.

        Создает асинхронный движок и фабрику сессий.

        Args:
            database_url (str): URL подключения к базе данных.
                                Например: "postgresql+asyncpg://user:pass@host:port/dbname"
        """
        cls.__async_engine = create_async_engine(
            database_url,
            echo=False  # Выключает логирование SQL-запросов
        )
        cls.__async_session_maker = async_sessionmaker(cls.__async_engine)

    @classmethod
    def get_engine(cls) -> AsyncEngine:
        """
        Получает асинхронный движок SQLAlchemy.

        Returns:
            AsyncEngine: Движок для выполнения запросов к базе.

        Raises:
            InitializationError: Если движок не был инициализирован.
        """
        if cls.__async_engine:
            return cls.__async_engine

        logger.critical(LOGGING_LEXICON["logging"]["database"]["init"]["fail"])
        raise InitializationError()

    @classmethod
    def get_session(cls) -> AsyncSession:
        """
        Создает и возвращает асинхронную сессию для работы с базой.

        Returns:
            AsyncSession: Асинхронная сессия SQLAlchemy.

        Raises:
            InitializationError: Если фабрика сессий не была инициализирована.
        """
        if cls.__async_session_maker:
            return cls.__async_session_maker()

        logger.critical(LOGGING_LEXICON["logging"]["database"]["init"]["fail"])
        raise InitializationError()


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.

    Наследуя этот класс, модели автоматически получают метаданные для создания таблиц.
    """
    pass
