from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from bot.keyboards.inline import dialog_start_kb
from bot.lexicon import BOT_LEXICON
from database.repositories import UsersRepository


router = Router()


@router.message(CommandStart())
async def process_start_handler(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    await UsersRepository.add_user(user_id=user_id, first_name=first_name)

    await message.answer(
        text=(BOT_LEXICON["bot"]["messages"]["start"]),
        reply_markup=dialog_start_kb
    )
