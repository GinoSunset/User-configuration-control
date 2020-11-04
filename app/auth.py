from .db import User


async def check_token(request, token: str):
    return await User.q(request.app["db"]).find_one({"api_key": token})
