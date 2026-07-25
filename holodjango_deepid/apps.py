from django.apps import AppConfig


class HolodjangoDeepidConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "holodjango_deepid"
    verbose_name = "Holochain DeepID (Django)"

    def ready(self):
        # Import signal handlers here once they exist, e.g.:
        # from . import signals  # noqa: F401
        pass
