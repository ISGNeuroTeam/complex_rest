from abc import abstractmethod
from typing import Union, List, Optional, TYPE_CHECKING
from django.db.models import QuerySet


if TYPE_CHECKING:  # circular import protection
    from .subjects import User
    from .permissions import Permit
    from .containers import SecurityZone


class IKeyChain:
    @property
    @abstractmethod
    def zone(self) -> Optional['SecurityZone']:
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


class IAuthCovered:
    @property
    @abstractmethod
    def owner(self) -> Optional['User']:
        """
        Returns owner
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def keychain(self) -> Optional['IKeyChain']:
        """
        Returns object keychain
        """
        raise NotImplementedError
