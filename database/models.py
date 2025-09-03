from typing import Annotated
from datetime import datetime

from sqlalchemy import String, BIGINT, BOOLEAN, TIMESTAMP
from sqlalchemy.orm import mapped_column, Mapped
from pgvector.sqlalchemy import Vector

from database.database import Base


str_100 = Annotated[str, mapped_column(String(100))]


class UsersOrm(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    first_name: Mapped[str_100]
    is_activate: Mapped[bool] = mapped_column(BOOLEAN, default=False)


class UsersMemoriesOrm(Base):
    __tablename__ = 'users_memories'

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    user_id: Mapped[int] = mapped_column(BIGINT, nullable=False)
    message_text: Mapped[str] = mapped_column(String, nullable=False)
    embedding: Mapped[list] = mapped_column(Vector(1536), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
