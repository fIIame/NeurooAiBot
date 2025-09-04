import yaml


with open('bot/lexicon/logging.yaml', 'r') as file:
    BOT_LEXICON = yaml.safe_load(file)
