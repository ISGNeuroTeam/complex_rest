from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    created_time = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation date'))
    modified_time = models.DateTimeField(auto_now=True, verbose_name=_('Modification date'))

    def __str__(self):
        return 'TimeStampedModel'

    class Meta:
        abstract = True
