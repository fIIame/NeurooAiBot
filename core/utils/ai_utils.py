import re
from typing import List

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from core.lexicon import RULE_BASED_LEXICON, SYSTEM_PROMPTS_LEXICON, BAD_WORDS_LEXICON
from core.utils.text_normalization import normalize_text


class AiMemoryUtils:
    # ------------------- Векторизация -------------------

    @staticmethod
    async def generate_embedding(text: str, openai_client: AsyncOpenAI, model: str) -> List[float]:
        """Получает embedding-вектор для текста."""
        emb = await openai_client.embeddings.create(
            model=model,
            input=text
        )
        return emb.data[0].embedding

    # ------------------- Rule-based фильтры -------------------

    @staticmethod
    def is_short(text: str) -> bool:
        """Сообщение слишком короткое (<3 слов)."""
        return len(text.split()) < 3

    @staticmethod
    def is_noise(text: str) -> bool:
        """Сообщение соответствует шаблонам "шума" (например, случайные символы)."""
        return any(re.match(pattern, text) for pattern in RULE_BASED_LEXICON["rules"]["noise_patterns"])

    @staticmethod
    def is_question(text: str) -> bool:
        """Сообщение является вопросом."""
        return text.strip().endswith("?")

    @staticmethod
    def contains_important_keyword(text: str) -> bool:
        """Сообщение содержит важные ключевые слова."""
        words = text.lower()
        return any(keyword.lower() in words for keyword in RULE_BASED_LEXICON["rules"]["important_keywords"])

    @staticmethod
    def contains_bad_words(text: str) -> bool:
        """Проверка на плохие слова."""
        words = set(re.findall(r"\w+", text.lower()))
        normalized_words = normalize_text(words)
        return not normalized_words.isdisjoint(BAD_WORDS_LEXICON)

    # ------------------- OpenAI фильтр -------------------

    @staticmethod
    async def ask_ai_is_important(text: str, openai_client: AsyncOpenAI, model: str) -> str:
        """Запрос к AI: стоит ли сохранять сообщение."""
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

    # ------------------- Основной фильтр -------------------

    @classmethod
    def is_spam(cls, text: str) -> bool:
        return cls.is_noise(text) or cls.is_short(text) or cls.contains_bad_words(text)
