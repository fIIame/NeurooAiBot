from typing import List

from openai import AsyncOpenAI

from core.lexicon import SYSTEM_PROMPTS_LEXICON


class AIService:
    """
    Сервис для взаимодействия с AI (OpenAI).

    Основные функции:
    - Формирует контекст из системных сообщений и памяти пользователя.
    - Отправляет запрос к модели и получает ответ.
    """

    @staticmethod
    async def get_reply(
            user_text: str,
            memories_context: str,
            openai_client: AsyncOpenAI,
            model: str
    ) -> str:
        """
        Получает ответ AI на сообщение пользователя с учетом контекста памяти.

        Процесс:
        1. Формирует список сообщений для OpenAI:
           - Системный промпт базового ассистента.
           - Системный промпт с памятью пользователя.
           - Сообщение пользователя.
        2. Отправляет запрос к модели через openai_client.chat.completions.create.
        3. Возвращает текст ответа AI.

        Args:
            user_text (str): Сообщение пользователя.
            memories_context (str): Контекст памяти пользователя (например, прошлые сообщения).
            openai_client (AsyncOpenAI): Асинхронный клиент OpenAI для вызова AI.
            model (str): Модель для генерации ответа (например, GPT-5-mini).

        Returns:
            str: Ответ модели AI на сообщение пользователя.
        """
        # Формируем сообщения для Chat API
        messages: List = [
            # Системный промпт с базовым поведением ассистента
            {"role": "system", "content": SYSTEM_PROMPTS_LEXICON["system_prompts"]["base_assistant"]},

            # Системный промпт с памятью пользователя
            {"role": "system", "content": SYSTEM_PROMPTS_LEXICON["system_prompts"]["rule_memory"].format(memories_context)},

            # Сообщение пользователя
            {"role": "user", "content": user_text}
        ]

        # Запрос к OpenAI
        response = await openai_client.chat.completions.create(
            model=model,
            messages=messages
        )

        # Возвращаем текст ответа
        return response.choices[0].message.content
