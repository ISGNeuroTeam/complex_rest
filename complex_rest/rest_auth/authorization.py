from typing import Optional, Any

from .exceptions import AccessDeniedError
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
            owner = User.objects.get(id=obj.owner_id)
            keychain = KeyChain.objects.get(id=obj.keychain_id)
            act = Action.objects.get(name=action, plugin__name=obj.plugin)
            is_owner = obj.user == owner

            permissions = [
                permit.allows(
                    obj.user, act, by_owner=is_owner) for permit in keychain.permissions if permit.affects_on(obj.user)
            ]

            if permissions:
                if all(permissions):
                    return func(obj, *args, **kwargs)
            else:
                if act.default_permission is True:
                    return func(obj, *args, **kwargs)

            raise AccessDeniedError('Access denied', obj.user.guid)

        return wrapper
    return deco
