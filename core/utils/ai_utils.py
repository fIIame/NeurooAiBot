from typing import List

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from core.lexicon import SYSTEM_PROMPTS_LEXICON


class AiMemoryUtils:
    """
    Утилиты для работы с памятью пользователя.

    Основные функции:
    - Генерация векторного представления текста (embedding) для хранения в памяти.
    - Оценка значимости сообщения через AI (для фильтрации важного контента).
    """

    # ------------------- Генерация embedding -------------------

    @staticmethod
    async def generate_embedding(text: str, openai_client: AsyncOpenAI, model: str) -> List[float]:
        """
        Генерирует векторное представление текста пользователя.

        Args:
            text (str): Текст сообщения.
            openai_client (AsyncOpenAI): Асинхронный клиент OpenAI.
            model (str): Модель для генерации embedding.

        Returns:
            List[float]: Векторное представление текста (embedding).
        """
        emb = await openai_client.embeddings.create(
            model=model,
            input=text
        )
        return emb.data[0].embedding

    # ------------------- Оценка важности через AI -------------------

    @staticmethod
    async def ask_ai_is_important(text: str, openai_client: AsyncOpenAI, model: str) -> str:
        """
        Определяет, следует ли сохранять сообщение, с помощью AI.

        Логика:
        1. Использует системный промпт из lexicon для правил фильтрации.
        2. Отправляет текст пользователя как пользовательское сообщение.
        3. Получает ответ модели: "да" или "нет".

        Args:
            text (str): Текст сообщения пользователя.
            openai_client (AsyncOpenAI): Асинхронный клиент OpenAI.
            model (str): Модель для генерации ответа (например, "GPT-5-mini").

        Returns:
            str: Ответ AI в нижнем регистре ("да" или "нет"), указывающий, стоит ли сохранять сообщение.
        """
        messages = [
            ChatCompletionSystemMessageParam(
                role="system",
                content=SYSTEM_PROMPTS_LEXICON["system_prompts"]["memory_filter"]
            ),
            ChatCompletionUserMessageParam(
                role="user",
                content=text
            )
        ]

        response = await openai_client.chat.completions.create(
            model=model,
            messages=messages
        )

        return response.choices[0].message.content.strip().lower()
