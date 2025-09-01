from aiogram import Router

from . import callbacks
from . import chat


router = Router()

router.include_routers(
    callbacks.router,
    chat.router
)
