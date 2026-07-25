from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

import holodjango_deepid.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DeepIdentity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "external_id",
                    models.CharField(
                        help_text="Stable identifier anchored via ExternalHash() on the Holochain side.",
                        max_length=128,
                        unique=True,
                    ),
                ),
                ("first_synced_at", models.DateTimeField(blank=True, null=True)),
                ("last_synced_at", models.DateTimeField(blank=True, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="deepid_identity",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FirstSyncToken",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "token",
                    models.CharField(
                        default=holodjango_deepid.models._generate_token,
                        max_length=64,
                        unique=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
                ("consumed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="deepid_first_sync_tokens",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="firstsynctoken",
            index=models.Index(
                fields=["token"], name="holodjango__token_5f1a4c_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="firstsynctoken",
            index=models.Index(
                fields=["user", "consumed_at"], name="holodjango__user_id_c5e8a1_idx"
            ),
        ),
    ]
