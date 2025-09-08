from aiogram.types import Message


async def safe_answer(message: Message, text: str, max_len: int = 4096):
    lines = text.splitlines(keepends=True)
    chunk = ""
    is_code_block_open = False
    for line in lines:
        if line.count("```") % 2 != 0:
            is_code_block_open = not is_code_block_open

        if len(chunk) + len(line) > max_len:
            send_chunk = chunk + ("```" if is_code_block_open else "")
            await message.answer(send_chunk)
            chunk = "```" if is_code_block_open else ""
        chunk += line

    if chunk:
        if is_code_block_open:
            chunk += "```"
        await message.answer(chunk)

