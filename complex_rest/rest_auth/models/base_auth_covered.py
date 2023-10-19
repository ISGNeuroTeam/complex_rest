import logging
import uuid

from typing import Optional, List

from django.db import models
from .permissions import AuthCoveredClass as AuthCoveredClassModel
from rest_auth.authentication import User
from mixins.models import NamedModel, TimeStampedModel

from .containers import KeyChainModel
from .abc import IAuthCovered


log = logging.getLogger('root.rest_auth')


class AuthCoveredModel(IAuthCovered, NamedModel, TimeStampedModel):
    _owner_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, null=True)

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
                return User.get_user(self._owner_id)
        except User.DoesNotExist:
            log.error(f'Not found owner with id = {self._owner_id}')
        return None

    @owner.setter
    def owner(self, user: Optional[User]):
        if user:
            self._owner_id = user.guid
        else:
            self._owner_id = None
        super(TimeStampedModel, self).save()

    @classmethod
    def get_auth_object(cls, obj_id: str) -> 'IAuthCovered':
        return cls.objects.get(pk=int(obj_id))


    def get_actions_for_auth_obj(self) -> List[str]:
        """
        Returns list of action names for auth instance
        """
        # find class that inherits IAuthCovered
        auth_cls = type(self)
        auth_covered_class_mro_index = auth_cls.__mro__.index(IAuthCovered) - 1
        auth_covered_class_instance = None

        for i in range(auth_covered_class_mro_index, -1, -1):
            auth_covered_class = auth_cls.__mro__[i]
            cls_import_str = f'{auth_covered_class.__module__}.{auth_covered_class.__name__}'
            try:
                auth_covered_class_instance = AuthCoveredClassModel.objects.get(class_import_str=cls_import_str)
            except AuthCoveredClassModel.DoesNotExist:
                continue
            break

        if auth_covered_class_instance is None:
            raise ValueError(f'Auth covered class for object {self.auth_name} is not found')

        return list(auth_covered_class_instance.actions.all().values_list('name', flat=True))

    class Meta:
        abstract = True

