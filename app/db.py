from aiomongodel import Document, StrField
import requests


class User(Document):
    _id = StrField(regex=r"[a-zA-Z0-9_]{3, 20}")
    api_key = StrField(required=True)
    name = StrField(required=True)

    class Meta:
        collection = "users"
