from django.db import models
from django.utils.translation import gettext_lazy as _


class NamedModel(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    created_time = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation date'))
    modified_time = models.DateTimeField(auto_now=True, verbose_name=_('Modification date'))

    class Meta:
        abstract = True
