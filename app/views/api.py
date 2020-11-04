import aiohttp
from pathlib import Path

from requests.api import request


async def index(request):
    site_name = request.app["config"].get("site_name")
    return aiohttp.web.json_response({"site_name": site_name})


async def files_list(request):

    reader = await request.multipart()

    field = await reader.next()
    filename = field.filename
    size = 0
    media = request.app["media_dir"]
    with open(media / filename, "wb") as f:
        while True:
            chunk = await field.read_chunk()  # 8192 bytes by default.
            if not chunk:
                break
            size += len(chunk)
            f.write(chunk)

    return aiohttp.web.json_response(
        {"text": "{} sized of {} successfully stored" "".format(filename, size)},
        status=201,
    )


class FilesView(aiohttp.web.View):
    async def get(self):
        return await aiohttp.web.Response()

    async def post(self):
        return await files_list(self.request)