from django.db import models
from main.models.abstract.base import BaseModel


class Password(BaseModel):
    url = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    title = models.TextField()
    username = models.TextField(null=True, blank=True)
    password = models.TextField(null=True, blank=True)
    emoji = models.TextField(null=True, blank=True)    
    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="passwords"
    )
    folder = models.ForeignKey(
        "PasswordManager.Folder",
        on_delete=models.CASCADE,
        related_name="folder_passwords",
    )
    file = models.FileField(upload_to="protected/passwords/attachments/", null=True)
    content_type = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.title

    class Meta:
        unique_together = ["title", "user"]
