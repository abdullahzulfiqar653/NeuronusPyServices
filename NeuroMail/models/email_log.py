from django.db import models
from django.utils import timezone
import uuid


class EmailLog(models.Model):
    email_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_seen = models.BooleanField(default=False)
    sent_at = models.DateTimeField(default=timezone.now)
    seen_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Email to {self.email} (ID: {self.email_id})"
