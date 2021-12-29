from django.db import models


class Person(models.Model):
    name = models.CharField(
        'name', max_length=127,
    )
    is_active = models.BooleanField('active')
