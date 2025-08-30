from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart


router = Router()


@router.message(CommandStart())
async def process_start_handler(message: Message):
    await message.answer(
        text="🐍 Привет! Я твой Python-помощник. "
             "Хочешь задать вопрос или получить подсказку? "
             "Напиши /chat и давай начинать!"
    )
