from django.db import models
from main.models.abstract.base import BaseModel
from NeuroMail.models.mailbox import MailBox


class Email(BaseModel):
    UID_PREFIX = 120
    INBOX = "inbox"
    SENT = "sent"
    DRAFT = "draft"
    TRASH = "trash"

    EMAIL_TYPE_CHOICES = [
        (SENT, "Sent"),
        (INBOX, "Inbox"),
        (DRAFT, "Draft"),
        (TRASH, "Trash"),
    ]

    mailbox = models.ForeignKey(
        MailBox, on_delete=models.CASCADE, related_name="emails"
    )
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)
    email_type = models.CharField(
        max_length=10, choices=EMAIL_TYPE_CHOICES, default=DRAFT
    )
    primary_email_type = models.CharField(
        max_length=10, choices=EMAIL_TYPE_CHOICES, null=True, blank=True
    )
    is_starred = models.BooleanField(default=False)
    is_seen = models.BooleanField(default=False)
    total_size = models.BigIntegerField(default=0)
    is_viewed_by_recepient = models.BooleanField(default=False)
    seen_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.subject} - {self.email_type} ({self.mailbox.email})"