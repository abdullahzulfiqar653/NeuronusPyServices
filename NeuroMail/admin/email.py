from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter

from NeuroMail.models import Email, EmailAttachment, EmailRecipient, TempMail


class RecipientSeenFilter(SimpleListFilter):
    title = 'Seen by Recipient'
    parameter_name = 'is_viewed_by_recepient'

    def lookups(self, request, model_admin):
        return (
            ('seen', 'Seen'),
            ('unseen', 'Unseen'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'seen':
            return queryset.filter(is_viewed_by_recepient=True)
        elif self.value() == 'unseen':
            return queryset.filter(is_viewed_by_recepient=False)
        return queryset


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
        "uid",
        "subject",
        "email_type",
        "primary_email_type",
        "mailbox",
        "is_starred",
        "is_seen",
        "is_viewed_by_recepient",
        "seen_at",
        "total_size",
        "mailbox_email",
    )

    search_fields = ("id", "subject", "email_type", "mailbox__email")

    list_filter = (
        "email_type",
        "is_starred",
        "is_seen",
        RecipientSeenFilter,  
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
                    "seen_at",
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
