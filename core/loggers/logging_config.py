from logging.config import dictConfig

import yaml


def setup_logging(config_path: str):
    with open(file=config_path, mode="r", encoding="utf-8") as file:
        config_path = yaml.safe_load(file)

    dictConfig(config_path)
