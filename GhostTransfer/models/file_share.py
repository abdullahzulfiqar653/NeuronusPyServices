from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from main.models.abstract.base import BaseModel


class FileShare(BaseModel):
    files = models.JSONField(default=list)
    # Security / restrictions
    views_used = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(null=True)
    max_views = models.PositiveIntegerField(null=True)
    allowed_ip = models.GenericIPAddressField(null=True)
    password_hash = models.CharField(max_length=128, null=True)

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        if not self.password_hash:
            return True
        return check_password(raw_password, self.password_hash)

    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at

    def can_view(self, ip=None):
        if self.is_expired():
            return False, "Link expired"

        if self.max_views and self.views_used >= self.max_views:
            return False, "View limit reached"

        if self.allowed_ips and ip not in self.allowed_ips:
            return False, "IP not allowed"

        return True, None

    def register_view(self):
        """Call this when a file is successfully accessed"""
        self.views_used += 1
        self.save(update_fields=["views_used"])
