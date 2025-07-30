from django.contrib import admin
from django.utils.html import format_html

from NeuroMail.models import Email, EmailAttachment, EmailRecipient, TempMail


class EmailAttachmentInline(admin.TabularInline):
    model = EmailAttachment
    extra = 0
    fields = ("filename", "content_type")
    readonly_fields = ("filename", "content_type")
    show_change_link = True


class EmailRecipientInline(admin.TabularInline):
    model = EmailRecipient
    extra = 0
    fields = ("email", "name", "recipient_type")
    readonly_fields = ("email", "name", "recipient_type")
    show_change_link = True


class EmailAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "imap_id",
        "subject",
        "email_type",
        "primary_email_type",
        "mailbox",
        "is_starred",
        "is_seen",
        "is_viewed_by_recepient",
        "viewed_at",
        "total_size",
        "mailbox_email",
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
                    "is_viewed_by_recepient",
                    "viewed_at",
                    "total_size",
                    "mailbox",
                ),
            },
        ),
    )

    readonly_fields = ("total_size",)

    def mailbox_email(self, obj):
        return format_html(
            "<a href='mailto:{}'>{}</a>", obj.mailbox.email, obj.mailbox.email
        )

    mailbox_email.short_description = "Mailbox Email"

    inlines = [EmailAttachmentInline, EmailRecipientInline]


admin.site.register(Email, EmailAdmin)
admin.site.register(TempMail)
