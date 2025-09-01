from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.keyboards.callback_fabrics import ChatCallback


dialog_start_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Начать диалог", callback_data=ChatCallback().pack())]
    ]
)
