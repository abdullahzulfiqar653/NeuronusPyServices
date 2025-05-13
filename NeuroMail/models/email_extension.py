from django.db import models

from main.models.abstract.base import BaseModel


class EmailExtension(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"
