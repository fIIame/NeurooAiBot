import logging
from typing import Optional, List

from sqlalchemy import update, select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from openai import AsyncOpenAI

from database.database import DatabaseConfig, Base
from database.models import UsersOrm, UsersMemoriesOrm
from core.lexicon import LOGGING_LEXICON
from core.utils.ai_utils import AiMemoryUtils

logger = logging.getLogger(__name__)


class AsyncRepository:
    @staticmethod
    async def create_tables() -> None:
        try:
            async with DatabaseConfig.get_engine().begin() as connection:
                await connection.run_sync(Base.metadata.create_all)
                logger.info(LOGGING_LEXICON["logging"]["database"]["tables"]["created"])

        except SQLAlchemyError as e:
            logger.error(LOGGING_LEXICON["logging"]["database"]["tables"]["create_sqlalchemy_error"].format(e))

        except Exception as e:
            logger.error(LOGGING_LEXICON["logging"]["database"]["tables"]["create_unexpected_error"].format(e))


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
            logger.error(LOGGING_LEXICON["logging"]["database"]["tables"]["add_sqlalchemy_error"].format(e))

        except Exception as e:
            logger.error(LOGGING_LEXICON["logging"]["database"]["tables"]["add_unexpected_error"].format(e))

    @staticmethod
    async def set_user_active(user_id: int) -> None:
        try:
            async with DatabaseConfig.get_session() as session:
                query = update(UsersOrm).filter_by(id=user_id).values(is_activate=True)
                await session.execute(query)
                await session.commit()

        except SQLAlchemyError as e:
            logger.error(LOGGING_LEXICON["logging"]["database"]["tables"]["activate_sqlalchemy_error"].format(e))

        except Exception as e:
            logger.error(LOGGING_LEXICON["logging"]["database"]["tables"]["activate_unexpected_error"].format(e))

    @staticmethod
    async def is_user_activated(user_id: int) -> Optional[bool]:
        try:
            async with DatabaseConfig.get_session() as session:
                query = select(UsersOrm).filter_by(id=user_id)
                result = await session.execute(query)
                user = result.scalars().first()
                return user.is_activate if user else False

        except SQLAlchemyError as e:
            logger.error(LOGGING_LEXICON["logging"]["database"]["tables"]["status_sqlalchemy_error"].format(e))

        except Exception as e:
            logger.error(LOGGING_LEXICON["logging"]["database"]["tables"]["status_unexpected_error"].format(e))


class UsersMemoriesRepository(AsyncRepository):
    @staticmethod
    async def safe_memory(user_id: int, text: str, openai_client: AsyncOpenAI, model: str) -> None:
        if await AiMemoryUtils.is_ai_should_save(text=text, openai_client=openai_client, model=model):
            vector = await AiMemoryUtils.get_vector(text, openai_client)
            async with DatabaseConfig.get_session() as session:
                query = insert(UsersMemoriesOrm).values(user_id=user_id, message_text=text, embedding=vector)
                await session.execute(query)
                await session.commit()

    @staticmethod
    async def get_memory(user_id: int, text: str, openai_client: AsyncOpenAI, limit: int = 5) -> List[str]:
        vector = await AiMemoryUtils.get_vector(text, openai_client)

        async with DatabaseConfig.get_session() as session:
            query = (
                select(UsersMemoriesOrm.message_text).
                filter_by(user_id=user_id).
                order_by(UsersMemoriesOrm.embedding.op("<->")(vector))
                .limit(limit)
            )

            result = await session.execute(query)
            rows = result.scalars().all()
            return list(rows)

    @staticmethod
    async def count_memories(user_id: int) -> int:
        async with DatabaseConfig.get_session() as session:
            query = select(func.count()).select_from(UsersMemoriesOrm).filter_by(user_id=user_id)
            result = await session.execute(query)
            return result.scalar()
