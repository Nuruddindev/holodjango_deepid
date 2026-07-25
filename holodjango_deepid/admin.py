from django.contrib import admin

from .models import DeepIdentity, FirstSyncToken


@admin.register(FirstSyncToken)
class FirstSyncTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "expires_at", "consumed_at", "is_valid")
    list_filter = ("consumed_at",)
    search_fields = ("user__username", "token")
    readonly_fields = ("token", "created_at")

    @admin.display(boolean=True)
    def is_valid(self, obj):
        return obj.is_valid


@admin.register(DeepIdentity)
class DeepIdentityAdmin(admin.ModelAdmin):
    list_display = ("user", "external_id", "first_synced_at", "last_synced_at")
    search_fields = ("user__username", "external_id")
