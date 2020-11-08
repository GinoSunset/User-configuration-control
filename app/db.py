from aiomongodel import Document, StrField, ListField, EmbDocField, EmbeddedDocument


class User(Document):
    _id = StrField(regex=r"[a-zA-Z0-9_]{3, 20}")
    api_key = StrField(required=True)
    name = StrField(required=True)
    files = ListField(EmbDocField("app.db.Files"), default=lambda: [])

    class Meta:
        collection = "users"

    def get_list_of_file_names(self):
        return [f.filename for f in self.files]

    def get_real_path_by_filename(self, filename):
        user_file = list(filter(lambda x: x.filename == filename, self.files))
        if user_file:
            return user_file[0].real_path
        return None


class Files(EmbeddedDocument):
    real_path = StrField(required=True)
    filename = StrField(required=True)
