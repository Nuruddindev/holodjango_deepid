import pytest
from django.contrib.auth import get_user_model

from holodjango_deepid import services
from holodjango_deepid.models import DeepIdentity, FirstSyncToken

User = get_user_model()


@pytest.mark.django_db
def test_issue_and_consume_first_sync_token():
    user = User.objects.create_user(username="nila")

    token = services.issue_first_sync_token(user)
    assert token.is_valid

    result = services.consume_first_sync_token(token.token)
    assert result.user_id == user.pk
    assert result.external_id == str(user.pk)

    token.refresh_from_db()
    assert not token.is_valid


@pytest.mark.django_db
def test_consuming_twice_fails():
    user = User.objects.create_user(username="nila")
    token = services.issue_first_sync_token(user)

    services.consume_first_sync_token(token.token)

    with pytest.raises(services.InvalidTokenError):
        services.consume_first_sync_token(token.token)


@pytest.mark.django_db
def test_unknown_token_fails():
    with pytest.raises(services.InvalidTokenError):
        services.consume_first_sync_token("does-not-exist")


@pytest.mark.django_db
def test_get_external_id_before_sync_is_none():
    user = User.objects.create_user(username="nila")
    assert services.get_external_id(user) is None
