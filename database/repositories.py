from sqlalchemy import select, update

from database.database import DatabaseConfig, Base
from database.models import UsersOrm


class AsyncRepository:
    @staticmethod
    async def create_tables() -> None:
        async with DatabaseConfig.get_engine().begin() as connection:
            await connection.run_sync(Base.metadata.create_all)



class UsersRepository(AsyncRepository):

    @staticmethod
    async def activate_user(user_id: int) -> None:
        async with DatabaseConfig.get_session().begin as session:
            query = await update(UsersOrm).filter_by(id=user_id).values(is_activate=True)
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def is_user_activated(user_id: int) -> bool:
        async with DatabaseConfig.get_session() as session:
            query = await select(UsersOrm).filter_by(id=user_id)
            result = await session.execute(query)
            user = result.scalars().first()
            return user.is_activated
