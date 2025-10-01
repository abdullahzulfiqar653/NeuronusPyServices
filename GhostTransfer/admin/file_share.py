from django.contrib import admin
from .models import FileShare


@admin.register(FileShare)
class FileShareAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "views_used",
        "max_views",
        "expires_at",
        "allowed_ip",
        "is_expired_display",
    )
    list_filter = ("expires_at",)
    search_fields = ("id", "message", "allowed_ip")
    readonly_fields = ("views_used", "password_hash")

    def is_expired_display(self, obj):
        return obj.is_expired()

    is_expired_display.boolean = True
    is_expired_display.short_description = "Expired"
