from typing import List, Optional
from openai import AsyncOpenAI
from core.lexicon import SYSTEM_PROMPTS_LEXICON


class AIService:
    """
    Сервис взаимодействия с AI (OpenAI).

    Отвечает за:
    - Формирование сообщений для ChatCompletion API, включая системные правила и память пользователя.
    - Отправку запроса в модель OpenAI и возврат ответа.
    """

    @staticmethod
    async def get_reply(
        user_text: str,
        memories_context: Optional[str],
        openai_client: AsyncOpenAI,
        model: str
    ) -> str:
        """
        Получает ответ модели AI на сообщение пользователя.

        Логика работы:
        1. Формирует системный промпт для базового поведения ассистента.
        2. Добавляет память пользователя как системный контекст, если она есть.
        3. Добавляет текст сообщения пользователя.
        4. Отправляет сформированный запрос в OpenAI ChatCompletion API.
        5. Возвращает ответ модели или fallback-сообщение, если ответ пуст.

        Args:
            user_text (str): Сообщение пользователя.
            memories_context (Optional[str]): Контекст памяти пользователя
                                              (объединённые прошлые сообщения).
            openai_client (AsyncOpenAI): Асинхронный клиент OpenAI.
            model (str): Название модели для генерации ответа (например, "gpt-5-mini").

        Returns:
            str: Текст ответа модели. Если AI не вернул текст, возвращается fallback-сообщение.
        """
        # --- Сбор сообщений для Chat API ---
        messages: List = [
            # Базовое поведение ассистента
            {"role": "system", "content": SYSTEM_PROMPTS_LEXICON["system_prompts"]["base_assistant"]}
        ]

        # Добавляем память пользователя как системный контекст
        if memories_context:
            messages.append({
                "role": "system",
                "content": SYSTEM_PROMPTS_LEXICON["system_prompts"]["rule_memory"].format(memories_context)
            })

        # Добавляем сообщение пользователя
        messages.append({"role": "user", "content": user_text})

        # --- Отправка запроса в OpenAI ---
        response = await openai_client.chat.completions.create(
            model=model,
            messages=messages
        )

        # --- Извлечение текста ответа модели ---
        ai_message = response.choices[0].message.content

        # --- Fallback, если ответ пуст ---
        return ai_message.strip() if ai_message else "Извини, я не смог сгенерировать ответ 😔"
