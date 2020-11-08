from app.conftest import create_user
import pytest
import requests
import json


class TestAuthCases:
    def test_user_configuration(self):
        r = requests.get("http://localhost:8000/api/v1/files/")
        assert r.status_code == 401
        r = requests.get(
            "http://localhost:8000/api/v1/files/",
            headers={"Authorization": "Token Invalid_token"},
        )
        assert r.status_code == 401

    @pytest.mark.asyncio
    def test_success(self, create_user):
        r = requests.get(
            "http://localhost:8000/api/v1/files/",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status_code == 200


class TestFilesViewCases:
    @pytest.mark.asyncio
    def test_fetch_list_files(self, create_user):
        filename = "test.conf"
        r = requests.get(
            "http://localhost:8000/api/v1/files/",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status_code == 200
        requests.post(
            "http://localhost:8000/api/v1/files/",
            files={"configuration": (f"{filename}", "test file content".encode())},
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        r = requests.get(
            "http://localhost:8000/api/v1/files/",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        response = json.loads(r.content)
        assert response["files"] == [filename]

    @pytest.mark.asyncio
    def test_file_with_eq_name(self, create_user):
        requests.post(
            "http://localhost:8000/api/v1/files/",
            files={"configuration": ("test.conf", "test file content".encode())},
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        r = requests.post(
            "http://localhost:8000/api/v1/files/",
            files={"configuration": ("test.conf", "test file content".encode())},
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status_code == 409
        r = requests.post(
            "http://localhost:8000/api/v1/files/",
            files={"configuration": ("test_new.conf", "test file content".encode())},
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status_code == 201

    @pytest.mark.asyncio
    def test_upload_files(self, create_user):
        r = requests.post(
            "http://localhost:8000/api/v1/files/",
            files={"configuration": ("test.conf", "test file content".encode())},
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status_code == 201

    @pytest.mark.asyncio
    async def test_save_file_on_upload(self, create_user, setup_db):
        requests.post(
            "http://localhost:8000/api/v1/files/",
            files={"configuration": ("test.conf", "test file content".encode())},
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        saved_user = await setup_db.users.find_one({"name": create_user["name"]})
        assert len(saved_user.get("files", [])) == len(create_user.get("files", [])) + 1


class TestFileDetailsViewCases:
    @pytest.mark.asyncio
    def test_get_file(self, create_user_and_files):
        user, user_file = create_user_and_files
        r = requests.get(
            f"http://localhost:8000/api/v1/files/{user['files'][0]['filename']}",
            headers={"Authorization": f"Token {user['api_key']}"},
        )
        assert r.status_code == 200
        assert r.text == user_file.read_text()

    @pytest.mark.asyncio
    def test_not_exists_file(self, create_user):
        r = requests.get(
            f"http://localhost:8000/api/v1/files/not_exists_file",
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status_code == 404


class TestCreateUserViewCases:
    @pytest.mark.asyncio
    def test_api_create_user(self, create_name_for_temp_user):
        r = requests.post(
            f"http://localhost:8000/api/v1/users/",
            data={"name": create_name_for_temp_user},
        )
        assert r.status_code == 201
        assert "api_key" in json.loads(r.content).keys()
