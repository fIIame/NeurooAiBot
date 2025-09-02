from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.enums import ChatAction
from openai import AsyncOpenAI

from database.repositories import UsersRepository
from bot.services.chat_services import get_ai_reply


router = Router()


@router.message()
async def handle_other_messages(message: Message, bot: Bot, openai_client: AsyncOpenAI):
    # Проверяем, активирован ли пользователь
    if not await UsersRepository.is_user_activated(message.from_user.id):
        await message.answer("Для начала работы введите /start")
        return

    # Сообщаем, что бот "печатает"
    processing_msg = await message.answer("💡 Запрос принят! Ответ появится примерно через 10–15 секунд.")
    await bot.send_chat_action(
        message.chat.id,
        ChatAction.TYPING
    )

    # Получаем ответ от модели
    ai_reply = await get_ai_reply(
        text=message.text,
        openai_client=openai_client
    )

    # Удаляем "заглушку" и отправляем реальный ответ
    await processing_msg.delete()
    await message.reply(ai_reply)
