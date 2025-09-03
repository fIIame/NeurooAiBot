from openai import AsyncOpenAI
from typing import List

async def get_vector(text: str, openai_client: AsyncOpenAI) -> List[float]:
    emb = await openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    vector = emb.data[0].embedding
    return vector
