from database.postgres.manager import PostgresManager
from database.postgres.repositories import AsyncRepository
from database.redis.manager import RedisManager


async def setup_db_connections(postgres_url: str, redis_url: str) -> None:
    """
    Настройка и инициализация всех баз данных, используемых ботом.

    Выполняет следующие действия:
    1. Создает подключение к PostgreSQL через `PostgresManager`.
    2. Создает подключение к Redis через `RedisManager`.
    3. Создает все таблицы в PostgreSQL, если они еще не существуют.

    Args:
        postgres_url (str): Асинхронный URL подключения к PostgreSQL.
                            Пример: "postgresql+asyncpg://user:password@localhost:5432/db_name"
        redis_url (str): URL подключения к Redis. Пример: "redis://localhost:6379"

    Raises:
        Любые исключения, возникающие при инициализации баз данных или создании таблиц,
        будут проброшены дальше.

    Example:
        await setup_db_connections(
            postgres_url="postgresql+asyncpg://user:password@localhost:5432/db_name",
            redis_url="redis://localhost:6379"
        )
    """
    # --- Инициализация подключений к базам данных ---
    PostgresManager.init(postgres_url)
    RedisManager.init(redis_url)

    # --- Создание таблиц PostgreSQL, если они ещё не созданы ---
    await AsyncRepository.create_tables()
