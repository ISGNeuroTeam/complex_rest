import uuid

from typing import Set
from django.db import models
from django.contrib.auth.models import AbstractUser, Group as DjangoGroup,\
    Permission as DjangoPermission, AnonymousUser as DjangoAnonymousUser
from django.utils.translation import gettext_lazy as _
from mixins.models import TimeStampedModel, NamedModel


class Group(DjangoGroup):
    class Meta:
        proxy = True


class User(AbstractUser):
    guid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    email = models.EmailField('email address', unique=True, blank=True, null=True, default=None)
    phone = models.CharField('phone', unique=True, max_length=150, blank=True, null=True)
    photo = models.TextField('photo', max_length=12000000, blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="user_set",
        related_query_name="user",
    )

    def roles(self) -> Set['Roles']:
        roles_set = set()
        for group in self.groups.all():
            roles_set.update(set(group.roles.all()))
        return roles_set

    def save(self, *args, **kwargs):
        if self.email == '':
            self.email = None
        super().save()


class KeycloakUser(User):
    def __init__(self, user_info: dict, *args, **kwargs):
        """
        Args:
            user_info (dict): user info from token
        """
        super().__init__(*args, **kwargs)
        self._user_info = user_info

        self.username = user_info['preferred_username']
        self.first_name = user_info['given_name']
        self.last_name = user_info['family_name']
        self.email = user_info['email']
        self.guid = uuid.UUID(user_info['sub'])

    def roles(self) -> Set['Role']:
        """
        Returns Roles set
        """
        roles = set()
        for role_name in self._user_info['realm_access']['roles']:
            role, created = Role.objects.get_or_create(name=role_name)
            roles.add(role)
        return roles

    class Meta:
        proxy = True

class AnonymousUser(DjangoAnonymousUser):
    guid = uuid.UUID('00000000-0000-0000-0000-000000000000')
    email = ''
    phone = ''
    photo = ''


class Permission(DjangoPermission):
    class Meta:
        proxy = True


class Role(TimeStampedModel, NamedModel):
    name = models.CharField(max_length=255, unique=True)
    permits = models.ManyToManyField('Permit', related_name='roles', blank=True)
    groups = models.ManyToManyField(Group, related_name='roles', blank=True)

    def __str__(self):
        return self.name

    def contains_user(self, user: User):
        return user in self.all_users

    @property
    def all_users(self):
        return User.objects.filter(groups__in=self.groups.all())
