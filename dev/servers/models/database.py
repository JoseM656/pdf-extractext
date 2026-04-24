from motor.motor_asyncio import AsyncIOMotorClient
<<<<<<< HEAD
from dev.servers.config import settings
=======
from dev.config import settings
>>>>>>> main


def get_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(settings.MONGO_URI)


def get_database():
    return get_client()[settings.MONGO_DB_NAME]