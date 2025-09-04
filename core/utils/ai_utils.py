import re
from typing import List

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from core.lexicon import RULE_BASED_LEXICON, SYSTEM_PROMPTS_LEXICON
from core.utils.enums import OpenAiModels


class AiMemoryUtils:
    @staticmethod
    async def get_vector(text: str, openai_client: AsyncOpenAI) -> List[float]:
        emb = await openai_client.embeddings.create(
            model=OpenAiModels.TEXT_EMBEDDING_3_SMALL.value,
            input=text
        )
        return emb.data[0].embedding

    # ------------------- Rule-based фильтры -------------------

    @staticmethod
    def _is_short_message(text: str) -> bool:
        return len(text.split()) < 3

    @staticmethod
    def _is_noise_pattern(text: str) -> bool:
        return any(re.match(pattern, text) for pattern in RULE_BASED_LEXICON["rules"]["noise_patterns"])

    @staticmethod
    def _is_question(text: str) -> bool:
        return text.strip().endswith("?")

    @staticmethod
    def _is_important_keyword(text: str) -> bool:
        words = text.lower().split()
        return any(keyword.lower() in words for keyword in RULE_BASED_LEXICON["rules"]["important_keywords"])

    # ------------------- OpenAI фильтр -------------------

    @staticmethod
    async def _ask_ai_should_save(text: str, openai_client: AsyncOpenAI, model: str) -> str:
        """Запрос к OpenAI: стоит ли сохранять сообщение в память."""
        messages = [
            ChatCompletionSystemMessageParam(
                role="system",
                content=SYSTEM_PROMPTS_LEXICON["system_prompts"]["memory_filter"]
            ),
            ChatCompletionUserMessageParam(role="user", content=text)
        ]

        response = await openai_client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content.strip().lower()

    # ------------------- Основная логика -------------------

    @classmethod
    async def is_ai_should_save(cls, text: str, openai_client: AsyncOpenAI, model: str) -> bool:
        """Решение: сохранять ли сообщение пользователя в память."""
        if cls._is_short_message(text) or cls._is_noise_pattern(text) or cls._is_question(text):
            return False
        if cls._is_important_keyword(text):
            return True

        answer = await cls._ask_ai_should_save(text, openai_client, model)
        return answer == "да"