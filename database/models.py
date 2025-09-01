from typing import Annotated

from sqlalchemy import String, BIGINT, BOOLEAN
from sqlalchemy.orm import mapped_column, Mapped

from database.database import Base


str_100 = Annotated[str, mapped_column(String(100))]


class UsersOrm(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    first_name: Mapped[str_100]
    is_activate: Mapped[bool] = mapped_column(BOOLEAN, default=False)
