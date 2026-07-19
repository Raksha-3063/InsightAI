import os
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

os.environ["TESTING"] = "true"

from backend.app.main import app
from backend.app.config import settings
from backend.app.database.connection import db_helper, connect_to_mongo, close_mongo_connection

@pytest.fixture(scope="session")
def event_loop_policy():
    return asyncio.get_event_loop_policy()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def test_db_setup():
    # Override settings for tests
    settings.DATABASE_NAME = "insightai_test"
    await connect_to_mongo()
    # Clean test DB
    await db_helper.db.users.delete_many({})
    yield
    # Clean up test DB
    await db_helper.db.users.delete_many({})
    await close_mongo_connection()

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
