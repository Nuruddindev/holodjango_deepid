"""
Minimal Django settings used only to run this package's own test
suite in isolation (via pytest-django). Not meant to be imported by
consuming projects.
"""

SECRET_KEY = "test-secret-key-not-for-production"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "holodjango_deepid",
]

USE_TZ = True
