from database.database import DatabaseConfig
from database.repositories import AsyncRepository


async def init_db(asyncpg_url: str):
    DatabaseConfig.init_db(asyncpg_url)

    await AsyncRepository.create_tables()
