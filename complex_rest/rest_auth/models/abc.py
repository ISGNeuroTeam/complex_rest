import typing
from abc import abstractmethod
from typing import Union, List
from django.db.models import QuerySet


if typing.TYPE_CHECKING:  # circular import protection
    from .subjects import User
    from .permissions import Permit, Action
    from .containers import SecurityZone


class IKeyChain:
    @property
    @abstractmethod
    def keychain_id(self) -> str:
        """
        Returns any unique identifier
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def zone(self) -> 'SecurityZone':
        """
        Returns security zone
        """
        pass

    @property
    @abstractmethod
    def permissions(self) -> Union[QuerySet, List['Permit']]:
        """
        Returns permissions
        """
        raise NotImplementedError

    @abstractmethod
    def allows(self, user: 'User', act: 'Action', by_owner: bool = None) -> bool:
        raise NotImplementedError


class IAuthCovered:
    @property
    @abstractmethod
    def object_id(self) -> str:
        """
        Returns any unique identifier
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def owner(self) -> 'User':
        """
        Returns owner
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def keychain(self) -> 'IKeyChain':
        """
        Returns object keychain
        """
        raise NotImplementedError
