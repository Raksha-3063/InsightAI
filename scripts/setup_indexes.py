import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def setup_database_indexes():
    """
    Creates optimal indexes for MongoDB collections.
    """
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DATABASE_NAME", "insightai")
    
    print(f"Connecting to MongoDB at {mongo_url}...")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # 1. Users collection
    print("Setting up indexes for 'users'...")
    await db.users.create_index("email", unique=True)
    
    # 2. Projects collection
    print("Setting up indexes for 'projects'...")
    await db.projects.create_index("userId")
    
    # 3. Datasets collection
    print("Setting up indexes for 'datasets'...")
    await db.datasets.create_index("projectId")
    
    # 4. Models collection
    print("Setting up indexes for 'models'...")
    await db.models.create_index("projectId")
    await db.models.create_index("datasetId")
    
    # 5. Forecasts collection
    print("Setting up indexes for 'forecasts'...")
    await db.forecasts.create_index("projectId")
    
    # 6. Conversations collection
    print("Setting up indexes for 'conversations'...")
    await db.conversations.create_index("projectId")
    await db.conversations.create_index("lastModified")
    
    # 7. Background jobs collection
    print("Setting up indexes for 'background_jobs'...")
    await db.background_jobs.create_index("projectId")
    await db.background_jobs.create_index("status")
    
    print("Database indexes set up successfully!")
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_database_indexes())
