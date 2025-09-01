from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


class DatabaseConfig:
    __async_engine: AsyncEngine = None
    __async_session_maker: async_sessionmaker = None

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


    @classmethod
    def async_session_maker(cls) -> AsyncSession:
        if cls.__async_session_maker:
            return cls.__async_session_maker()



class Base(DeclarativeBase):
    pass