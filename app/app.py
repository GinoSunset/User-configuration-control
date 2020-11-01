from aiohttp import web
from .routes import setup_routes
import motor.motor_asyncio


async def create_app(config: dict):
    app = web.Application()
    app["config"] = config
    setup_routes(app)
    app.on_startup.append(on_start)
    app.on_cleanup.append(on_shutdown)
    return app


async def on_start(app):
    config = app["config"]
    app["db"] = motor.motor_asyncio.AsyncIOMotorClient(config["database_uri"])


async def on_shutdown(app):
    await app["db"].close()
