from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from bot.keyboards.inline import dialog_start_kb
from bot.lexicon import BOT_LEXICON
from database.repositories import UsersRepository

router = Router()


@router.message(CommandStart())
async def process_start_handler(message: Message):
    """
    Обработчик команды /start.

    1. Добавляет пользователя в базу (если еще не существует).
    2. Отправляет приветственное сообщение с inline-кнопкой для начала диалога.

    Args:
        message (Message): объект сообщения от пользователя.
    """
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    # --- Добавляем пользователя в базу ---
    await UsersRepository.add_user(user_id=user_id, first_name=first_name)

    # --- Отправляем приветственное сообщение с клавиатурой ---
    await message.answer(
        text=BOT_LEXICON["bot"]["messages"]["start"],
        reply_markup=dialog_start_kb
    )
