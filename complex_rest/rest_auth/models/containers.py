import logging


from django.db import models
from django.core.validators import int_list_validator
from mptt.models import MPTTModel, TreeForeignKey
from mixins.models import NamedModel, TimeStampedModel
from rest_auth.authentication import User
from rest_auth.models import Permit, Action
from rest_auth.abc import IAuthCovered, IKeyChain


log = logging.getLogger('root.rest_auth')


class SecurityZone(NamedModel, TimeStampedModel, MPTTModel):
    parent = TreeForeignKey('self', on_delete=models.CASCADE, related_name='zones', null=True, blank=True)
    permits = models.ManyToManyField(Permit, related_name='zones', blank=True)

    @property
    def effective_permissions(self):
        return self.permits.all().union(self.parent.effective_permissions if self.parent else Permit.objects.none())


class KeyChainModel(IKeyChain, TimeStampedModel):
    keychain_id = models.CharField('keychain_id', unique=True, max_length=255)
    _zone = models.IntegerField(null=True, blank=True)
    _permits = models.CharField(validators=int_list_validator(sep=','))

    @property
    def zone(self) -> SecurityZone:
        try:
            return SecurityZone.objects.get(id=self._zone) if self._zone else None
        except SecurityZone.DoesNotExist:
            log.error(f'Not found securit zone with id {self._zone}')

    @property
    def permissions(self):
        return Permit.objects.filter(id__in=self._permits.split(','))

    def __str__(self):
        return f'{self.keychain_id}'

    class Meta:
        unique_together = ('plugin', 'keychain_id',)

    @property
    def permissions(self):
        return self.permits.all().union(self.zone.effective_permissions if self.zone else Permit.objects.none())

    def allows(self, user: User, act: Action, by_owner: bool = None):
        return any([
            permit.allows(user, act, by_owner) for permit in self.permissions
        ])
