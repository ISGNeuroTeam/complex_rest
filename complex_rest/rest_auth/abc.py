from abc import ABC, abstractmethod
from typing import Union, List, Any
from django.db.models import QuerySet
from rest_auth.authentication import User


from rest_auth.models import Permit, SecurityZone, Action


class IKeyChain(ABC):
    @property
    @abstractmethod
    def keychain_id(self) -> str:
        """
        Returns any unique identifier
        """
        pass

    @property
    @abstractmethod
    def zone(self) -> SecurityZone:
        """
        Returns security zone
        """
        pass

    @property
    @abstractmethod
    def permissions(self) -> Union[QuerySet, List[Permit]]:
        """
        Returns permissions
        """
        pass

    @property
    @abstractmethod
    def objects(self):
        """
        Returns object manager (same interface as django managers)
        """
        pass

    @abstractmethod
    def allows(self, user: User, act: Action, by_owner: bool = None) -> bool:
        pass


class IAuthCovered(ABC):
    @property
    @abstractmethod
    def object_id(self) -> str:
        """
        Returns any unique identifier
        """

    @property
    @abstractmethod
    def owner(self) -> User:
        """
        Returns owner
        """
        pass

    @property
    @abstractmethod
    def keychain(self) -> IKeyChain:
        """
        Returns object keychain
        """
        pass
