from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from database.repositories import UsersRepository
from bot.keyboards.inline import dialog_start_kb


router = Router()


@router.message(CommandStart())
async def process_start_handler(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    await UsersRepository.insert_user(user_id=user_id, first_name=first_name)

    await message.answer(
        text=(
            "<b>Привет! Я Neuroo 👾</b>\n"
            "Хочешь <i>задать вопрос</i> или получить <i>подсказку</i>? 💫\n\n"
            "<code>Нажми на кнопку ниже, чтобы начать чат 👇🏻</code> "
        ),
        reply_markup=dialog_start_kb
    )
