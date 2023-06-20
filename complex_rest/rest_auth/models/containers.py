import logging

from typing import Iterable, Optional, Union, List
from django.db import models
from django.core.validators import int_list_validator
from mptt.models import MPTTModel, TreeForeignKey
from mixins.models import NamedModel, TimeStampedModel
from rest_auth.authentication import User

from .permissions import Permit, Action
from .abc import IKeyChain, IAuthCovered


log = logging.getLogger('root.rest_auth')


class SecurityZone(NamedModel, TimeStampedModel, MPTTModel):
    parent = TreeForeignKey('self', on_delete=models.CASCADE, related_name='zones', null=True, blank=True)
    permits = models.ManyToManyField(Permit, related_name='zones', blank=True)

    @property
    def effective_permissions(self):
        return self.permits.all().union(self.parent.effective_permissions if self.parent else Permit.objects.none())


class KeyChainModel(IKeyChain, TimeStampedModel):
    _name = models.CharField(max_length=255, unique=True, null=True, blank=True)
    _zone = models.IntegerField(null=True, blank=True)
    _auth_objects = models.TextField(default='')  # ',' split ids string

    def __init__(self, *args, **kwargs):
        super(TimeStampedModel, self).__init__(*args, **kwargs)
        if self._state.adding:
            self.save()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.save()

    @property
    def auth_id(self) -> str:
        return self.id

    @classmethod
    def get_keychain(cls, obj_id: str) -> Optional['IKeyChain']:
        return cls.objects.get(id=int(obj_id))

    @classmethod
    def get_keychains(cls) -> Iterable['IKeyChain']:
        return cls.objects.all()

    @classmethod
    def delete_object(cls, keychain_id: str):
        keychain: 'KeyChainModel' = cls.objects.get(id=int(keychain_id))
        # todo remove keychains
        for obj in keychain.get_auth_objects():
            obj.keychain = None
        keychain.delete()

    def add_auth_object(self, auth_obj: Union[List['IAuthCovered'], 'IAuthCovered'], replace=False):
        if replace:
            for obj in self.get_auth_objects():
                obj.keychain = None
            self._auth_objects = ''
        if isinstance(auth_obj, list):
            for obj in auth_obj:
                obj.keychain = self
            update_set = set(
                map(
                    lambda x: x.auth_id,
                    auth_obj
                )
            )
        else:
            auth_obj.keychain = self
            update_set = {auth_obj.auth_id}

        s = set(self._auth_objects.split(',')) if self._auth_objects else set()
        s.update(update_set)
        self._auth_objects = ','.join(s)
        self.save()

    def remove_auth_object(self, auth_obj: Union[List['IAuthCovered'], 'IAuthCovered']):
        if isinstance(auth_obj, list):
            for obj in auth_obj:
                obj.keychain = None
            update_set = set(
                map(
                    lambda x: x.auth_id,
                    auth_obj
                )
            )
        else:
            auth_obj.keychain = None
            update_set = {auth_obj.auth_id}

        s = set(self._auth_objects.split(',')) if self._auth_objects else set()
        s.difference_update(update_set)
        self._auth_objects = ','.join(s)
        self.save()

    def get_auth_objects(self) -> list['IAuthCovered']:
        return list(
            map(
                lambda auth_obj_id: self.get_auth_covered_class().get_auth_object(auth_obj_id),
                self._auth_objects.split(',') if self._auth_objects else set()
            )
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
        if zone:
            self._zone = zone.pk
        else:
            self._zone = None
        self.save()

    def __str__(self):
        return f'{self.id}'

    class Meta:
        abstract = True
