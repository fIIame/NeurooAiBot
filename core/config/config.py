from dataclasses import dataclass
from typing import List, Optional

from environs import Env


class Database:
    def __init__(self, db_host: str, db_port: int, db_user: str, db_pass: str, db_name: str):
        self.DB_HOST = db_host
        self.DB_PORT = db_port
        self.DB_USER = db_user
        self.DB_PASS = db_pass
        self.DB_NAME = db_name

    @property
    def asyncpg_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


@dataclass()
class TgBot:
    token: str
    admin_ids: List[int]


@dataclass()
class Config:
    tg_bot: TgBot
    db: Database
    aitunnel_api_key: str


def load_config(path: Optional[str] = None) -> Config:
    env = Env()
    env.read_env(path=path)

    config = Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMIN_IDS")))
        ),
        db=Database(
            db_host=env.str("DB_HOST"),
            db_port=env.int("DB_PORT"),
            db_user=env.str("DB_USER"),
            db_pass=env.str("DB_PASS"),
            db_name=env.str("DB_NAME")
        ),
        aitunnel_api_key=env.str("AITUNNEL_API_KEY")
    )

    return config
