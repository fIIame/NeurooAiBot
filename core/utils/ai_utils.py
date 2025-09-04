import re
from typing import List, Optional

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from core.lexicon import RULE_BASED_LEXICON


class AiMemoryUtils:

    @staticmethod
    async def get_vector(
            text: str,
            openai_client: AsyncOpenAI
    ) -> List[float]:

        emb = await openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        vector = emb.data[0].embedding
        return vector

    @staticmethod
    def _is_short_message(text: str) -> bool:
        return len(text.split()) < 3

    @staticmethod
    def _is_noise_pattern(text: str) -> bool:
        for noise_pattern in RULE_BASED_LEXICON["rules"]["noise_patterns"]:
            if re.match(noise_pattern, text):
                return True
        return False

    @staticmethod
    def _is_important_keyword(text: str) -> bool:
        for important_keyword in RULE_BASED_LEXICON["rules"]["important_keywords"]:
            if important_keyword.lower() in text.lower().split():
                return True
        return False

    @staticmethod
    async def _ask_ai_should_save(text: str, openai_client: AsyncOpenAI, model: str) -> str:

        messages: List = [
            ChatCompletionSystemMessageParam(role="system", content=(
                "Ты фильтр сообщений."
                "Ответь только 'да' или 'нет', нужно ли сохранять сообщение о пользователе."
            )),
            ChatCompletionUserMessageParam(role="user", content=text)
        ]

        response = await openai_client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=5
        )

        answer = response.choices[0].message.content.strip().lower()
        return answer.lower()

    @classmethod
    async def is_ai_should_save(cls, text: str, openai_client: AsyncOpenAI, model: str) -> bool:
        if cls._is_short_message(text) or cls._is_noise_pattern(text):
            return False
        if cls._is_important_keyword(text):
            answer = await cls._ask_ai_should_save(text, openai_client, model)
            return answer == "да"
        return False
