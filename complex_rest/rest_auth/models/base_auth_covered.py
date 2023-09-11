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

    @property
    def auth_id(self) -> str:
        return str(self.id)

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
        super(TimeStampedModel, self).save()

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
        super(TimeStampedModel, self).save()

    @classmethod
    def get_auth_object(cls, obj_id: str) -> 'IAuthCovered':
        return cls.objects.get(pk=int(obj_id))

    class Meta:
        abstract = True

