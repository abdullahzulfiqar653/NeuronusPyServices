from django.contrib import admin
from NeuroMail.models.mailbox import MailBox
from NeuroMail.models.email_extension import EmailExtension


class MailBoxAdmin(admin.ModelAdmin):
    list_display = ("user", "email", "password")
    search_fields = ("email",)


admin.site.register(MailBox, MailBoxAdmin)


class EmailExtensionAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


admin.site.register(EmailExtension, EmailExtensionAdmin)
