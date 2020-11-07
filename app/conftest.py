from app.settings import load_config
import pytest
from motor.motor_asyncio import AsyncIOMotorClient


@pytest.fixture
def setup_db():
    conf = load_config()
    return AsyncIOMotorClient(conf["database_uri"]).control_conf


@pytest.fixture
async def create_user(setup_db):
    user = {"name": "Test user", "api_key": "TestapiKey", "files": []}
    await setup_db.users.insert_one(user)
    yield user
    await setup_db.users.delete_one({"name": user["name"]})
