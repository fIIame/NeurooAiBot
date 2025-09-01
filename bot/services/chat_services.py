from openai import AsyncOpenAI


async def get_ai_reply(text: str, openai_client: AsyncOpenAI) -> str:
    response = await openai_client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "Базовый умный помощник"},
            {"role": "user", "content": text}
        ]
    )

    ai_reply = response.choices[0].message.content
    return ai_reply
