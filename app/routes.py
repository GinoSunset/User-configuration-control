from .views import api


def setup_routes(app):
    app.router.add_route("GET", "/api/v1/", api.index)
