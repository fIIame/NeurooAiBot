import yaml


with open('core/lexicon/logging.yaml', 'r') as file:
    LOGGING_LEXICON = yaml.safe_load(file)

with open('core/lexicon/rule_based.yaml', 'r') as file:
    RULE_BASED_LEXICON = yaml.safe_load(file)