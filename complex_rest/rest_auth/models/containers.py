import logging

from typing import Iterable, Optional
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

    def __init__(self, *args, **kwargs):
        super(TimeStampedModel, self).__init__(*args, **kwargs)
        super(TimeStampedModel, self).save()

    _zone = models.IntegerField(null=True, blank=True)

    @classmethod
    def get_object(cls, obj_id: str) -> Optional['IKeyChain']:
        return cls.objects.get(id=int(obj_id))

    @classmethod
    def get_objects(cls) -> Iterable['IKeyChain']:
        return cls.objects.all()

    @classmethod
    def delete_object(cls, obj_id: str):
        cls.objects.filter(id=int(obj_id)).delete()

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
        if zone:
            self._zone = zone.pk
        else:
            self._zone = None
        self.save()

    def __str__(self):
        return f'{self.id}'

    class Meta:
        abstract = True
