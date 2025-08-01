from django.contrib import admin
from django.utils.html import format_html

from NeuroMail.models import Email, EmailAttachment, EmailRecipient, TempMail


class EmailAttachmentInline(admin.TabularInline):
    model = EmailAttachment
    extra = 0  # No extra empty rows
    fields = ("filename", "content_type")
    readonly_fields = ("filename", "content_type")
    show_change_link = True


class EmailRecipientInline(admin.TabularInline):
    model = EmailRecipient
    extra = 0  # No extra empty rows
    fields = ("email", "name", "recipient_type")
    readonly_fields = ("email", "name", "recipient_type")
    show_change_link = True


class EmailAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "imap_id",
        "subject",
        "email_type",
        "mailbox",
        "is_starred",
        "read",
        "read_at",
    )

    search_fields = ("id", "subject", "email_type", "mailbox__email")

    list_filter = (
        "email_type",
        "is_starred",
        "is_seen",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject",
                    "body",
                    "email_type",
                    "primary_email_type",
                    "is_starred",
                    "is_seen",
                    "is_read_by_recipient",
                    "read_at",
                    "total_size",
                    "mailbox",
                ),
            },
        ),
    )

    readonly_fields = ("total_size", "imap_id")

    def read(self, obj) -> bool:
        return obj.is_read_by_recipient

    read.boolean = True
    read.short_description = "read"
    inlines = [EmailAttachmentInline, EmailRecipientInline]


admin.site.register(Email, EmailAdmin)
admin.site.register(TempMail)
