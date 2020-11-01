import requests


def test_user_configuration():
    r = requests.get("http://localhost:8000/api/v1/user/123")
    assert r.status_code == 401
    r = requests.auth
