"""
Core models for holodjango_deepid.

Follows the pattern proven in NFB Den: Django is the identity authority.
A short-lived, single-use token is issued to let a Holochain agent bring
a user's identity into the DHT on first sync. The token itself is never
stored long-term once consumed — it exists only to bootstrap trust once
per device.

This module intentionally does NOT store AgentPubKey <-> User mappings.
That resolution lives in the hc_deepid zome (ExternalHash(django_id) is
the anchor); Django only needs to know its own users and issue/validate
tokens against them.
"""

import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

# How long a first-sync token remains valid before it must be reissued.
DEFAULT_TOKEN_TTL_SECONDS = getattr(
    settings, "HOLODJANGO_DEEPID_TOKEN_TTL_SECONDS", 300
)


def _generate_token() -> str:
    return secrets.token_urlsafe(32)


class FirstSyncToken(models.Model):
    """
    An ephemeral, single-use token that authorizes one Holochain agent
    to pull this user's profile data into the DHT for the first time.

    Lifecycle:
      1. Issued (via `FirstSyncToken.issue(user)`) when a device needs
         to sync for the first time.
      2. Presented once to the Holochain-side first-sync flow.
      3. Consumed (`mark_consumed()`) immediately after successful use.
         Consumed/expired tokens are not valid for reuse.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="deepid_first_sync_tokens",
    )
    token = models.CharField(max_length=64, unique=True, default=_generate_token)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["user", "consumed_at"]),
        ]

    def __str__(self) -> str:
        status = "consumed" if self.consumed_at else "active"
        return f"FirstSyncToken(user={self.user_id}, {status})"

    @classmethod
    def issue(cls, user, ttl_seconds: int = DEFAULT_TOKEN_TTL_SECONDS) -> "FirstSyncToken":
        """Issue a new first-sync token for `user`, valid for `ttl_seconds`."""
        return cls.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(seconds=ttl_seconds),
        )

    @property
    def is_valid(self) -> bool:
        return self.consumed_at is None and self.expires_at > timezone.now()

    def mark_consumed(self) -> None:
        self.consumed_at = timezone.now()
        self.save(update_fields=["consumed_at"])


class DeepIdentity(models.Model):
    """
    Tracks the external identity anchor for a Django user, i.e. the
    stable `django_id` that hc_deepid's `ExternalHash(django_id)` is
    built from, plus bookkeeping about sync state.

    This is deliberately thin: it does not know about individual
    AgentPubKeys or devices. That multi-device resolution is the
    hc_deepid zome's job on the Holochain side.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="deepid_identity",
    )
    external_id = models.CharField(
        max_length=128,
        unique=True,
        help_text="Stable identifier anchored via ExternalHash() on the Holochain side.",
    )
    first_synced_at = models.DateTimeField(null=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"DeepIdentity(user={self.user_id}, external_id={self.external_id})"

    def mark_synced(self) -> None:
        now = timezone.now()
        if self.first_synced_at is None:
            self.first_synced_at = now
        self.last_synced_at = now
        self.save(update_fields=["first_synced_at", "last_synced_at"])
