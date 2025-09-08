from typing import Set
from pymorphy3 import MorphAnalyzer

def normalize_word(word: str, morph: MorphAnalyzer) -> str:
    """
    Приводит слово к его нормальной форме с помощью pymorphy3.

    Args:
        word (str): Слово для нормализации.
        morph (MorphAnalyzer): Объект морфологического анализатора.

    Returns:
        str: Нормализованная форма слова.
    """
    return morph.parse(word)[0].normal_form


def normalize_text(words: Set[str]) -> Set[str]:
    """
    Нормализует множество слов, приводя каждое слово к его нормальной форме.
    Пропускает пустые строки.

    Args:
        words (Set[str]): Множество слов для нормализации.

    Returns:
        Set[str]: Множество нормализованных слов.
    """
    morph = MorphAnalyzer(lang="ru")
    return {normalize_word(word.lower(), morph) for word in words if word.strip()}