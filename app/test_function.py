from app.conftest import create_user
import pytest
import requests


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
    def test_fetch_list_files(self, create_user):
        assert False

    def test_file_with_eq_name(self):
        assert False

    @pytest.mark.asyncio
    def test_upload_files(self, create_user):
        r = requests.post(
            "http://localhost:8000/api/v1/files/",
            files={"configuration": ("test.conf", "test file content".encode())},
            headers={"Authorization": f"Token {create_user['api_key']}"},
        )
        assert r.status_code == 201
