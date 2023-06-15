from abc import abstractmethod
from typing import Union, List, Optional, TYPE_CHECKING, Iterable, Union
from django.db.models import QuerySet
from .permissions import PermitKeychain
from core.load_plugins import import_string

if TYPE_CHECKING:  # circular import protection
    from .subjects import User
    from .permissions import Permit
    from .containers import SecurityZone


class IKeyChain:
    # must be set by a child class
    auth_covered_class_import_str = None

    @classmethod
    def get_auth_covered_class(cls):
        return import_string(cls.auth_covered_class_import_str)

    @property
    @abstractmethod
    def auth_id(self) -> str:
        """
        Return unique str for keychain
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_keychain(cls, obj_id: str) -> Optional['IKeyChain']:
        """
        Returns keychain by id or None
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_keychains(cls) -> Iterable['IKeyChain']:
        """
        Returns all keychains
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def delete_object(cls, obj_id: str):
        """
        Delete object with id
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def zone(self) -> Optional['SecurityZone']:
        """
        Returns security zone
        """
        raise NotImplementedError

    @zone.setter
    @abstractmethod
    def zone(self, zone: Optional['SecurityZone']=None):
        """
        Sets security zone
        """
        raise NotImplementedError

    @property
    def permissions(self) -> Union[QuerySet, List['Permit']]:
        return PermitKeychain.get_keychain_permits(self.auth_covered_class_import_str, str(self.id))

    def add_permission(self, permission: 'Permit'):
        """
        Add permission to keychain
        """
        return PermitKeychain.add_permit_to_keychain(self.auth_covered_class_import_str, str(self.id), permission)

    def remove_permissions(self):
        """
        Removes all permisisons
        """
        return PermitKeychain.delete_permissions(self.auth_covered_class_import_str, str(self.id))

    def add_auth_object(self, auth_obj: Union[List['IAuthCovered'], 'IAuthCovered'], replace=False):
        raise NotImplementedError

    def remove_auth_object(self, auth_obj: Union[List['IAuthCovered'], 'IAuthCovered']):
        raise NotImplementedError

    def get_auth_objects(self) -> list['IAuthCovered']:
        """
        return list of auth covered objects
        """
        pass



class IAuthCovered:

    @property
    @abstractmethod
    def auth_id(self) -> str:
        """
        Returns unique string for auth covered object
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def owner(self) -> Optional['User']:
        """
        Returns owner
        """
        raise NotImplementedError

    @owner.setter
    @abstractmethod
    def owner(self, user: 'User'):
        """
        Sets owner
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def keychain(self) -> Optional['IKeyChain']:
        """
        Returns object keychain
        """
        raise NotImplementedError

    @keychain.setter
    @abstractmethod
    def keychain(self, keychain: 'IKeyChain'):
        """
        sets keychain
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_auth_object(cls, auth_id: str) -> Optional['IAuthCovered']:
        """
        Returns object with id or None
        """
        raise NotImplementedError

