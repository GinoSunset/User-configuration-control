import aiohttp
from pathlib import Path
import string
import random

from requests.api import request


async def index(request):
    site_name = request.app["config"].get("site_name")
    return aiohttp.web.json_response({"site_name": site_name})


def get_available_file_name(media, filename):
    path_to_file = media / filename
    while path_to_file.exists():
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters) for i in range(6))
        filename = "%s_%s%s" % (path_to_file.stem, random_string, path_to_file.suffix)
        path_to_file = media / filename
    return path_to_file


async def write_to_file(path_to_file, field):
    size = 0
    with open(path_to_file, "wb") as f:
        while True:
            chunk = await field.read_chunk()  # 8192 bytes by default.
            if not chunk:
                break
            size += len(chunk)
            f.write(chunk)
    return size


async def upload_file(request):
    reader = await request.multipart()
    field = await reader.next()
    filename = field.filename
    media = request.app["media_dir"]
    path_to_file = get_available_file_name(media, filename)
    size = await write_to_file(path_to_file, field)

    return aiohttp.web.json_response(
        {"text": f"{filename} sized of {size} successfully save"},
        status=201,
    )


class FilesView(aiohttp.web.View):
    async def get(self):
        return aiohttp.web.json_response({"files": None})

    async def post(self):
        return await upload_file(self.request)