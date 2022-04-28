import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, Group as DjangoGroup, Permission as DjangoPermission

from rest_auth.models.base import BaseModel, NamedModel


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


class Role(BaseModel, NamedModel):
    permits = models.ManyToManyField('Permit', related_name='roles', blank=True)
    groups = models.ManyToManyField(Group, related_name='roles')

    def __str__(self):
        return self.name

    def contains_user(self, user: User):
        return user in self.users.all() | User.objects.filter(groups__in=self.groups.all())


