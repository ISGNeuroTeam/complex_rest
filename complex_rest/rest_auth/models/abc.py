from abc import abstractmethod
from typing import Union, List, Optional, TYPE_CHECKING, Iterable
from django.db.models import QuerySet


if TYPE_CHECKING:  # circular import protection
    from .subjects import User
    from .permissions import Permit
    from .containers import SecurityZone


class IKeyChain:
    @classmethod
    @abstractmethod
    def get_object(cls, obj_id) -> Optional['IKeyChain']:
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
    def delete_object(cls, obj_id):
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
    @abstractmethod
    def permissions(self) -> Union[QuerySet, List['Permit']]:
        """
        Returns permissions
        """
        raise NotImplementedError

    @abstractmethod
    def add_permission(self, permission: 'Permit'):
        """
        Add permission to keychain
        """
        raise NotImplementedError

    @abstractmethod
    def remove_permission(self, permission: 'Permit'):
        """
        Removes permission
        """
        raise NotImplementedError

    def remove_permissions(self):
        """
        Removes all permisisons
        """
        raise NotImplementedError

    # @abstractmethod
    # def get_auth_covered_objects(self) -> Iterable['IAuthCovered']:
    #     """
    #     Returns all auth covered objects in keychain
    #     """
    #     raise NotImplementedError


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
    def get_object(cls, obj_id) -> Optional['IAuthCovered']:
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
