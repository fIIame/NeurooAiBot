from database.redis.manager import RedisManager


class RedisMemoriesRepository:
    """
    Репозиторий для работы с краткосрочной памятью пользователей в Redis.

    Хранит историю сообщений чата пользователя и позволяет получать последние N сообщений.
    """

    @staticmethod
    async def save_memory(user_id: int, text: str, limit: int = 10) -> None:
        """
        Сохраняет сообщение пользователя в Redis.

        Логика:
        1. Формирует ключ в формате "chat:{user_id}:history".
        2. Добавляет новое сообщение в начало списка (LPUSH).
        3. Обрезает список до указанного лимита (LTRIM).

        Args:
            user_id (int): Идентификатор пользователя.
            text (str): Сообщение для сохранения.
            limit (int, optional): Максимальное количество сообщений в истории. По умолчанию 10.
        """
        client = RedisManager.get_client()
        if client is None:
            raise RuntimeError("Redis client is not initialized")
        key = f"chat:{user_id}:history"
        await client.lpush(key, text)
        await client.ltrim(key, 0, limit - 1)

    @staticmethod
    async def get_memories(user_id: int, limit: int = 10) -> list[str]:
        """
        Получает последние сообщения пользователя из Redis.

        Логика:
        1. Формирует ключ в формате "chat:{user_id}:history".
        2. Возвращает последние `limit` сообщений (LRANGE).

        Args:
            user_id (int): Идентификатор пользователя.
            limit (int, optional): Количество сообщений для извлечения. По умолчанию 10.

        Returns:
            list[str]: Список сообщений пользователя в порядке от последних к старым.
        """
        client = RedisManager.get_client()
        if client is None:
            raise RuntimeError("Redis client is not initialized")
        key = f"chat:{user_id}:history"
        return await client.lrange(key, 0, limit - 1)
