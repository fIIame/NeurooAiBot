import yaml


# ------------------- Загрузка словаря бота -------------------
# lexicon.yaml содержит тексты сообщений, кнопки, подсказки и т.д.
with open('bot/lexicon/lexicon.yaml', 'r', encoding='utf-8') as file:
    BOT_LEXICON = yaml.safe_load(file)  # Загружаем как словарь для использования в коде
