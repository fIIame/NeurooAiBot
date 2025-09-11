from typing import Optional
from redis.asyncio import from_url, Redis


class RedisManager:
    """
    Менеджер для работы с асинхронным клиентом Redis.

    Основные функции:
    - Инициализация единственного клиента Redis.
    - Получение доступа к клиенту для выполнения команд Redis.

    Примечание:
    Использует паттерн Singleton для единственного экземпляра клиента.
    """
    __client: Optional[Redis] = None

    @classmethod
    def init(cls, redis_url: str) -> None:
        """
        Инициализирует Redis-клиент с указанным URL.

        Args:
            redis_url (str): URL для подключения к Redis (например, "redis://localhost:6379/0").
        """
        cls.__client = from_url(redis_url, decode_responses=True)

    @classmethod
    def get_client(cls) -> Optional[Redis]:
        """
        Возвращает инициализированный Redis-клиент.

        Returns:
            Optional[Redis]: Объект Redis, если был инициализирован, иначе None.
        """
        return cls.__client
