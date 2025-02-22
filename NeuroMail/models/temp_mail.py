from django.db import models
from django.contrib.auth.models import User

from main.models.abstract.base import BaseModel


class TempMail(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="tempmail",
    )
    email = models.EmailField(unique=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.email}"



