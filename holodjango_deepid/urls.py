from django.urls import path

from . import views

app_name = "holodjango_deepid"

urlpatterns = [
    path(
        "first-sync/issue/",
        views.issue_first_sync_token,
        name="issue-first-sync-token",
    ),
    path(
        "first-sync/consume/",
        views.consume_first_sync_token,
        name="consume-first-sync-token",
    ),
]
