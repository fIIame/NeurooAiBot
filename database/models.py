from typing import Annotated
from datetime import datetime

from sqlalchemy import String, BIGINT, BOOLEAN, TIMESTAMP
from sqlalchemy.orm import mapped_column, Mapped
from pgvector.sqlalchemy import Vector

from database.database import Base


# Удобный алиас для строк фиксированной длины
str_100 = Annotated[str, mapped_column(String(100))]


class UsersOrm(Base):
    """
    ORM-модель для таблицы пользователей.

    Колонки:
    - id: уникальный идентификатор пользователя (Telegram user_id)
    - first_name: имя пользователя (до 100 символов)
    - is_activate: флаг активации пользователя (True, если пользователь прошёл активацию)
    """
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    first_name: Mapped[str_100]
    is_activate: Mapped[bool] = mapped_column(BOOLEAN, default=False)


class UsersMemoriesOrm(Base):
    """
    ORM-модель для таблицы памяти пользователей.

    Колонки:
    - id: уникальный идентификатор записи памяти
    - user_id: ID пользователя (связь с UsersOrm)
    - message_text: текстовое сообщение пользователя (уникальное)
    - embedding: векторное представление сообщения (для поиска по схожести)
    - created_at: дата и время создания записи
    """
    __tablename__ = 'users_memories'

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    user_id: Mapped[int] = mapped_column(BIGINT, nullable=False)
    message_text: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    embedding: Mapped[list] = mapped_column(Vector(1536), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
