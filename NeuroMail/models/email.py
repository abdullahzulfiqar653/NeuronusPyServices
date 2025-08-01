from django.db import models
from django.db.models import Q
from NeuroMail.models.mailbox import MailBox
from main.models.abstract.base import BaseModel


class Email(BaseModel):
    UID_PREFIX = 120
    INBOX = "inbox"
    SENT = "sent"
    DRAFT = "draft"
    TRASH = "trash"
    SPAM = "Junk"

    EMAIL_TYPE_CHOICES = [
        (SENT, "Sent"),
        (INBOX, "Inbox"),
        (DRAFT, "Draft"),
        (TRASH, "Trash"),
        (SPAM, "Spam"),
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
    is_read_by_recipient = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_sent_success = models.BooleanField(default=False)
    imap_uid = models.CharField(max_length=64, editable=False, null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} - {self.email_type} ({self.mailbox.email})"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["mailbox", "imap_uid", "primary_email_type"],
                name="unique_mailbox_email_uid",
                condition=Q(imap_uid__isnull=False),
            )
        ]
