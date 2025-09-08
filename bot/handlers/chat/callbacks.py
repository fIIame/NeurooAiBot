from aiogram import Router
from aiogram.types import CallbackQuery

from bot.keyboards.callback_fabrics import ChatCallback
from bot.lexicon import BOT_LEXICON
from database.repositories import UsersRepository


router = Router()


@router.callback_query(ChatCallback.filter())
async def process_dialog_callback(query: CallbackQuery):
    """
    Обработчик нажатия кнопки "Начать чат" в диалоговом меню.

    Шаги:
    1. Активирует пользователя в базе (UsersRepository.set_user_active).
    2. Отправляет приветственное сообщение с началом диалога.
    3. Завершает обработку callback с уведомлением пользователя.

    Args:
        query (CallbackQuery): Объект callback от нажатия кнопки пользователем.
    """
    user_id = query.from_user.id

    # --- Активируем пользователя ---
    await UsersRepository.set_user_active(user_id=user_id)

    # --- Отправка приветственного сообщения ---
    await query.message.answer(BOT_LEXICON["bot"]["messages"]["dialog_start"])

    # --- Завершение callback с уведомлением ---
    await query.answer(text=BOT_LEXICON["bot"]["callbacks_answers"]["activated"], show_alert=False)
