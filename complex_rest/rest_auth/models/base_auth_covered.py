import logging

from abc import ABCMeta

from django.db import models
from rest_auth.authentication import User
from mixins.models import NamedModel, TimeStampedModel

from .containers import KeyChainModel
from .abc import IAuthCovered


log = logging.getLogger('root.rest_auth')


class BaseAuthCoveredModel(IAuthCovered, NamedModel, TimeStampedModel):
    object_id = models.CharField(max_length=256, blank=True, null=False, unique=True)
    _owner_id = models.PositiveIntegerField()
    _keychain_id = models.PositiveIntegerField()

    @property
    def keychain(self) -> KeyChainModel:
        try:
            return KeyChainModel.objects.get(id=self._keychain_id)
        except KeyChainModel.DoesNotExist:
            log.error(f'Not found KeyChain with id = {self._keychain_id}')
            return None

    @property
    def owner(self) -> User:
        try:
            return User.objects.get(id=self._owner_id)
        except User.DoesNotExist:
            log.error(f'Not found owner with id = {self._owner_id}')
            return None

    class Meta:
        abstract = True
