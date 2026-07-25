from django.core.management.base import BaseCommand
from django.utils import timezone

from holodjango_deepid.models import FirstSyncToken


class Command(BaseCommand):
    help = (
        "Delete expired or consumed first-sync tokens. Tokens are ephemeral "
        "by design (used once at first sync, then discarded) — this command "
        "just clears the bookkeeping rows so they don't accumulate."
    )

    def handle(self, *args, **options):
        expired = FirstSyncToken.objects.filter(expires_at__lt=timezone.now())
        consumed = FirstSyncToken.objects.exclude(consumed_at__isnull=True)
        stale = (expired | consumed).distinct()

        count = stale.count()
        stale.delete()
        self.stdout.write(self.style.SUCCESS(f"Pruned {count} stale first-sync token(s)."))
