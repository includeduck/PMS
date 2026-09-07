from django.db import models


class DepartmentGroup(models.Model):
    """PMS group/department (UC-07). Distinct from django.contrib.auth.Group."""

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
