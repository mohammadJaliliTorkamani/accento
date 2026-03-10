from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = AsyncIOMotorClient(settings.MONGO_URL)
db = client["accento"]
collection = db["results"]

async def create_indexes():
    await collection.create_index("url", unique=True)
