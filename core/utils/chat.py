from aiogram.types import Message
from typing import List


def _split_text_into_lines(text: str) -> List[str]:
    """
    Разбивает текст на строки с сохранением символов переноса строки.

    Args:
        text (str): Исходный текст.

    Returns:
        List[str]: Список строк с переносами.
    """
    return text.splitlines(keepends=True)


def _chunk_lines(lines: List[str], max_len: int = 4096) -> List[str]:
    """
    Разбивает список строк на чанки заданной длины с учетом открытых/закрытых блоков кода Markdown.

    Args:
        lines (List[str]): Список строк текста.
        max_len (int, optional): Максимальная длина чанка. По умолчанию 4096.

    Returns:
        List[str]: Список текстовых чанков, готовых к отправке.
    """
    chunks = []
    chunk = ""
    is_code_block_open = False

    for line in lines:
        # Проверяем открытие/закрытие блока кода
        if line.count("```") % 2 != 0:
            is_code_block_open = not is_code_block_open

        # Если добавление строки превышает лимит, сохраняем текущий чанк
        if len(chunk) + len(line) > max_len:
            send_chunk = chunk + ("```" if is_code_block_open else "")
            chunks.append(send_chunk)
            chunk = "```" if is_code_block_open else ""

        chunk += line

    # Добавляем последний чанк
    if chunk:
        if is_code_block_open:
            chunk += "```"
        chunks.append(chunk)

    return chunks


async def safe_answer(message: Message, text: str, max_len: int = 4096):
    """
    Безопасно отправляет длинный текст через Telegram, разбивая его на чанки,
    при этом корректно закрывая незакрытые блоки кода Markdown.

    Args:
        message (Message): Объект сообщения aiogram.
        text (str): Текст для отправки.
        max_len (int, optional): Максимальная длина одного сообщения. По умолчанию 4096.
    """
    if len(text) <= max_len:
        await message.answer(text)
        return

    lines = _split_text_into_lines(text)
    chunks = _chunk_lines(lines, max_len)

    for chunk in chunks:
        await message.answer(chunk)
