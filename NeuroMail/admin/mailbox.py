from django.contrib import admin
from NeuroMail.models.mailbox import MailBox


class MailBoxAdmin(admin.ModelAdmin):
    list_display = ("user", "email", "password")
    search_fields = ("email",)


admin.site.register(MailBox, MailBoxAdmin)
