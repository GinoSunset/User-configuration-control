import uuid
from pathlib import Path
from _pytest.config import Config
from bson import ObjectId
from aiomongodel import (
    Document,
    RefField,
    ListField,
    StrField,
    ObjectIdField,
)
from pymongo import ASCENDING, IndexModel


class User(Document):
    _id = ObjectIdField(default=lambda: ObjectId())
    api_key = StrField(required=True)
    name = StrField(required=True)

    class Meta:
        collection = "users"
        indexes = [
            IndexModel([("api_key", ASCENDING)], unique=True),
        ]

    def generate_api_key(self):
        return uuid.uuid4()

    def to_json(self):
        return {"name": self.name, "api_key": self.api_key}

    def to_json_without_api_key(self):
        return {"name": self.name, "id": str(self._id)}


class Configuration(Document):
    real_path = StrField(required=True)
    filename = StrField(required=True)
    hash = StrField(required=True)
    users = ListField(RefField("app.db.User"), default=lambda: list())

    class Meta:
        collection = "configurations"
        indexes = [
            IndexModel(
                [("hash", ASCENDING), ("filename", ASCENDING)],
                name="hash_and_filename",
                unique=True,
            )
        ]

    def to_json(self, *args, **kwargs):
        data = self.to_data(*args, **kwargs)
        if "real_path" in data.keys():
            data.pop("real_path")
        data["_id"] = str(self._id)
        return data
