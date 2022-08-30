import logging

from abc import ABCMeta

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
    def keychain(self) -> KeyChainModel:
        try:
            if self._keychain_id:
                return self.keychain_model.objects.get(id=self._keychain_id)
        except self.keychain_model.DoesNotExist:
            log.error(f'Not found KeyChain with id = {self._keychain_id}')
        return None

    @keychain.setter
    def keychain(self, keychain: KeyChainModel):
        self._keychain_id = keychain.pk
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
    def owner(self, user: User):
        self._owner_id = user.pk
        self.save()

    class Meta:
        abstract = True
