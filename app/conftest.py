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


@pytest.fixture
async def create_name_for_temp_user(setup_db):
    name = "TempUser"
    yield name
    await setup_db.users.delete_one({"name": name})


@pytest.fixture
async def create_user_and_files(setup_db, tmp_path):
    f = tmp_path / "some_confqwerty.ini"
    f.write_text("[ini]\nSome=Some")
    user = {
        "name": "Test user",
        "api_key": "TestapiKey",
        "files": [{"real_path": f.as_posix(), "filename": "some_conf.ini"}],
    }
    await setup_db.users.insert_one(user)
    yield user, f
    await setup_db.users.delete_one({"name": user["name"]})
