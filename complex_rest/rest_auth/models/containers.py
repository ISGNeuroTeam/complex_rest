import logging

from django.db import models
from django.core.validators import int_list_validator
from mptt.models import MPTTModel, TreeForeignKey
from mixins.models import NamedModel, TimeStampedModel
from rest_auth.authentication import User

from .permissions import Permit, Action
from .abc import IKeyChain


log = logging.getLogger('root.rest_auth')


class SecurityZone(NamedModel, TimeStampedModel, MPTTModel):
    parent = TreeForeignKey('self', on_delete=models.CASCADE, related_name='zones', null=True, blank=True)
    permits = models.ManyToManyField(Permit, related_name='zones', blank=True)

    @property
    def effective_permissions(self):
        return self.permits.all().union(self.parent.effective_permissions if self.parent else Permit.objects.none())


class KeyChainModel(IKeyChain, TimeStampedModel):
    _zone = models.IntegerField(null=True, blank=True)
    _permits = models.CharField(
        max_length=1024, validators=[int_list_validator(sep=','), ]
    )

    @property
    def zone(self) -> SecurityZone:
        if self._zone:
            try:
                return SecurityZone.objects.get(id=self._zone) if self._zone else None
            except SecurityZone.DoesNotExist:
                log.error(f'Not found security zone with id {self._zone}')

        return None

    @zone.setter
    def zone(self, zone: SecurityZone):
        self._zone = zone
        self.save()

    @property
    def permissions(self):
        return Permit.objects.filter(id__in=self._permits.split(','))

    def add_permission(self, permission: 'Permit'):
        permit_ids = set(self._permits.split(','))
        permit_ids.add(permission.pk)
        self._permits = ','.join(permit_ids)
        self.save()

    def remove_permission(self, permission: 'Permit'):
        permit_ids = set(self._permits.split(','))
        permit_ids.remove(permission.pk)
        self._permits = ','.join(permit_ids)
        self.save()

    def __str__(self):
        return f'{self.keychain_id}'

    class Meta:
        abstract = True
