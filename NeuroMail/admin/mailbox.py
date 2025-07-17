from django.contrib import admin
from NeuroMail.models.mailbox import MailBox
from NeuroMail.models.email_recipient import EmailRecipient
from NeuroMail.models.email_extension import EmailExtension


class MailBoxAdmin(admin.ModelAdmin):
    list_display = ("user", "email", "password")
    search_fields = ("email",)


admin.site.register(MailBox, MailBoxAdmin)


class EmailRecipientAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "name", "recipient_type")
    search_fields = ("email",)
    autocomplete_fields = ("mail",)


admin.site.register(EmailRecipient, EmailRecipientAdmin)


class EmailExtensionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active")


admin.site.register(EmailExtension, EmailExtensionAdmin)
