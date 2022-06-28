from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateField(default=timezone.now, blank=True)
    updated_at = models.DateField(default=timezone.now, blank=True)
    deleted_at = models.DateField(null=True, blank=True)

    class Meta:
        abstract = True
