"""
Service layer: the actual first-sync logic, independent of any
particular view/API framework. Views (DRF, plain Django, ninja, etc.)
should be thin wrappers around these functions.
"""

from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.db import transaction

from .models import DeepIdentity, FirstSyncToken

User = get_user_model()


class InvalidTokenError(Exception):
    """Raised when a first-sync token is missing, expired, or already consumed."""


@dataclass
class FirstSyncResult:
    user_id: int
    external_id: str


def issue_first_sync_token(user) -> FirstSyncToken:
    """Issue a fresh, single-use first-sync token for `user`."""
    return FirstSyncToken.issue(user)


@transaction.atomic
def consume_first_sync_token(token_value: str) -> FirstSyncResult:
    """
    Validate and consume a first-sync token, returning the identity
    info the Holochain-side agent needs to complete its first sync.

    Raises InvalidTokenError if the token doesn't exist, is expired,
    or has already been consumed.
    """
    try:
        token = FirstSyncToken.objects.select_for_update().get(token=token_value)
    except FirstSyncToken.DoesNotExist as exc:
        raise InvalidTokenError("Token not found.") from exc

    if not token.is_valid:
        raise InvalidTokenError("Token is expired or already consumed.")

    token.mark_consumed()

    identity, _ = DeepIdentity.objects.get_or_create(
        user=token.user,
        defaults={"external_id": str(token.user.pk)},
    )
    identity.mark_synced()

    return FirstSyncResult(user_id=token.user_id, external_id=identity.external_id)


def get_external_id(user) -> str | None:
    """Return the external_id anchor for `user`, if one has been established."""
    try:
        return user.deepid_identity.external_id
    except DeepIdentity.DoesNotExist:
        return None
