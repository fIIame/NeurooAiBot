import logging
from typing import Optional

from sqlalchemy import update, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

from database.database import DatabaseConfig, Base
from database.models import UsersOrm

logger = logging.getLogger(__name__)


class AsyncRepository:
    @staticmethod
    async def create_tables() -> None:
        try:
            async with DatabaseConfig.get_engine().begin() as connection:
                await connection.run_sync(Base.metadata.create_all)
                logger.info("Таблицы базы данных успешно созданы")

        except SQLAlchemyError as e:
            logger.error(f"Ошибка SQLAlchemy при создании таблиц базы данных: {e}")

        except Exception as e:
            logger.error(f"Неожиданная ошибка при создании таблиц базы данных: {e}")


class UsersRepository(AsyncRepository):

    @staticmethod
    async def add_user(user_id: int, first_name: str) -> None:
        try:
            async with DatabaseConfig.get_session() as session:
                query = (
                    insert(UsersOrm)
                    .values(id=user_id, first_name=first_name)
                    .on_conflict_do_nothing(index_elements=['id'])
                )
                await session.execute(query)
                await session.commit()

        except SQLAlchemyError as e:
            logger.error(f"Ошибка SQLAlchemy при добавлении пользователя: {e}")

        except Exception as e:
            logger.error(f"Неожиданная ошибка при добавлении пользователя: {e}")

    @staticmethod
    async def set_user_active(user_id: int) -> None:
        try:
            async with DatabaseConfig.get_session() as session:
                query = update(UsersOrm).filter_by(id=user_id).values(is_activate=True)
                await session.execute(query)
                await session.commit()

        except SQLAlchemyError as e:
            logger.error(f"Не удалось активировать пользователя {user_id}: {e}")

        except Exception as e:
            logger.error(f"Неожиданная ошибка при активации пользователя {user_id}: {e}")

    @staticmethod
    async def is_user_activated(user_id: int) -> Optional[bool]:
        try:
            async with DatabaseConfig.get_session() as session:
                query = select(UsersOrm).filter_by(id=user_id)
                result = await session.execute(query)
                user = result.scalars().first()
                return user.is_activate if user else False

        except SQLAlchemyError as e:
            logger.error(f"Не удалось получить статус активации пользователя {user_id}: {e}")

        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении статуса активации пользователя {user_id}: {e}")
