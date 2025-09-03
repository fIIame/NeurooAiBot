from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.enums import ChatAction
from openai import AsyncOpenAI

from database.repositories import UsersRepository, UsersMemoriesRepository
from bot.services.ai_services import AIService
from bot.services.memory_services import MemoryService

router = Router()


@router.message()
async def handle_other_messages(
    message: Message,
    bot: Bot,
    openai_client: AsyncOpenAI
):
    user_id = message.from_user.id
    user_text = message.text

    # --- Проверяем активацию пользователя ---
    if not await UsersRepository.is_user_activated(user_id):
        await message.answer("Для начала работы введите /start")
        return

    # --- Сообщаем пользователю, что бот "печатает" ---
    processing_msg = await message.answer("💡 Запрос принят! Ответ появится через 10–15 секунд.")
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    # --- Работа с памятью ---
    await MemoryService.save(user_id, user_text, openai_client)
    memories = await MemoryService.get(user_id, user_text, openai_client)
    memories_context = "\n".join(memories) if memories else ""

    # --- Получаем ответ от модели ---
    ai_reply = await AIService.get_reply(user_text, memories_context, openai_client)

    # --- Убираем заглушку и отправляем ответ ---
    await processing_msg.delete()
    await message.reply(ai_reply)