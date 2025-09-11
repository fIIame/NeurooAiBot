import asyncio
from typing import List
from openai import AsyncOpenAI

from database.postgres.repositories import UsersMemoriesRepository
from database.redis.repositories import RedisMemoriesRepository
from core.utils.memory_filters import MemoryFilter
from core.utils.ai_utils import AiMemoryUtils


class PermanentMemoryService:
    """
    Сервис управления долгосрочной памятью пользователей (PostgreSQL).

    Назначение:
    - Хранение значимых сообщений пользователя (текст + embedding).
    - Получение наиболее релевантных сообщений по embedding.

    Ограничения:
    - Для каждого пользователя хранится максимум 50 сообщений.
    - Вопросительные сообщения не сохраняются при переполнении памяти.
    """

    @staticmethod
    async def save(user_id: int, text: str, vector: List[float]) -> None:
        """
        Сохраняет сообщение в долгосрочную память при соблюдении условий.

        Условия сохранения:
        1. Если у пользователя ≤ 50 сообщений и текст не является вопросом — сохраняем.
        2. Если сообщений > 50 или текст является вопросом — игнорируем.

        Args:
            user_id (int): Идентификатор пользователя.
            text (str): Сообщение пользователя.
            vector (List[float]): Векторное представление текста.
        """
        count = await UsersMemoriesRepository.count_memories(user_id)
        if count <= 50 and not MemoryFilter.is_question(text):
            await UsersMemoriesRepository.safe_memory(user_id, text, vector)

    @staticmethod
    async def get(user_id: int, vector: List[float], limit: int = 5) -> List[str]:
        """
        Извлекает наиболее релевантные сообщения пользователя из долгосрочной памяти.

        Args:
            user_id (int): Идентификатор пользователя.
            vector (List[float]): Вектор текущего сообщения.
            limit (int, optional): Максимальное количество сообщений. По умолчанию 5.

        Returns:
            List[str]: Список текстов сообщений, отсортированных по релевантности.
        """
        return await UsersMemoriesRepository.get_memory(user_id, vector, limit)

    @staticmethod
    async def build_context_and_save(
        user_id: int,
        user_text: str,
        openai_client: AsyncOpenAI,
        filter_model: str,
        embedding_model: str
    ) -> str:
        """
        Формирует контекст из долгосрочной памяти и сохраняет новое сообщение.

        Логика:
        1. Проверяет значимость сообщения через `MemoryFilter`.
        2. Генерирует embedding для текста.
        3. Извлекает релевантные сообщения пользователя.
        4. Асинхронно сохраняет новое сообщение и его embedding.

        Args:
            user_id (int): Идентификатор пользователя.
            user_text (str): Текст сообщения.
            openai_client (AsyncOpenAI): Клиент OpenAI.
            filter_model (str): Модель для фильтрации значимых сообщений.
            embedding_model (str): Модель для генерации embedding текста.

        Returns:
            str: Контекст релевантных сообщений для передачи в AI.
        """
        context = ""

        if await MemoryFilter.is_required_for_permanent_memory(user_text, openai_client, filter_model):
            vector = await AiMemoryUtils.generate_embedding(user_text, openai_client, embedding_model)
            memories = await PermanentMemoryService.get(user_id, vector)
            if memories:
                context = "\nPermanent memories:\n" + "\n".join(memories)

            # Сохраняем сообщение и embedding асинхронно
            asyncio.create_task(PermanentMemoryService.save(user_id, user_text, vector))

        return context


class TemporaryMemoryService:
    """
    Сервис управления краткосрочной памятью пользователей (Redis).

    Назначение:
    - Хранение последних реплик диалога (пользователь + бот).
    - Быстро формирует контекст последних сообщений для AI.

    Ограничения:
    - Хранится ограниченное количество сообщений.
    """

    @staticmethod
    async def save(user_id: int, user_text: str, bot_reply: str) -> None:
        """
        Сохраняет связку "пользователь + бот" в Redis.

        Args:
            user_id (int): Идентификатор пользователя.
            user_text (str): Сообщение пользователя.
            bot_reply (str): Ответ модели.
        """
        await RedisMemoriesRepository.save_memory(user_id, f"User: {user_text}")
        await RedisMemoriesRepository.save_memory(user_id, f"Bot: {bot_reply}")

    @staticmethod
    async def get(user_id: int) -> List[str]:
        """
        Извлекает историю диалога пользователя из Redis.

        Args:
            user_id (int): Идентификатор пользователя.

        Returns:
            List[str]: Список сообщений в формате ["User: ...", "Bot: ...", ...].
        """
        return await RedisMemoriesRepository.get_memories(user_id)

    @staticmethod
    async def build_context(user_id: int) -> str:
        """
        Формирует строковый контекст последних сообщений из Redis.

        Args:
            user_id (int): Идентификатор пользователя.

        Returns:
            str: Контекст вида "Temporary memories:\nUser: ...\nBot: ...",
                 или пустая строка, если сообщений нет.
        """
        temporary_context = await TemporaryMemoryService.get(user_id)
        return "Temporary memories:\n" + "\n".join(temporary_context) if temporary_context else ""


class MemoryContextService:
    """
    Сервис объединения краткосрочной (Redis) и долгосрочной (PostgreSQL) памяти.
    Формирует единый контекст для передачи AI.
    """

    @staticmethod
    async def build_full_context(
        user_id: int,
        user_text: str,
        openai_client: AsyncOpenAI,
        filter_model: str,
        embedding_model: str
    ) -> str:
        """
        Формирует полный контекст для AI.

        Логика:
        1. Достаёт краткосрочную память (последние сообщения из Redis).
        2. Достаёт долгосрочную память (релевантные сообщения из PostgreSQL, если нужно).
        3. Объединяет их в единую строку для передачи модели.
        4. Сохраняет текущее сообщение в обе памяти.

        Args:
            user_id (int): Идентификатор пользователя.
            user_text (str): Сообщение пользователя.
            openai_client (AsyncOpenAI): Клиент OpenAI.
            filter_model (str): Модель для фильтрации значимых сообщений.
            embedding_model (str): Модель для генерации embedding текста.

        Returns:
            str: Полный контекст сообщений (краткосрочные + долгосрочные).
        """
        temporary_context = await TemporaryMemoryService.build_context(user_id)
        permanent_context = await PermanentMemoryService.build_context_and_save(
            user_id, user_text, openai_client, filter_model, embedding_model
        )
        return temporary_context + "\n\n" + permanent_context