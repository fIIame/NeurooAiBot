from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.enums import ChatAction
from openai import AsyncOpenAI

from bot.services.ai_services import AIService
from bot.services.memory_services import TemporaryMemoryService, MemoryContextService
from bot.lexicon import BOT_LEXICON
from database.postgres.repositories import UsersRepository
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

    Алгоритм работы:
    1. Проверяет активацию пользователя.
    2. Отправляет индикатор "печатает..." в чат.
    3. Формирует контекст для AI:
       - краткосрочная память (Redis),
       - долгосрочная память (PostgreSQL), если сообщение значимо.
    4. Получает ответ от модели AI с учётом контекста.
    5. Сохраняет реплики пользователя и бота в краткосрочную память.
    6. Отправляет ответ безопасно, разбивая длинные тексты на чанки.

    Args:
        message (Message): Сообщение пользователя.
        bot (Bot): Экземпляр Telegram-бота.
        openai_client (AsyncOpenAI): Асинхронный клиент OpenAI.
        chat_model (str): Модель для генерации ответа AI.
        filter_model (str): Модель фильтрации сообщений для сохранения в долгосрочную память.
        embedding_model (str): Модель генерации embedding текста.
    """
    user_id = message.from_user.id
    user_text = message.text

    # --- Проверка активации пользователя ---
    if not await UsersRepository.is_user_activated(user_id):
        # Отправляем уведомление, если пользователь не активирован
        await message.answer(BOT_LEXICON["bot"]["messages"]["not_activated"])
        return

    # --- Индикатор "печатает..." ---
    processing_msg = await message.answer(BOT_LEXICON["bot"]["messages"]["waiting_for_response"])
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    # --- Формирование контекста сообщений пользователя ---
    memories_context = await MemoryContextService.build_full_context(
        user_id=user_id,
        user_text=user_text,
        openai_client=openai_client,
        filter_model=filter_model,
        embedding_model=embedding_model
    )

    # --- Получение ответа модели AI с учётом контекста ---
    ai_reply = await AIService.get_reply(user_text, memories_context, openai_client, chat_model)

    # --- Сохранение сообщений пользователя и бота в краткосрочную память ---
    await TemporaryMemoryService.save(user_id, user_text, ai_reply)

    # --- Безопасная отправка ответа пользователю ---
    await processing_msg.delete()
    await safe_answer(message, ai_reply)
