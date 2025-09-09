from typing import List
from openai import AsyncOpenAI

from database.repositories import UsersMemoriesRepository
from core.utils.ai_utils import AiMemoryUtils


class MemoryService:
    """
    Сервис для управления пользовательской памятью.

    Возможности:
    - Сохраняет значимые сообщения пользователя в базу (embedding + текст).
    - Извлекает наиболее релевантные прошлые сообщения по векторному поиску.

    Ограничения:
    - Для каждого пользователя хранится максимум 50 сообщений.
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
        Сохраняет сообщение пользователя в память, если оно важно для последующих диалогов.

        Логика:
        1. Проверяем, является ли сообщение значимым:
           - Содержит ли ключевые слова (правило).
           - Если нет — уточняем у AI.
        2. Игнорируем вопросы (они нужны только для поиска, но не для сохранения).
        3. Проверяем лимит памяти (50 сообщений).
        4. Если условия выполнены — сохраняем через репозиторий.

        Args:
            user_id (int): ID пользователя.
            text (str): Сообщение пользователя.
            vector (List[float]): Векторное представление текста.
            openai_client (AsyncOpenAI): Асинхронный клиент OpenAI.
            model (str): Модель, используемая для фильтрации (решение о сохранении).
        """
        # --- Определяем, стоит ли сохранять ---
        if AiMemoryUtils.contains_important_keyword(text):
            should_save = True
        else:
            should_save = await AiMemoryUtils.ask_ai_is_important(text, openai_client, model) == "да"

        # --- Проверяем лимит и тип сообщения ---
        count = await UsersMemoriesRepository.count_memories(user_id)
        if count < 50 and should_save and not AiMemoryUtils.is_question(text):
            await UsersMemoriesRepository.safe_memory(user_id, text, vector, openai_client, model)

    @staticmethod
    async def get(
        user_id: int,
        vector: List[float],
        limit: int = 5
    ) -> List[str]:
        """
        Извлекает релевантные воспоминания пользователя из памяти.

        Args:
            user_id (int): ID пользователя.
            vector (List[float]): Вектор запроса (embedding текущего сообщения).
            limit (int, optional): Максимальное количество воспоминаний. По умолчанию 5.

        Returns:
            List[str]: Список сообщений из памяти, упорядоченных по близости к запросу.
        """
        return await UsersMemoriesRepository.get_memory(user_id, vector, limit)
