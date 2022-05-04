from typing import Optional, Any

from .exceptions import AccessDeniedError, OwnerIDError, KeyChainIDError
from .models import User, KeyChain, Action


class BaseProtectedResource:



    __slots__ = 'user', 'owner_id', 'keychain_id'

    def __init__(
            self,
            user: Optional[User] = None,
            owner_id: Optional[Any] = None,
            keychain_id: Optional[Any] = None):

        self.user = user
        self.owner_id = owner_id
        self.keychain_id = keychain_id


def check_authorization(action: str):
    def deco(func):
        def wrapper(obj: BaseProtectedResource, *args, **kwargs):
            try:
                owner = User.objects.get(id=obj.owner_id) if obj.owner_id else None
            except User.DoesNotExist:
                raise OwnerIDError("user unknown", obj.owner_id)
            try:
                keychain = KeyChain.objects.get(id=obj.keychain_id)
            except KeyChain.DoesNotExist:
                raise KeyChainIDError("keychain unknown", obj.keychain_id)

            act = Action.objects.get(name=action, plugin__name=obj.plugin)
            is_owner = obj.user == owner

            permissions = {
                permit.allows(
                    obj.user, act, by_owner=is_owner) for permit in keychain.permissions if permit.affects_on(obj.user)
            }

            if permissions and permissions != {None}:
                if False not in permissions:
                    return func(obj, *args, **kwargs)
            else:
                if act.default_permission is True:
                    return func(obj, *args, **kwargs)

            raise AccessDeniedError('Access denied', obj.user.pk)

        return wrapper
    return deco
