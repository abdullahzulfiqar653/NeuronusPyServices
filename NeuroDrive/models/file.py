from django.db import models
from main.models.abstract.base import BaseModel


class File(BaseModel):
    name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    metadata = models.JSONField(null=True, blank=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    owner = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="files"
    )
    directory = models.ForeignKey(
        "NeuroDrive.Directory",
        null=True,
        on_delete=models.CASCADE,
        related_name="files",
    )
    size = models.PositiveIntegerField()  # Size in bytes
    s3_url = models.CharField(max_length=256)
    is_starred = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def move_to_folder(self, new_folder):
        """Move file to another folder"""
        self.folder = new_folder
        self.save()

    def size_in_gb(self):
        return self.size / (1024 * 1024 * 1024)

    class Meta:
        unique_together = ("owner", "name", "directory")
