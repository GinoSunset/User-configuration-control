from .views import api


def setup_routes(app):
    app.router.add_route("GET", "/api/v1/", api.index)
    app.router.add_view("/api/v1/files/", api.FilesView)
    app.router.add_view("/api/v1/files/{filename}", api.FileDetailsView)
    app.router.add_view("/api/v1/users/", api.UsersView)
