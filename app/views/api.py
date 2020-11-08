import aiohttp
import string
import random
from app.db import Files


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
    with open(path_to_file, "wb") as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            f.write(chunk)


async def save_file_to_fs(request, filename, field):
    media = request.app["media_dir"]
    path_to_file = get_available_file_name(media, filename)
    await write_to_file(path_to_file, field)
    return path_to_file


async def save_file_to_db(request, filename, path_to_file):
    file_model = Files(real_path=path_to_file, filename=filename)
    await request["user"].update(
        request.app["db"], {"$addToSet": {"files": file_model.to_mongo()}}
    )


async def upload_file(request):
    reader = await request.multipart()
    field = await reader.next()
    filename = field.filename

    if filename not in request["user"].get_list_of_file_name():
        path_to_file = await save_file_to_fs(request, filename, field)
        await save_file_to_db(request, filename, path_to_file)
        return aiohttp.web.json_response(
            {"files": [f.filename for f in request["user"].files]},
            status=201,
        )
    return aiohttp.web.json_response(
        {"error": f"configuration {filename} already exist"}, status=409
    )


class FilesView(aiohttp.web.View):
    async def get(self):
        return aiohttp.web.json_response(
            {"files": self.request["user"].get_list_of_file_name()}
        )

    async def post(self):
        return await upload_file(self.request)