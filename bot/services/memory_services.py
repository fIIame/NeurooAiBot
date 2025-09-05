from typing import List

from openai import AsyncOpenAI

from database.repositories import UsersMemoriesRepository


class MemoryService:

    @staticmethod
    async def save(user_id: int, text: str, vector: List[float], openai_client: AsyncOpenAI, model: str) -> None:
        count = await UsersMemoriesRepository.count_memories(user_id)
        if count < 50:
            await UsersMemoriesRepository.safe_memory(user_id, text, vector, openai_client, model)

    @staticmethod
    async def get(user_id: int, vector: List[float], limit: int = 5) -> List[str]:
        return await UsersMemoriesRepository.get_memory(user_id, vector, limit)
