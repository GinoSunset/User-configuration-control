from aiohttp.web_middlewares import middleware
from .middleware import token_auth_middleware
from .auth import check_token
from aiohttp import web
from .routes import setup_routes
from pathlib import Path
import motor.motor_asyncio


async def create_app(config: dict):
    app = web.Application(middlewares=[token_auth_middleware(check_token=check_token)])
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
    app["db"] = motor.motor_asyncio.AsyncIOMotorClient(
        config["database_uri"]
    ).control_conf
    print(f"media dir is [{media_dir.as_posix()}]")
    print(f"db uri is [{config['database_uri']}]")


async def on_shutdown(app):
    pass
