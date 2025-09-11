import logging
from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from core.exceptions.database import InitializationError
from core.lexicon import LOGGING_LEXICON


logger = logging.getLogger(__name__)


class PostgresManager:
    """
    Менеджер асинхронного подключения к базе данных Postgres через SQLAlchemy.

    Этот класс обеспечивает централизованное хранение движка и фабрики сессий,
    чтобы их можно было использовать во всем приложении без повторной инициализации.

    Атрибуты класса:
        __async_engine (Optional[AsyncEngine]): Асинхронный движок SQLAlchemy для выполнения запросов.
        __async_session_maker (Optional[async_sessionmaker]): Фабрика для создания асинхронных сессий.
    """

    __async_engine: Optional[AsyncEngine] = None
    __async_session_maker: Optional[async_sessionmaker] = None

    @classmethod
    def init(cls, postgres_url: str) -> None:
        """
        Инициализация подключения к базе данных Postgres.

        Создает асинхронный движок и фабрику сессий для последующего использования
        во всех слоях приложения.

        Args:
            postgres_url (str): URL подключения к базе Postgres.
                                Пример: "postgresql+asyncpg://user:pass@host:port/dbname"
        """
        cls.__async_engine = create_async_engine(
            postgres_url,
            echo=False  # Выключает логирование SQL-запросов в консоль
        )
        cls.__async_session_maker = async_sessionmaker(cls.__async_engine)

    @classmethod
    def get_engine(cls) -> AsyncEngine:
        """
        Возвращает асинхронный движок SQLAlchemy.

        Этот движок используется для выполнения всех SQL-запросов в приложении.

        Returns:
            AsyncEngine: Асинхронный движок для работы с Postgres.

        Raises:
            InitializationError: Если движок не был инициализирован вызовом `init`.
        """
        if cls.__async_engine:
            return cls.__async_engine

        logger.critical(LOGGING_LEXICON["logging"]["database"]["init"]["fail"])
        raise InitializationError()

    @classmethod
    def get_session(cls) -> AsyncSession:
        """
        Создает и возвращает асинхронную сессию для работы с базой данных.

        Используется для выполнения транзакций и запросов в репозиториях.

        Returns:
            AsyncSession: Асинхронная сессия SQLAlchemy.

        Raises:
            InitializationError: Если фабрика сессий не была инициализирована вызовом `init`.
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
