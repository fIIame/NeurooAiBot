from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.callback_fabrics import ChatCallback
from database.repositories import UsersRepository


router = Router()


@router.callback_query(ChatCallback.filter())
async def process_dialog_callback(query: CallbackQuery):
    user_id = query.from_user.id
    await UsersRepository.activate_user(user_id=user_id)

    await query.message.answer(text="Отлично, давай начинать!")
    await query.answer()
