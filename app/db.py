from aiomongodel import Document, StrField, ListField, EmbDocField, EmbeddedDocument


class User(Document):
    _id = StrField(regex=r"[a-zA-Z0-9_]{3, 20}")
    api_key = StrField(required=True)
    name = StrField(required=True)
    files = ListField(EmbDocField("app.db.Files"), default=lambda: [])

    class Meta:
        collection = "users"


class Files(EmbeddedDocument):
    real_path = StrField(required=True)
    filename = StrField(required=True)
