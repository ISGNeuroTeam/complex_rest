import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, Group as DjangoGroup, Permission as DjangoPermission


class User(AbstractUser):
    guid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    email = models.EmailField('email address', unique=True, blank=True, null=True, default=None)
    phone = models.CharField('phone', unique=True, max_length=150, blank=True, null=True)
    photo = models.TextField('photo', max_length=12000000, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.email == '':
            self.email = None
        super().save()


class Group(DjangoGroup):
    class Meta:
        proxy = True


class Permission(DjangoPermission):
    class Meta:
        proxy = True



