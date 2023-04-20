import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, Group as DjangoGroup, Permission as DjangoPermission
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

    def save(self, *args, **kwargs):
        if self.email == '':
            self.email = None
        super().save()


class Permission(DjangoPermission):
    class Meta:
        proxy = True


class Role(TimeStampedModel, NamedModel):
    permits = models.ManyToManyField('Permit', related_name='roles', blank=True)
    groups = models.ManyToManyField(Group, related_name='roles', blank=True)

    def __str__(self):
        return self.name

    def contains_user(self, user: User):
        return user in self.all_users

    @property
    def all_users(self):
        return User.objects.filter(groups__in=self.groups.all())
