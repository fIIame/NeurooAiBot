from aiogram import Router
from aiogram.types import Message


router = Router()


@router.message()
async def handle_other_messages(message: Message):
    await message.answer("Для начала работы введите /start")
