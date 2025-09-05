from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.enums import ChatAction
from openai import AsyncOpenAI

from bot.services.chat_services import AIService
from bot.services.memory_services import MemoryService
from bot.lexicon import BOT_LEXICON
from database.repositories import UsersRepository
from core.utils.ai_utils import AiMemoryUtils


router = Router()


@router.message()
async def handle_other_messages(
    message: Message,
    bot: Bot,
    openai_client: AsyncOpenAI,
    model: str
):
    user_id = message.from_user.id
    user_text = message.text

    # --- Проверяем активацию пользователя ---
    if not await UsersRepository.is_user_activated(user_id):
        await message.answer(BOT_LEXICON["bot"]["messages"]["not_activated"])
        return

    # --- Сообщаем пользователю, что бот "печатает" ---
    processing_msg = await message.answer(BOT_LEXICON["bot"]["messages"]["waiting_for_response"])
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    # --- Работа с памятью ---
    vector = await AiMemoryUtils.get_vector(user_text, openai_client)
    await MemoryService.save(user_id, user_text, vector, openai_client, model)
    memories = await MemoryService.get(user_id, vector)
    memories_context = "\n".join(memories) if memories else "Память пользователя пуста."

    # --- Получаем ответ от модели ---
    ai_reply = await AIService.get_reply(user_text, memories_context, openai_client, model)

    # --- Убираем заглушку и отправляем ответ ---
    await processing_msg.delete()
    await message.reply(ai_reply)
