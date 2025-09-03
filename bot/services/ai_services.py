from typing import List

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

class AIService:

    @staticmethod
    async def get_reply(user_text: str, memories_context: str, openai_client: AsyncOpenAI) -> str:
        messages: List = [
            ChatCompletionSystemMessageParam(role="system", content="Базовый умный помощник"),
        ]

        if memories_context:
            # Добавляем память пользователя как отдельное системное сообщение
            messages.append(
                ChatCompletionSystemMessageParam(role="system", content=f"Память пользователя:\n{memories_context}")
            )

        messages.append(
            ChatCompletionUserMessageParam(role="user", content=user_text)
        )

        response = await openai_client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages
        )

        return response.choices[0].message.content
