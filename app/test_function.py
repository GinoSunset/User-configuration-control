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
    # TODO: remove files media after save
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
