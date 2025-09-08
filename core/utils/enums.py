from enum import Enum


class OpenAiModels(Enum):
    """
    Перечисление доступных моделей OpenAI для использования в боте.

    Атрибуты:
        GPT_5_NANO: Маленькая и быстрая модель для фильтров и вспомогательных задач.
        GPT_5_MINI: Основная чат-модель для генерации ответов пользователю.
        TEXT_EMBEDDING_3_SMALL: Модель для получения embedding текста.
    """
    GPT_5_NANO = "gpt-5-nano"
    GPT_5_MINI = "gpt-5-mini"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
