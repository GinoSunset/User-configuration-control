from aiohttp.web_middlewares import middleware
from .middleware import token_auth_middleware
from .auth import check_token
from aiohttp import web
from .routes import setup_routes
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
    app["db"] = motor.motor_asyncio.AsyncIOMotorClient().control_conf


async def on_shutdown(app):
    await app["db"].close()
