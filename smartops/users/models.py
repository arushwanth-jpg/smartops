from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        AGENT = "AGENT", "Agent"
        REQUESTER = "REQUESTER", "Requester"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.REQUESTER,
    )

    team = models.ForeignKey(
        "Team",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Team(models.Model):

    name = models.CharField(max_length=100)

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name