import re

from openai import AsyncOpenAI
from core.utils.text_normalization import normalize_text
from core.utils.ai_utils import AiMemoryUtils
from core.lexicon import RULE_BASED_LEXICON, BAD_WORDS_LEXICON


class MemoryFilter:
    """
    Набор фильтров для оценки текстовых сообщений перед сохранением в память бота.

    Методы включают:
    - Rule-based фильтры (короткие сообщения, шум, плохие слова, важные ключевые слова).
    - Определение вопросов.
    - Проверку на спам.
    - Проверку необходимости сохранения в постоянную память.
    """

    # ------------------- Rule-based фильтры -------------------

    @staticmethod
    def is_short(text: str) -> bool:
        """
        Проверяет, является ли сообщение слишком коротким.

        Критерий: меньше 3 слов.

        Args:
            text (str): Текст сообщения.

        Returns:
            bool: True, если сообщение короткое.
        """
        return len(text.split()) < 3

    @staticmethod
    def is_noise(text: str) -> bool:
        """
        Определяет, является ли сообщение шумом по заранее заданным шаблонам.

        Args:
            text (str): Текст сообщения.

        Returns:
            bool: True, если текст распознан как шум.
        """
        return any(re.match(pattern, text) for pattern in RULE_BASED_LEXICON["rules"]["noise_patterns"])

    @staticmethod
    def is_question(text: str) -> bool:
        """
        Определяет, является ли сообщение вопросом.

        Критерий: сообщение оканчивается на '?'

        Args:
            text (str): Текст сообщения.

        Returns:
            bool: True, если текст вопросительный.
        """
        return text.strip().endswith("?")

    @staticmethod
    def contains_important_keyword(text: str) -> bool:
        """
        Проверяет наличие в тексте важных ключевых слов.

        Args:
            text (str): Текст сообщения.

        Returns:
            bool: True, если есть хотя бы одно ключевое слово.
        """
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in RULE_BASED_LEXICON["rules"]["important_keywords"])

    @staticmethod
    def contains_bad_words(text: str) -> bool:
        """
        Проверяет текст на наличие плохих слов.

        Логика:
        1. Разбиваем текст на слова.
        2. Нормализуем слова через `normalize_text`.
        3. Проверяем пересечение с BAD_WORDS_LEXICON.

        Args:
            text (str): Текст сообщения.

        Returns:
            bool: True, если текст содержит плохие слова.
        """
        words = set(re.findall(r"\w+", text.lower()))
        normalized_words = normalize_text(words)
        return not normalized_words.isdisjoint(BAD_WORDS_LEXICON)

    # ------------------- Основные фильтры -------------------

    @classmethod
    def is_spam(cls, text: str) -> bool:
        """
        Определяет, является ли сообщение спамом.

        Спам — это короткое сообщение, шум или наличие плохих слов.

        Args:
            text (str): Текст сообщения.

        Returns:
            bool: True, если сообщение спам.
        """
        return cls.is_short(text) or cls.is_noise(text) or cls.contains_bad_words(text)

    @classmethod
    async def is_required_for_permanent_memory(
        cls,
        text: str,
        openai_client: AsyncOpenAI,
        model: str
    ) -> bool:
        """
        Проверяет, нужно ли сохранять сообщение в постоянную память (Postgres).

        Логика:
        1. Спам — не сохраняем.
        2. Важные ключевые слова — сохраняем.
        3. В противном случае спрашиваем AI.

        Args:
            text (str): Текст сообщения.
            openai_client (AsyncOpenAI): Клиент OpenAI для проверки важности.
            model (str): Модель для проверки важности.

        Returns:
            bool: True, если сообщение должно быть сохранено в Postgres.
        """
        if cls.is_spam(text):
            return False
        if cls.contains_important_keyword(text):
            return True

        # Запрос к AI о необходимости сохранения
        ai_answer = await AiMemoryUtils.ask_ai_is_important(text, openai_client, model)
        return ai_answer.lower() == "да"
