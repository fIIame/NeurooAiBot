import yaml


with open('bot/lexicon/lexicon.yaml', 'r') as file:
    BOT_LEXICON = yaml.safe_load(file)
