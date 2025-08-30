import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from openai import OpenAI

from bot.handlers import common, chat, other
from core.config import load_config, Config
from core.loggers import setup_logging


async def main(config: Config):
    # Создаём объекты бота и диспетчера
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode="Markdown")
    )
    dp = Dispatcher()

    # Добавляем в диспетчер роутеры
    dp.include_routers(
        common.router,
        chat.router,
        other.router
    )

    ai_agent = OpenAI(
        api_key=config.aitunnel_api_key,
        base_url="https://api.aitunnel.ru/v1/"
    )


    # Добавляем переменные окружения в пространство имен диспетчера
    dp.workflow_data.update({"admin_ids": config.tg_bot.admin_ids, "ai_agent": ai_agent})

    # Удаляем апдейты, пришедшие вне работы бота
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        # Запускаем polling для получения обновлений от Telegram
        logger.info("Starting bot...")
        await dp.start_polling(bot)
    finally:
        # Закрываем сессию бота, освобождая ресурсы
        logger.info("Stopping bot...")
        await bot.session.close()


if __name__ == '__main__':
    # Инициализируем logging
    setup_logging("core/loggers/config.yaml")
    logger = logging.getLogger(__name__)

    # Инициализируем конфиг
    config = load_config()

    asyncio.run(main(config))
