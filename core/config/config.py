from dataclasses import dataclass
from typing import List, Optional

from environs import Env


@dataclass()
class TgBot:
    token: str
    admin_ids: List[int]


@dataclass()
class Config:
    tg_bot: TgBot
    aitunnel_api_key: str


def load_config(path: Optional[str] = None) -> Config:
    env = Env()
    env.read_env(path=path)

    config = Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMIN_IDS")))
        ),
        aitunnel_api_key=env.str("AITUNNEL_API_KEY")
    )

    return config
