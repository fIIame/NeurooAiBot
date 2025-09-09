from typing import List, Optional

from openai import AsyncOpenAI

from core.lexicon import SYSTEM_PROMPTS_LEXICON


class AIService:
    """
    Сервис для взаимодействия с AI (OpenAI).

    Отвечает за:
    - Формирование сообщений для ChatCompletion API (системные правила, память, сообщение пользователя).
    - Вызов модели OpenAI и возврат ответа.
    """

    @staticmethod
    async def get_reply(
        user_text: str,
        memories_context: Optional[str],
        openai_client: AsyncOpenAI,
        model: str
    ) -> str:
        """
        Получает ответ от модели AI на сообщение пользователя.

        Логика:
        1. Добавляем системный промпт с правилами базового ассистента.
        2. Если есть память пользователя — добавляем её как системный промпт.
        3. Добавляем само сообщение пользователя.
        4. Отправляем запрос в OpenAI ChatCompletion API.
        5. Возвращаем текст ответа модели.

        Args:
            user_text (str): Текстовое сообщение пользователя.
            memories_context (Optional[str]): Контекст памяти пользователя
                                                (список прошлых сообщений, объединённых в строку).
            openai_client (AsyncOpenAI): Асинхронный клиент OpenAI.
            model (str): Название модели для генерации ответа (например, "gpt-5-mini").

        Returns:
            str: Ответ модели AI. Если ответа нет, возвращает fallback сообщение.
        """
        # --- Формируем список сообщений для Chat API ---
        messages: List = [
            # Базовое поведение ассистента
            {"role": "system", "content": SYSTEM_PROMPTS_LEXICON["system_prompts"]["base_assistant"]},
        ]

        # Добавляем память (если есть)
        if memories_context:
            messages.append({
                "role": "system",
                "content": SYSTEM_PROMPTS_LEXICON["system_prompts"]["rule_memory"].format(memories_context)
            })

        # Сообщение пользователя
        messages.append({"role": "user", "content": user_text})

        # --- Запрос в OpenAI ---
        response = await openai_client.chat.completions.create(
            model=model,
            messages=messages
        )

        # --- Извлекаем текст ответа ---
        ai_message = response.choices[0].message.content

        # --- Fallback (если AI не вернул текст) ---
        return ai_message.strip() if ai_message else "Извини, я не смог сгенерировать ответ 😔"