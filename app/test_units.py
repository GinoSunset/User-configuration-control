from collections import namedtuple
import pytest

from app.middleware import is_exclude_requests


class TestMiddlewareCases:
    @pytest.mark.parametrize(
        "req,exclude_path,expected",
        (
            (("GET", "/api/v1/"), [("GET", "/api/v1/")], True),
            (("GET", "/api/v1/"), [("POST", "/api/v1/")], False),
            (("GET", "/api/v1/auth"), [("GET", "/api/v1/")], False),
            (("GET", "/api/v1/auth"), [("GET", "/api/v1/au")], False),
            (("GET", "/api/v1/auth"), [("GET", "/api/v1/au")], False),
            (
                ("GET", "/api/v1/auth"),
                [("GET", "/api/v1/auth1"), ("GET", "/api/v1/auth")],
                True,
            ),
        ),
    )
    def test_is_exclude_requests_func(self, req, exclude_path, expected):
        req_ = namedtuple("request", "method path")
        req_.method, req_.path = req
        assert is_exclude_requests(req_, exclude_path) is expected
