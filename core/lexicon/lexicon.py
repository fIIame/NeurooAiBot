import yaml
from core.utils.text_normalization import normalize_text


# ------------------- Загрузка логов -------------------
with open('core/lexicon/logging.yaml', 'r', encoding='utf-8') as file:
    LOGGING_LEXICON = yaml.safe_load(file)  # Словарь с текстами для логирования

# ------------------- Правила для rule-based фильтров -------------------
with open('core/lexicon/rule_based.yaml', 'r', encoding='utf-8') as file:
    RULE_BASED_LEXICON = yaml.safe_load(file)  # Словарь с правилами для фильтров

# ------------------- Системные промпты для AI -------------------
with open('core/lexicon/system_prompts.yaml', 'r', encoding='utf-8') as file:
    SYSTEM_PROMPTS_LEXICON = yaml.safe_load(file)  # Словарь с системными промптами

# ------------------- Словарь плохих слов -------------------
with open('core/lexicon/bad_words.yaml', 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)
    bad_words = set(data.get("bad_words", []))  # Преобразуем в set для быстрого поиска
    BAD_WORDS_LEXICON = normalize_text(bad_words)  # Нормализуем слова через pymorphy
