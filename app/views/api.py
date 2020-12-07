import aiohttp
import string
import random
import hashlib
import os
from pathlib import Path

from aiomongodel.errors import DuplicateKeyError, DocumentNotFoundError
from bson.errors import InvalidId
from bson.objectid import ObjectId

from app.db import Configuration, User


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


async def write_to_file_with_calc_hash(path_to_file, field, hash_func):
    h = hashlib.new(hash_func)
    with open(path_to_file, "wb") as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            h.update(chunk)
            f.write(chunk)
    return h.hexdigest()


async def save_file_to_fs(request, filename, field):
    media = request.app["media_dir"]
    hash_func = request.app["config"]["hash_func"]
    path_to_file = get_available_file_name(media, filename)
    hash = await write_to_file_with_calc_hash(path_to_file, field, hash_func)
    return path_to_file, hash


async def save_file_to_db(request, filename, path_to_file, hash):
    configuration_model = Configuration(
        real_path=path_to_file, filename=filename, hash=hash
    )
    await configuration_model.save(request.app["db"])
    return configuration_model


async def upload_file(request):
    reader = await request.multipart()
    field = await reader.next()
    filename = field.filename

    path_to_file, hash = await save_file_to_fs(request, filename, field)
    try:
        configuration = await save_file_to_db(request, filename, path_to_file, hash)
    except DuplicateKeyError:
        path_to_file.unlink()
        return aiohttp.web.json_response(
            {"error": f"configuration {filename} already exist"}, status=409
        )
    return aiohttp.web.json_response(
        {"configuration": configuration.to_json()},
        status=201,
    )


class СonfigurationsView(aiohttp.web.View):
    async def get(self):
        configurations = [
            configuration.to_json()
            async for configuration in Configuration.q(self.request.app["db"]).find({})
        ]
        return aiohttp.web.json_response({"configurations": configurations})

    async def post(self):
        return await upload_file(self.request)


async def download_file(configuration):
    file_path = getattr(configuration, "real_path")
    if file_path:
        file_path = Path(file_path)
    if (file_path is None) or (not file_path.exists()):
        raise FileNotFoundError
    with open(file_path, "rb") as f:
        data = f.read()
    return configuration.filename, data


async def get_configuration_by_id(db, id) -> Configuration:
    configuration_id = ObjectId(id)
    return await Configuration.q(db).get(configuration_id)


class СonfigurationDownloadView(aiohttp.web.View):
    async def get(self):
        id = self.request.match_info["configuration_id"]
        try:
            configuration = await get_configuration_by_id(self.request.app["db"], id)
            filename, data = await download_file(configuration)
        except InvalidId:
            return aiohttp.web.json_response({"error": f"bad id format"}, status=400)
        except (DocumentNotFoundError, FileNotFoundError):
            return aiohttp.web.json_response(
                {"error": f"file with id {id} not exist"}, status=404
            )
        return aiohttp.web.Response(
            body=data,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )


class ConfigurationDetailView(aiohttp.web.View):
    async def get(self):
        id = self.request.match_info["configuration_id"]
        try:
            configuration = await get_configuration_by_id(self.request.app["db"], id)
        except InvalidId:
            return aiohttp.web.json_response({"error": f"bad id format"}, status=400)
        except DocumentNotFoundError:
            return aiohttp.web.json_response(
                {"error": f"file with id {id} not exist"}, status=404
            )
        return aiohttp.web.json_response(configuration.to_json())

    async def put(self):
        raw_id_conf = self.request.match_info["configuration_id"]
        raw_id_user = self.request.match_info["user_id"]
        try:
            configuration = await get_configuration_by_id(
                self.request.app["db"], raw_id_conf
            )
        except InvalidId:
            return aiohttp.web.json_response(
                {"error": f"bad configuration id format"}, status=400
            )
        except DocumentNotFoundError:
            return aiohttp.web.json_response(
                {"error": f"file with id {raw_id_conf} not exist"}, status=404
            )
        try:
            user_id = ObjectId(raw_id_user)
        except InvalidId:
            return aiohttp.web.json_response(
                {"error": f"bad user id format"}, status=400
            )
        try:
            user = await User.q(self.request.app["db"]).get(user_id)
        except DocumentNotFoundError:
            return aiohttp.web.json_response(
                {"error": f"user with id {raw_id_user} not exist"}, status=404
            )
        configuration.add_user(user)
        configuration.validate()
        await configuration.save(self.request.app["db"])
        return aiohttp.web.json_response(configuration.to_json(), status=201)


class UsersView(aiohttp.web.View):
    async def create_user(self):
        data = await self.request.post()
        user = User(name=data["name"])
        user.api_key = user.generate_api_key()
        try:
            await user.save(self.request.app["db"])
        except DuplicateKeyError:
            return aiohttp.web.json_response(
                {"error": f"user already exists"}, status=409
            )
        return aiohttp.web.json_response(
            user.to_json(),
            status=201,
        )

    async def post(self):
        return await self.create_user()

    async def get(self):
        users = [
            user.to_json_without_api_key()
            async for user in User.q(self.request.app["db"]).find({})
        ]
        return aiohttp.web.json_response(users)


class UsersViewDetailsView(aiohttp.web.View):
    async def get(self):
        id = self.request.match_info["user_id"]
        try:
            user_id = ObjectId(id)
        except InvalidId:
            return aiohttp.web.json_response({"error": f"bad id format"}, status=400)
        try:
            user = await User.q(self.request.app["db"]).get(user_id)
        except DocumentNotFoundError:
            return aiohttp.web.json_response(
                {"error": f"user with id {user_id} not exist"}, status=404
            )
        return aiohttp.web.json_response(user.to_json())


class UserConfigutationsViewDetailsView(aiohttp.web.View):
    async def get(self):
        id = self.request.match_info["user_id"]
        try:
            user_id = ObjectId(id)
        except InvalidId:
            return aiohttp.web.json_response({"error": f"bad id format"}, status=400)
        try:
            user = await User.q(self.request.app["db"]).get(user_id)
        except DocumentNotFoundError:
            return aiohttp.web.json_response(
                {"error": f"user with id {user_id} not exist"}, status=404
            )
        configuration_query = Configuration.q(self.request.app["db"]).find(
            {"users": user_id}
        )
        configururations = [
            configuration.to_json() async for configuration in configuration_query
        ]
        return aiohttp.web.json_response(configururations)
