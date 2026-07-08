from motor.motor_asyncio import AsyncIOMotorClient
from backend.app.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_helper = Database()

async def connect_to_mongo():
    db_helper.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_helper.db = db_helper.client[settings.DATABASE_NAME]
    print(f"Connected to MongoDB Atlas: {settings.DATABASE_NAME}")

async def close_mongo_connection():
    if db_helper.client:
        db_helper.client.close()
        print("Closed MongoDB connection.")
