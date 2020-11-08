import uuid
from pathlib import Path

from aiomongodel import Document, EmbDocField, EmbeddedDocument, ListField, StrField
from pymongo import ASCENDING, IndexModel


class User(Document):
    api_key = StrField(required=True)
    name = StrField(required=True)
    files = ListField(EmbDocField("app.db.Files"), default=lambda: [])

    class Meta:
        collection = "users"
        indexes = [
            IndexModel([("name", ASCENDING)], unique=True),
        ]

    def get_list_of_file_names(self):
        return [f.filename for f in self.files]

    def get_real_path_by_filename(self, filename):
        user_file = list(filter(lambda x: x.filename == filename, self.files))
        if user_file:
            return Path(user_file[0].real_path)
        return None

    def generate_api_key(self):
        return uuid.uuid4()

    def to_json(self):
        return {"name": self.name, "api_key": self.api_key}


class Files(EmbeddedDocument):
    real_path = StrField(required=True)
    filename = StrField(required=True)
