from pathlib import Path

import motor.motor_asyncio
from aiohttp import web
from aiohttp.web_middlewares import middleware

from .auth import check_token
from .db import Configuration, User
from .middleware import token_auth_middleware
from .routes import setup_routes


async def create_app(config: dict):
    app = web.Application(
        middlewares=[
            token_auth_middleware(
                check_token=check_token,
                exclude_method_routes=[
                    ("POST", "/api/v1/users/"),
                ],
            )
        ]
    )
    app["config"] = config
    setup_routes(app)
    app.on_startup.append(on_start)
    app.on_cleanup.append(on_shutdown)
    return app


async def on_start(app):
    config = app["config"]
    media_dir = Path(config["media_dir"])
    if not media_dir.exists():
        media_dir.mkdir()
    app["media_dir"] = media_dir
    app["db"] = motor.motor_asyncio.AsyncIOMotorClient(config["database_uri"])[
        config["db_name"]
    ]
    await User.q(app["db"]).create_indexes()
    await Configuration.q(app["db"]).create_indexes()
    print(f"media dir is [{media_dir.as_posix()}]")
    print(f"db uri is [{config['database_uri']}]")


async def on_shutdown(app):
    pass
