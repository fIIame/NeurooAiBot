from typing import List

from openai import AsyncOpenAI
from database.repositories import UsersMemoriesRepository
from core.utils.ai_utils import AiMemoryUtils


class MemoryService:
    """
    Сервис для работы с памятью пользователя.

    Основные функции:
    - Сохранять значимые сообщения пользователя в базу памяти.
    - Получать релевантные прошлые сообщения по вектору.

    Ограничения:
    - Храним не более 50 сообщений на пользователя.
    """

    @staticmethod
    async def save(
            user_id: int,
            text: str,
            vector: List[float],
            openai_client: AsyncOpenAI,
            model: str
    ) -> None:
        """
        Сохраняет сообщение пользователя в базу памяти, если оно значимо.

        Процесс:
        1. Проверяет через AI, стоит ли сохранять сообщение (AiMemoryUtils.is_ai_should_save).
        2. Если сообщение не значимо, выходит.
        3. Если количество сохраненных сообщений < 50, сохраняет сообщение через UsersMemoriesRepository.

        Args:
            user_id (int): ID пользователя.
            text (str): Сообщение пользователя.
            vector (List[float]): Векторное представление сообщения для поиска по embedding.
            openai_client (AsyncOpenAI): Асинхронный клиент OpenAI для вызова AI.
            model (str): Модель для генерации embedding.
        """
        # Проверка, нужно ли сохранять сообщение
        should_save = await AiMemoryUtils.is_ai_should_save(text, openai_client, model)
        if not should_save:
            return

        # Проверяем текущий счетчик памяти пользователя
        count = await UsersMemoriesRepository.count_memories(user_id)
        if count < 50:
            # Сохраняем память
            await UsersMemoriesRepository.safe_memory(user_id, text, vector, openai_client, model)

    @staticmethod
    async def get(
            user_id: int,
            vector: List[float],
            limit: int = 5
    ) -> List[str]:
        """
        Получает релевантные сообщения из памяти пользователя.

        Args:
            user_id (int): ID пользователя.
            vector (List[float]): Векторное представление запроса для поиска.
            limit (int, optional): Максимальное количество сообщений для возврата. По умолчанию 5.

        Returns:
            List[str]: Список текстов сообщений, наиболее релевантных вектору запроса.
        """
        return await UsersMemoriesRepository.get_memory(user_id, vector, limit)
