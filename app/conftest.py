import uuid
from app.settings import load_config
import pytest
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient


@pytest.fixture
def test_conf():
    local_settings_ = open("local.yaml", "r") if Path("local.yaml").exists() else None
    conf = load_config(local_settings_)
    conf["db_name"] = f'{conf["db_name"]}_test'
    return conf


@pytest.fixture
async def setup_db(test_conf):
    db = AsyncIOMotorClient(test_conf["database_uri"])
    yield db[test_conf["db_name"]]
    await db.drop_database(test_conf["db_name"])


@pytest.fixture
async def create_user(setup_db):
    user = {"name": "Test user", "api_key": f"{str(uuid.uuid4())}", "files": []}
    await setup_db.users.insert_one(user)
    yield user
    await setup_db.users.delete_one({"name": user["name"]})
    await setup_db.drop_collection("users")


@pytest.fixture
async def create_name_for_temp_user(setup_db):
    name = "TempUser"
    yield name
    await setup_db.users.delete_one({"name": name})


@pytest.fixture
async def create_user_and_configuration(setup_db, tmp_path):
    f = tmp_path / "some_confqwerty.ini"
    f.write_text("[ini]\nSome=Some")
    user = {
        "name": "Test user",
        "api_key": str(uuid.uuid4),
    }
    user_id = await setup_db.users.insert_one(user)
    configuration = {
        "filename": "some_conf.ini",
        "hash": "this_is_right_hash",
        "real_path": f.as_posix(),
        "users": [user_id.inserted_id],
    }
    configuration_id = await setup_db.configurations.insert_one(configuration)

    yield str(configuration_id.inserted_id), f
    await setup_db.users.delete_one({"name": user["name"]})
    await setup_db.configurations.delete_one({"hash": "this_is_right_hash"})
