import logging

from typing import Optional, List

from django.db import models
from rest_auth.authentication import User
from mixins.models import NamedModel, TimeStampedModel

from .containers import KeyChainModel
from .abc import IAuthCovered


log = logging.getLogger('root.rest_auth')


class AuthCoveredModel(IAuthCovered, NamedModel, TimeStampedModel):
    _owner_id = models.PositiveIntegerField(blank=True, null=True)
    _keychain_id = models.PositiveIntegerField(blank=True, null=True)

    # must be set by child class
    keychain_model = None

    def __init__(self, *args, **kwargs):
        super(TimeStampedModel, self).__init__(*args, **kwargs)
        if self._state.adding:
            self.save()

    @property
    def keychain(self) -> KeyChainModel:
        try:
            if self._keychain_id:
                keychain = self.keychain_model.objects.get(id=self._keychain_id)
                return keychain
        except self.keychain_model.DoesNotExist:
            log.error(f'Not found KeyChain with id = {self._keychain_id}')
        return None

    @keychain.setter
    def keychain(self, keychain: KeyChainModel):
        if keychain:
            self._keychain_id = keychain.id
        else:
            self._keychain_id = None
        self.save()

    @property
    def owner(self) -> User:
        try:
            if self._owner_id:
                return User.objects.get(id=self._owner_id)
        except User.DoesNotExist:
            log.error(f'Not found owner with id = {self._owner_id}')
        return None

    @owner.setter
    def owner(self, user: Optional[User]):
        if user:
            self._owner_id = user.id
        else:
            self._owner_id = None
        self.save()

    @classmethod
    def get_objects(cls, keychain: bool = None) -> List['AuthCoveredModel']:
        all_objects = cls.objects.all()
        if keychain is None:
            return list(all_objects)
        if keychain:
            return list(
                all_objects.filter(_keychain_id__isnull=False)
            )
        else:
            return list(
                all_objects.filter(_keychain_id__isnull=True)
            )

    @classmethod
    def get_object(cls, obj_id: str) -> 'IAuthCovered':
        return cls.objects.get(pk=int(obj_id))

    class Meta:
        abstract = True

