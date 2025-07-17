from django.db import models

from main.models.abstract.base import BaseModel
from NeuroMail.models.email import Email


class EmailRecipient(BaseModel):
    UID_PREFIX = 122
    TO = "to"
    CC = "cc"
    BCC = "bcc"
    FROM = "from"

    RECIPIENT_TYPE_CHOICES = [
        (TO, "To"),
        (CC, "CC"),
        (BCC, "BCC"),
        (FROM, "FROM"),
    ]

    mail = models.ForeignKey(Email, on_delete=models.CASCADE, related_name="recipients")
    email = models.EmailField()
    name = models.CharField(max_length=256, null=True, blank=True)
    recipient_type = models.CharField(max_length=10, choices=RECIPIENT_TYPE_CHOICES)

    def __str__(self):
        return f"{self.email} ({self.recipient_type})"
