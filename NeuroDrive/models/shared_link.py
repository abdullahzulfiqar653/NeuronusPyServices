from django.db import models
from django.utils import timezone
import uuid

class SharedLink(models.Model):
    file = models.FileField(upload_to='shared_link/')
    file_name = models.CharField(max_length=255)
    
    allowed_views = models.PositiveIntegerField(null=True, blank=True)
    used_views = models.PositiveIntegerField(default=0)
    ends_at = models.DateTimeField(null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    allowed_ip = models.GenericIPAddressField(null=True, blank=True)
    s3_url = models.CharField(max_length=256)
    public_key = models.CharField(max_length=45, unique=True, default=uuid.uuid4().hex)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return self.ends_at and timezone.now() > self.ends_at
    
    def can_access(self, ip=None, password=None):
        if self.is_expired():
            return False, "Link expired"
        if self.allowed_views is not None and self.used_views >= self.allowed_views:
            return False, "View limit reached"
        if self.password and self.password != password:
            return False, "Password incorrect"
        if self.allowed_ip and self.allowed_ip != ip:
            return False, "IP restricted"
        return True, "Access granted"
    
    def increment_views(self):
        if self.allowed_views is not None:
            self.used_views += 1
            self.save()
