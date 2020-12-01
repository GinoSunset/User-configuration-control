import json
import io
from aiohttp import FormData
from .app import create_app


class TestAuthCases:
    async def test_user_configuration(self, aiohttp_client, test_conf, loop):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)
        r = await client.get("/api/v1/files/")
        assert r.status == 401
        r = await client.get(
            "api/v1/files/",
            headers={"Authorization": "Token Invalid_token"},
        )
        assert r.status == 401

    async def test_success(self, aiohttp_client, event_loop, create_user, test_conf):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)
        r = await client.get(
            "api/v1/files/",
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
            "api/v1/files/",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status == 200
        data = FormData()
        data.add_field("configuration", io.StringIO("test content"), filename=filename)
        await client.post(
            "api/v1/files/",
            data=data,
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        r = await client.get(
            "api/v1/files/",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        text = await r.read()
        response = json.loads(text)
        assert response["files"] == [filename]

    async def test_file_with_eq_name(
        self, aiohttp_client, event_loop, create_user, test_conf
    ):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)
        data = FormData()
        data.add_field(
            "configuration", io.StringIO("test content"), filename="test_file"
        )
        await client.post(
            "api/v1/files/",
            data=data,
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        data = FormData()
        data.add_field(
            "configuration", io.StringIO("test content"), filename="test_file"
        )
        r = await client.post(
            "api/v1/files/",
            data=data,
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status == 409
        data = FormData()
        data.add_field(
            "configuration", io.StringIO("test content"), filename="test_file_new"
        )
        r = await client.post(
            "api/v1/files/",
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
            "api/v1/files/",
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
        r = await client.post(
            "api/v1/files/",
            data=data,
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        saved_user = await r.json()
        assert len(saved_user.get("files", [])) == len(create_user.get("files", [])) + 1


class TestFileDetailsViewCases:
    async def test_get_file(
        self, aiohttp_client, event_loop, create_user_and_files, test_conf
    ):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)
        user, user_file = create_user_and_files
        r = await client.get(
            f"api/v1/files/{user['files'][0]['filename']}",
            headers={"Authorization": f"Token {user['api_key']}"},
        )
        assert r.status == 200
        text = await r.text()

        assert text == user_file.read_text()

    async def test_not_exists_file(
        self, aiohttp_client, event_loop, create_user, test_conf
    ):
        app = await create_app(config=test_conf)
        client = await aiohttp_client(app)
        r = await client.get(
            f"api/v1/files/not_exists_file",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status == 404


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


class TestListUsersFileCases:
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
        assert [{"name": f"{create_user['name']}"}] == json.loads(text)
