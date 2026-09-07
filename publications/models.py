from django.conf import settings
from django.db import models


class Publication(models.Model):
    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500)
    year = models.PositiveIntegerField(null=True, blank=True)
    abstract = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="publications",
    )
    file = models.FileField(upload_to="publications/", blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
