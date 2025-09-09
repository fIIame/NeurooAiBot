import asyncio
from typing import Optional

from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.enums import ChatAction
from openai import AsyncOpenAI

from bot.services.chat_services import AIService
from bot.services.memory_services import MemoryService
from bot.lexicon import BOT_LEXICON
from database.repositories import UsersRepository
from core.utils.ai_utils import AiMemoryUtils
from core.utils.chat import safe_answer


router = Router()


@router.message()
async def handle_other_messages(
    message: Message,
    bot: Bot,
    openai_client: AsyncOpenAI,
    chat_model: str,
    filter_model: str,
    embedding_model: str
) -> None:
    """
    Обрабатывает все текстовые сообщения пользователей.

    Логика:
    1. Проверяет активацию пользователя.
    2. Отправляет индикатор "печатает..." в чат.
    3. Генерирует embedding для сообщения, если оно не спам.
    4. Извлекает релевантные воспоминания из памяти пользователя.
    5. Получает ответ от AI с учётом памяти.
    6. Отправляет ответ безопасно, разбивая на чанки.
    7. Сохраняет важные сообщения в память в фоновом режиме.

    Args:
        message (Message): Сообщение пользователя.
        bot (Bot): Экземпляр Telegram-бота.
        openai_client (AsyncOpenAI): Клиент OpenAI для запросов.
        chat_model (str): Модель генерации ответов.
        filter_model (str): Модель фильтрации сообщений для памяти.
        embedding_model (str): Модель для генерации embedding.
    """
    user_id = message.from_user.id
    user_text = message.text

    # --- Проверка активации пользователя ---
    if not await UsersRepository.is_user_activated(user_id):
        await message.answer(BOT_LEXICON["bot"]["messages"]["not_activated"])
        return

    # --- Индикатор "печатает..." ---
    processing_msg = await message.answer(BOT_LEXICON["bot"]["messages"]["waiting_for_response"])
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    # --- Инициализация контекста памяти ---
    memories_context: Optional[str] = None

    # --- Обработка сообщений, которые не являются спамом ---
    if not AiMemoryUtils.is_spam(user_text):

        # Генерация векторного представления текста
        vector = await AiMemoryUtils.generate_embedding(user_text, openai_client, embedding_model)

        # Получение релевантных воспоминаний
        memories = await MemoryService.get(user_id, vector)
        if memories:
            memories_context = "\n".join(memories)

        # Сохранение сообщения в память (фон)
        asyncio.create_task(MemoryService.save(
            user_id=user_id,
            text=user_text,
            vector=vector,
            openai_client=openai_client,
            model=filter_model
        ))

    # --- Получение ответа от AI ---
    ai_reply = await AIService.get_reply(user_text, memories_context, openai_client, chat_model)

    # --- Отправка ответа пользователю безопасно ---
    await processing_msg.delete()
    await safe_answer(message, ai_reply)