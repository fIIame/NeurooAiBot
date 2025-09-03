import yaml


with open('core/lexicon/lexicon.yaml', 'r') as file:
    LOGGING_LEXICON = yaml.safe_load(file)