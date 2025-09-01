from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.enums import ChatAction
from openai import AsyncOpenAI

from database.repositories import UsersRepository
from bot.services.chat_services import get_ai_reply


router = Router()


@router.message()
async def handle_other_messages(message: Message, bot: Bot, openai_client: AsyncOpenAI):
    is_activated = await UsersRepository.is_user_activated(message.from_user.id)
    if not is_activated:
        await message.answer("Для начала работы введите /start")
        return

    # Сообщаем, что бот "печатает"
    await bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING
    )

    user_message = message.text
    ai_reply = await get_ai_reply(text=user_message, openai_client=openai_client)
    await message.answer(text=ai_reply)
