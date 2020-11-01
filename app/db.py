from aiomongodel import Document, StrField, SynonymField


class User(Document):
    _id = StrField(regex=r"[a-zA-Z0-9_]{3, 20}")
    api_key = StrField(required=False)

    name = SynonymField(_id)

    class Meta:
        collection = "users"
