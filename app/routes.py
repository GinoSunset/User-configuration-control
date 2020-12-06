from .views import api


def setup_routes(app):
    app.router.add_route("GET", "/api/v1/", api.index)
    app.router.add_view("/api/v1/configurations/", api.СonfigurationsView)
    app.router.add_view(
        "/api/v1/configurations/{configuration_id}/", api.ConfigurationDetailView
    )
    app.router.add_view(
        "/api/v1/configurations/{configuration_id}/users/{user_id}",
        api.ConfigurationDetailView,
    )
    app.router.add_view(
        "/api/v1/configurations/{configuration_id}/download/",
        api.СonfigurationDownloadView,
    )
    app.router.add_view("/api/v1/users/", api.UsersView)
    app.router.add_view("/api/v1/users/{user_id}", api.UsersViewDetailsView)
