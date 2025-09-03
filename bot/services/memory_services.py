from database.repositories import UsersMemoriesRepository
from openai import AsyncOpenAI

class MemoryService:

    @staticmethod
    async def save(user_id: int, text: str, openai_client: AsyncOpenAI):
        await UsersMemoriesRepository.safe_memory(user_id, text, openai_client)

    @staticmethod
    async def get(user_id: int, query_text: str, openai_client: AsyncOpenAI, limit: int = 5):
        return await UsersMemoriesRepository.get_memory(user_id, query_text, openai_client, limit)
