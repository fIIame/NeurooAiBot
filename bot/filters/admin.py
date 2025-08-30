from typing import List

from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Message, admin_ids: List[int]) -> bool:
        return message.from_user.id in admin_ids
