from django.apps import AppConfig


class VideosAppConfig(AppConfig):
    """App configuration for the videos_app Django application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'videos_app'

    def ready(self):
        """Imports signals so they are registered when the app starts."""
        import videos_app.signals  # noqa: F401
