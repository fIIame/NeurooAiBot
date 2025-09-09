from database.database import DatabaseConfig
from database.repositories import AsyncRepository


async def init_db(asyncpg_url: str) -> None:
    """
    Инициализация базы данных для бота.

    Шаги:
    1. Настройка конфигурации подключения к базе через DatabaseConfig.
    2. Создание всех таблиц, если они еще не созданы.

    Args:
        asyncpg_url (str): URL подключения к PostgreSQL для асинхронного драйвера asyncpg.

    Example:
        await init_db("postgresql+asyncpg://user:password@localhost:5432/db_name")
    """
    # --- Инициализация конфигурации базы данных ---
    DatabaseConfig.init_db(asyncpg_url)

    # --- Создание таблиц, определенных в Base.metadata ---
    await AsyncRepository.create_tables()
