import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, Group as DjangoGroup, Permission as DjangoPermission


class User(AbstractUser):
    guid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)


class Group(DjangoGroup):
    class Meta:
        proxy = True


class Permission(DjangoPermission):
    class Meta:
        proxy = True



