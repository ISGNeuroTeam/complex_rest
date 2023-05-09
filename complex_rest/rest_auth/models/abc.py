from abc import abstractmethod
from typing import Union, List, Optional, TYPE_CHECKING, Iterable
from django.db.models import QuerySet
from .permissions import PermitKeychain


if TYPE_CHECKING:  # circular import protection
    from .subjects import User
    from .permissions import Permit
    from .containers import SecurityZone


class IKeyChain:
    # must be set by a child class
    auth_covered_class_import_str = None

    @classmethod
    @abstractmethod
    def get_object(cls, obj_id: str) -> Optional['IKeyChain']:
        """
        Returns keychain by id or None
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_objects(cls) -> Iterable['IKeyChain']:
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


class IAuthCovered:
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
    def get_object(cls, obj_id: str) -> Optional['IAuthCovered']:
        """
        Returns object with id or None
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_objects(cls, keychain: Optional[bool] = None) -> Iterable['IAuthCovered']:
        """
        Returns list of objects.
        keychain is True returns only objects with keychain.
        keychain is False returns only objects without keychain
        keychain is None returns all objects
        """
        raise NotImplementedError
