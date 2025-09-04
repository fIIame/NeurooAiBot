from typing import List, Optional

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from core.lexicon import SYSTEM_PROMPTS_LEXICON


class AIService:

    @staticmethod
    async def get_reply(user_text: str, memories_context: Optional[str], openai_client: AsyncOpenAI, model: str) -> str:

        messages: List = [
            ChatCompletionSystemMessageParam(
                role="system",
                content=SYSTEM_PROMPTS_LEXICON["system_prompts"]["base_assistant"]
            )
        ]

        if memories_context:
            # Добавляем память пользователя как отдельное системное сообщение
            messages.append(
                ChatCompletionSystemMessageParam(
                    role="system",
                    content=SYSTEM_PROMPTS_LEXICON["system_prompts"]["rule_memory"].format(memories_context)
                )
            )

        messages.append(
            ChatCompletionUserMessageParam(role="user", content=user_text)
        )

        response = await openai_client.chat.completions.create(
            model=model,
            messages=messages
        )

        return response.choices[0].message.content
