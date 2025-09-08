import asyncio

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
    Основной обработчик всех текстовых сообщений пользователей.

    Шаги:
    1. Проверяет, активирован ли пользователь.
    2. Отправляет индикатор "печатает..." в чат.
    3. Получает embedding сообщения и релевантные воспоминания пользователя.
    4. Получает ответ от AI через выбранную модель.
    5. Безопасно отправляет ответ, разбивая длинные тексты на чанки.
    6. Сохраняет сообщение пользователя в память, если оно важно.

    Args:
        message (Message): Сообщение пользователя.
        bot (Bot): Экземпляр бота.
        openai_client (AsyncOpenAI): Асинхронный клиент OpenAI.
        chat_model (str): Модель для генерации ответа.
        filter_model (str): Модель для фильтрации/сохранения памяти.
        embedding_model (str): Модель для генерации векторного представления текста.
    """
    user_id = message.from_user.id
    user_text = message.text

    # --- Проверка активации пользователя ---
    if not await UsersRepository.is_user_activated(user_id):
        await message.answer(BOT_LEXICON["bot"]["messages"]["not_activated"])
        return

    # --- Показываем "печатает..." пользователю ---
    processing_msg = await message.answer(BOT_LEXICON["bot"]["messages"]["waiting_for_response"])
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    # --- Работа с памятью ---
    vector_task = asyncio.create_task(AiMemoryUtils.get_vector(user_text, openai_client, embedding_model))
    vector = await vector_task
    memories = await MemoryService.get(user_id, vector)
    memories_context = "\n".join(memories) if memories else "Память пользователя пуста."

    # --- Получение ответа от AI ---
    ai_reply = await AIService.get_reply(user_text, memories_context, openai_client, chat_model)

    # --- Отправка ответа пользователю безопасно ---
    await processing_msg.delete()
    await safe_answer(message, ai_reply)

    # --- Сохранение сообщения в память без блокировки основного потока ---
    asyncio.create_task(MemoryService.save(
        user_id=user_id,
        text=user_text,
        vector=vector,
        openai_client=openai_client,
        model=filter_model
    ))
