import aiohttp
import json


async def index(request):
    site_name = request.app["config"].get("site_name")
    return aiohttp.web.Response(body=json.dumps({"Body": site_name}))
