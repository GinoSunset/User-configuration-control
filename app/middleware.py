from typing import Callable, List
from aiohttp import web
from aiomongodel.errors import DocumentNotFoundError


def is_exclude_requests(request, exclude_method_routes):
    return (request.method, request.path) in exclude_method_routes


def token_auth_middleware(
    check_token: Callable,
    auth_scheme: str = "Token",
    request_property: str = "user",
    exclude_method_routes: List[str] = None,
):
    @web.middleware
    async def middleware(request, handler):
        if is_exclude_requests(request, exclude_method_routes):
            return await handler(request)
        try:
            scheme, token = request.headers["Authorization"].strip().split(" ")
        except KeyError:
            raise web.HTTPUnauthorized(
                reason="Missing authorization header",
                headers={
                    "WWW-Authenticate": 'Token realm="Access to the staging site"',
                },
            )
        except ValueError:
            raise web.HTTPForbidden(
                reason="Invalid authorization header",
            )

        if auth_scheme.lower() != scheme.lower():
            raise web.HTTPForbidden(
                reason="Invalid token scheme",
            )
        try:
            user = await check_token(request, token)
        except DocumentNotFoundError:
            raise web.HTTPUnauthorized(reason="Insvalid token")
        except Exception as e:
            raise web.HTTPForbidden()
        if user:
            request[request_property] = user
        else:
            raise web.HTTPForbidden(
                reason="Token doesn't exist",
                headers={
                    "WWW-Authenticate": 'Token realm="Access to the staging site"',
                },
            )

        return await handler(request)

    return middleware