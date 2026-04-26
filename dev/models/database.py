from motor.motor_asyncio import AsyncIOMotorClient
from dev.config import settings


def get_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(settings.MONGO_URI)


def get_database():
    return get_client()[settings.MONGO_DB_NAME]