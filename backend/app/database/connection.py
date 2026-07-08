import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from backend.app.config import settings

class Database:
    client: AsyncIOMotorClient = None
    _db = None
    _loop = None

    @property
    def db(self):
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if self.client is None or self._loop != current_loop:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self._db = self.client[settings.DATABASE_NAME]
            self._loop = current_loop
        return self._db

db_helper = Database()

async def connect_to_mongo():
    # Trigger connection initialization
    _ = db_helper.db
    print(f"Connected to MongoDB: {settings.DATABASE_NAME}")

async def close_mongo_connection():
    if db_helper.client:
        db_helper.client.close()
        db_helper.client = None
        db_helper._db = None
        db_helper._loop = None
        print("Closed MongoDB connection.")
