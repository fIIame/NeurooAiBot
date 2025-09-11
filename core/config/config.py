from dataclasses import dataclass
from typing import List, Optional

from environs import Env


class PostgresConfig:
    """
    Класс для хранения конфигурации подключения к базе данных.

    Атрибуты:
        DB_HOST (str): Хост базы данных.
        DB_PORT (int): Порт базы данных.
        DB_USER (str): Пользователь базы данных.
        DB_PASS (str): Пароль пользователя.
        DB_NAME (str): Имя базы данных.
    """

    def __init__(self, db_host: str, db_port: int, db_user: str, db_pass: str, db_name: str):
        self.DB_HOST = db_host
        self.DB_PORT = db_port
        self.DB_USER = db_user
        self.DB_PASS = db_pass
        self.DB_NAME = db_name

    @property
    def asyncpg_url(self) -> str:
        """
        Генерирует URL для подключения к базе данных через asyncpg.

        Returns:
            str: URL для SQLAlchemy / asyncpg в формате:
                 postgresql+asyncpg://user:pass@host:port/dbname
        """
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


@dataclass
class TgBot:
    """
    Конфигурация Telegram-бота.

    Attributes:
        token (str): Токен бота.
        admin_ids (List[int]): Список ID администраторов бота.
    """
    token: str
    admin_ids: List[int]


@dataclass
class Config:
    """
    Основная конфигурация приложения.

    Attributes:
        tg_bot (TgBot): Настройки Telegram-бота.
        postgres (PostgresConfig): Настройки подключения к базе данных.
        redis_url (str): URL для подключения к Redis.
        aitunnel_api_key (str): API-ключ для сервиса Aitunnel.
    """
    tg_bot: TgBot
    postgres: PostgresConfig
    redis_url: str
    aitunnel_api_key: str


def load_config(path: Optional[str] = None) -> Config:
    """
    Загружает конфигурацию приложения из .env файла.

    Args:
        path (Optional[str]): Путь к .env файлу. Если None, используется стандартный.

    Returns:
        Config: Объект конфигурации с Telegram-ботом, базой данных и ключами API.
    """
    env = Env()
    env.read_env(path=path)

    config = Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMIN_IDS")))  # преобразуем строки в int
        ),
        postgres=PostgresConfig(
            db_host=env.str("DB_HOST"),
            db_port=env.int("DB_PORT"),
            db_user=env.str("DB_USER"),
            db_pass=env.str("DB_PASS"),
            db_name=env.str("DB_NAME")
        ),
        redis_url=env.str("REDIS_URL"),
        aitunnel_api_key=env.str("AITUNNEL_API_KEY")
    )

    return config
