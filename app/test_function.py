import pytest
import requests


def test_user_configuration():
    r = requests.get("http://localhost:8000/api/v1/user/")
    assert r.status_code == 401
    r = requests.get(
        "http://localhost:8000/api/v1/user/123",
        headers={"Authorization": "Token Invalid_token"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
def test_success(create_user):
    r = requests.get(
        "http://localhost:8000/api/v1/user/",
        headers={"Authorization": f"Token {create_user['api_key']}"},
    )
    assert r.status_code == 200