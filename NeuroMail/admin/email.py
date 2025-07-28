from django.contrib import admin
from django.utils.html import format_html
from NeuroMail.models import Email, EmailAttachment, EmailRecipient, TempMail
from NeuroMail.models.email_log import EmailLog


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
        "subject",
        "email_type",
        "primary_email_type",
        "mailbox",
        "is_starred",
        "is_seen",
        "total_size",
        "mailbox_email",
    )

    def mailbox_email(self, obj):
        return format_html(
            "<a href='mailto:{}'>{}</a>", obj.mailbox.email, obj.mailbox.email
        )

    mailbox_email.short_description = "Mailbox Email"

    search_fields = ("id", "subject", "email_type", "mailbox__email")
    list_filter = ("email_type", "is_starred", "is_seen")

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
                    "total_size",
                    "mailbox",
                ),
            },
        ),
    )

    readonly_fields = ("total_size",)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    inlines = [EmailAttachmentInline, EmailRecipientInline]

# Register the model with the custom admin class
admin.site.register(Email, EmailAdmin)
admin.site.register(TempMail)

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('email_id', 'is_seen', 'seen_at')
    search_fields = ('email_id',)
    list_filter = ('is_seen',)
    readonly_fields = ('email_id', 'is_seen', 'seen_at')