import json
import io
from aiohttp import FormData
from bson.objectid import ObjectId
from .app import create_app


class TestAuthCases:
    async def test_user_configuration(self, aiohttp_client, test_conf, loop):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)
        r = await client.get("/api/v1/configurations/")
        assert r.status == 401
        r = await client.get(
            "api/v1/configurations/",
            headers={"Authorization": "Token Invalid_token"},
        )
        assert r.status == 401

    async def test_success(self, aiohttp_client, event_loop, create_user, test_conf):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)
        r = await client.get(
            "api/v1/configurations/",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status == 200


class TestFilesViewCases:
    async def test_fetch_list_files(
        self, aiohttp_client, event_loop, create_user, test_conf
    ):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)
        filename = "test.conf"
        r = await client.get(
            "api/v1/configurations/",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status == 200
        data = FormData()
        data.add_field("configuration", io.StringIO("test content"), filename=filename)
        await client.post(
            "api/v1/configurations/",
            data=data,
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        r = await client.get(
            "api/v1/configurations/",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        text = await r.read()
        response = json.loads(text)
        assert response["configurations"]

    async def test_file_with_eq_hash_and_name(
        self, aiohttp_client, event_loop, create_user, test_conf
    ):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)
        data = FormData()
        data.add_field(
            "configuration", io.StringIO("test content"), filename="test_file"
        )
        await client.post(
            "api/v1/configurations/",
            data=data,
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        data = FormData()
        data.add_field(
            "configuration", io.StringIO("test content"), filename="test_file"
        )
        r = await client.post(
            "api/v1/configurations/",
            data=data,
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status == 409
        data = FormData()
        data.add_field(
            "configuration", io.StringIO("test content"), filename="test_file_new"
        )
        r = await client.post(
            "api/v1/configurations/",
            data=data,
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status == 201

    async def test_upload_files(
        self, aiohttp_client, event_loop, create_user, test_conf
    ):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)
        data = FormData()
        data.add_field(
            "configuration", io.StringIO("test content"), filename="test.conf"
        )
        r = await client.post(
            "api/v1/configurations/",
            data=data,
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status == 201

    async def test_save_file_on_upload(
        self, test_conf, aiohttp_client, event_loop, create_user, setup_db
    ):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)
        data = FormData()
        data.add_field(
            "configuration", io.StringIO("test content"), filename="test.conf"
        )
        r = await client.get(
            "api/v1/configurations/",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        start_configurations = await r.json()
        await client.post(
            "api/v1/configurations/",
            data=data,
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        r = await client.get(
            "api/v1/configurations/",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        after_saved_configuration = await r.json()
        assert (
            len(after_saved_configuration["configurations"])
            == len(start_configurations["configurations"]) + 1
        )


class TestFileDetailsViewCases:
    async def test_get_file(
        self,
        aiohttp_client,
        event_loop,
        create_user,
        create_configuration_with_user,
        test_conf,
    ):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)
        r = await client.get(
            f"api/v1/configurations/{create_configuration_with_user['id']}/download/",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status == 200
        text = await r.text()
        with open(create_configuration_with_user["real_path"], "r") as f:
            assert text == f.read()

    async def test_details_config_with_bad_id(
        self, aiohttp_client, event_loop, create_user, test_conf
    ):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)
        r = await client.get(
            f"api/v1/configurations/not_exists_file/",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status == 400

    async def test_not_exists_file(
        self, aiohttp_client, event_loop, create_user, test_conf
    ):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)
        r = await client.get(
            f"api/v1/configurations/{ObjectId()}",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status == 404

    async def test_add_user_to_config(
        self,
        aiohttp_client,
        event_loop,
        create_user,
        create_configuration_with_user,
        test_conf,
    ):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)
        r = await client.get(
            f"api/v1/configurations/{create_configuration_with_user['id']}/",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status == 200
        text = await r.text()
        conf_before_add_user = json.loads(text)
        r = await client.put(
            f"api/v1/configurations/{create_configuration_with_user['id']}/users/{str(create_user['_id'])}",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status == 201
        text = await r.text()
        conf_after_add_user = json.loads(text)
        assert len(conf_before_add_user["users"]) + 1 == len(
            conf_after_add_user["users"]
        )


class TestCreateUserViewCases:
    async def test_api_create_user(
        self, aiohttp_client, event_loop, create_name_for_temp_user, test_conf
    ):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)
        r = await client.post(
            f"api/v1/users/",
            data={"name": create_name_for_temp_user},
        )
        assert r.status == 201
        text = await r.text()
        assert "api_key" in json.loads(text).keys()


class TestUsersCases:
    async def test_permision_on_list(self, create_user, aiohttp_client, test_conf):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)
        r = await client.get(f"/api/v1/users/")
        assert r.status == 401

    async def test_list_of_user(self, create_user, aiohttp_client, test_conf):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)
        r = await client.get(
            f"/api/v1/users/",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status == 200
        text = await r.text()
        assert [
            {"name": create_user["name"], "id": str(create_user["_id"])}
        ] == json.loads(text)

    async def test_details_user_api(self, create_user, aiohttp_client, test_conf):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)

        r = await client.get(
            f"/api/v1/users/{str(create_user['_id'])}",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status == 200

    async def test_details_user_api_bad_id(
        self, create_user, aiohttp_client, test_conf
    ):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)

        r = await client.get(
            f"/api/v1/users/{str(create_user['_id'])}-bad-format",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status == 400

    async def test_get_configs_by_user_id(
        self,
        create_user,
        aiohttp_client,
        test_conf,
        create_configuration_with_user,
        create_configuration,
    ):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)
        await client.put(
            f"api/v1/configurations/{create_configuration_with_user['id']}/users/{str(create_user['_id'])}",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        await client.put(
            f"api/v1/configurations/{create_configuration['id']}/users/{str(create_user['_id'])}",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        r = await client.get(
            f"/api/v1/users/{str(create_user['_id'])}/configurations/",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status == 200
        text = await r.text()
        user_conf = json.loads(text)
        assert len(user_conf) == 2
