import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from openai import AsyncOpenAI

from bot.handlers import common, chat
from core.lexicon import LOGGING_LEXICON
from core.config import load_config, Config
from core.loggers import setup_logging
from core.utils.enums import OpenAiModels
from database import init_db


async def main(config: Config):
    """
    Основная точка входа для запуска Telegram-бота.

    Args:
        config (Config): Загруженный объект конфигурации приложения.
    """

    # --- Инициализация Telegram-бота ---
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode="Markdown")
    )
    dp = Dispatcher()

    # --- Подключение роутеров (обработчиков команд/сообщений) ---
    dp.include_routers(
        common.router,
        chat.router
    )

    # --- Инициализация базы данных ---
    await init_db(config.db.asyncpg_url)

    # --- Инициализация OpenAI-агента ---
    openai_client = AsyncOpenAI(
        api_key=config.aitunnel_api_key,
        base_url="https://api.aitunnel.ru/v1/"
    )

    # --- Общие данные, доступные во всех хендлерах ---
    dp.workflow_data.update({
        "admin_ids": config.tg_bot.admin_ids,
        "openai_client": openai_client,
        "chat_model": OpenAiModels.GPT_5_MINI.value,
        "filter_model": OpenAiModels.GPT_5_NANO.value,
        "embedding_model": OpenAiModels.TEXT_EMBEDDING_3_SMALL.value
    })

    # --- Удаляем апдейты, пришедшие до старта бота ---
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        logger.info(LOGGING_LEXICON["logging"]["bot"]["start"])
        # --- Запуск цикла обработки апдейтов ---
        await dp.start_polling(bot)
    finally:
        logger.info(LOGGING_LEXICON["logging"]["bot"]["stop"])
        # --- Корректное завершение работы ---
        await bot.session.close()


if __name__ == '__main__':
    """
    Точка запуска приложения.
    Настраивает логирование, загружает конфигурацию и стартует event-loop.
    """

    # --- Настройка логирования ---
    setup_logging("core/loggers/config.yaml")
    logger = logging.getLogger(__name__)

    # --- Загрузка конфигурации из окружения ---
    config = load_config()

    # --- Запуск основного event-loop ---
    asyncio.run(main(config))