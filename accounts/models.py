from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    GUEST = "guest", "Guest"
    VUB_NETWORK = "vub_network", "VUB-Network User"
    MEMBER = "member", "Member"
    PUBLISHER = "publisher", "Publisher"
    MODERATOR = "moderator", "Moderator"
    ADMINISTRATOR = "administrator", "Administrator"


class User(AbstractUser):
    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.GUEST,
    )
    university = models.CharField(max_length=255, blank=True)
    department = models.ForeignKey(
        "orgs.DepartmentGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
    )
    is_confirmed = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)


class ConfirmationToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="confirmation_tokens",
    )
    token = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"Token for {self.user}"
