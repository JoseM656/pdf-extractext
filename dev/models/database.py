from motor.motor_asyncio import AsyncIOMotorClient
from dev.config import settings


def get_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(settings.MONGO_URI)
