from typing import List
from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsAdminFilter(BaseFilter):
    """
    Фильтр для проверки, является ли пользователь администратором.

    Используется в роутерах Aiogram для ограничения команд/доступа.

    Args:
        message (Message): Сообщение пользователя.
        admin_ids (List[int]): Список Telegram ID администраторов.

    Returns:
        bool: True, если пользователь в списке admin_ids, иначе False.
    """

    async def __call__(self, message: Message, admin_ids: List[int]) -> bool:
        return message.from_user.id in admin_ids