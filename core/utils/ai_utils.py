import re
from typing import List

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from core.lexicon import RULE_BASED_LEXICON, SYSTEM_PROMPTS_LEXICON, BAD_WORDS_LEXICON
from core.utils.text_normalization import normalize_text


class AiMemoryUtils:
    """
    Утилиты для работы с памятью пользователя и фильтрации сообщений.

    Основные функции:
    - Генерация векторного представления сообщения для хранения в embedding-памяти.
    - Фильтрация сообщений на основе правил (короткие, шум, вопросы, важные ключевые слова, плохие слова).
    - Проверка через AI, стоит ли сохранять сообщение.
    """

    # ------------------- Векторизация -------------------

    @staticmethod
    async def get_vector(text: str, openai_client: AsyncOpenAI, model: str) -> List[float]:
        """
        Получает embedding-вектор для текста.

        Args:
            text (str): Сообщение пользователя.
            openai_client (AsyncOpenAI): Асинхронный клиент OpenAI.
            model (str): Модель для генерации embedding.

        Returns:
            List[float]: Векторное представление текста.
        """
        emb = await openai_client.embeddings.create(
            model=model,
            input=text
        )
        return emb.data[0].embedding

    # ------------------- Rule-based фильтры -------------------

    @staticmethod
    def _is_short_message(text: str) -> bool:
        """Сообщение слишком короткое (<3 слов)."""
        return len(text.split()) < 3

    @staticmethod
    def _is_noise_pattern(text: str) -> bool:
        """Сообщение соответствует шаблонам "шума" (например, случайные символы)."""
        return any(re.match(pattern, text) for pattern in RULE_BASED_LEXICON["rules"]["noise_patterns"])

    @staticmethod
    def _is_question(text: str) -> bool:
        """Сообщение является вопросом."""
        return text.strip().endswith("?")

    @staticmethod
    def _is_important_keyword(text: str) -> bool:
        """Сообщение содержит важные ключевые слова."""
        words = text.lower()
        return any(keyword.lower() in words for keyword in RULE_BASED_LEXICON["rules"]["important_keywords"])

    @staticmethod
    def _is_bad_message(text: str) -> bool:
        """
        Проверка на плохие слова.

        1. Разбиваем текст на слова.
        2. Нормализуем их через pymorphy3.
        3. Проверяем пересечение с BAD_WORDS_LEXICON.

        Returns:
            bool: True, если сообщение содержит плохие слова.
        """
        words = set(re.findall(r"\w+", text.lower()))
        normalized_words = normalize_text(words)
        return not normalized_words.isdisjoint(BAD_WORDS_LEXICON)

    # ------------------- OpenAI фильтр -------------------

    @staticmethod
    async def _ask_ai_should_save(text: str, openai_client: AsyncOpenAI, model: str) -> str:
        """
        Запрос к AI, стоит ли сохранять сообщение.

        Args:
            text (str): Сообщение пользователя.
            openai_client (AsyncOpenAI): Клиент OpenAI.
            model (str): Модель для генерации ответа.

        Returns:
            str: Ответ модели ("да" или "нет").
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

    # ------------------- Основная логика -------------------

    @classmethod
    async def is_ai_should_save(
            cls,
            text: str,
            openai_client: AsyncOpenAI,
            model: str
    ) -> bool:
        """
        Решение: сохранять ли сообщение пользователя в память.

        Логика:
        1. Сначала проверяем rule-based фильтры:
           - короткие сообщения,
           - шум,
           - вопросы,
           - плохие слова.
        2. Если сообщение содержит важные ключевые слова — сохраняем.
        3. Иначе делаем запрос к AI для решения.

        Args:
            text (str): Сообщение пользователя.
            openai_client (AsyncOpenAI): Клиент OpenAI.
            model (str): Модель для проверки.

        Returns:
            bool: True, если сообщение стоит сохранить.
        """
        # Rule-based проверки
        if cls._is_short_message(text) or cls._is_noise_pattern(text) or cls._is_question(text) or cls._is_bad_message(text):
            return False

        # Важные ключевые слова
        if cls._is_important_keyword(text):
            return True

        # Проверка AI
        answer = await cls._ask_ai_should_save(text, openai_client, model)
        return answer == "да"
