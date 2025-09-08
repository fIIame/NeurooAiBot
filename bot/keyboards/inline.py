from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards.callback_fabrics import ChatCallback
from bot.lexicon import BOT_LEXICON


# --- Inline-клавиатура для начала диалога ---
dialog_start_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=BOT_LEXICON["bot"]["keyboards"]["buttons"]["start_chat"],
                callback_data=ChatCallback().pack()  # формируем callback_data с префиксом "chat"
            )
        ]
    ]
)
