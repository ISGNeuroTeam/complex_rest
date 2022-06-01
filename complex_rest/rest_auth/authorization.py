from typing import Optional, Any, Callable
from core.settings.base import PLUGINS_DIR
from .exceptions import OwnerIDError, KeyChainIDError, ActionError, AccessDeniedError
from .models import User, KeyChain, Action, Role, Permit


class BaseProtectedResource:

    __slots__ = 'user', 'owner_id', 'keychain_id'

    plugin = None  # Some magic requested!

    def __init__(
            self,
            user: Optional[User] = None,
            owner_id: Optional[Any] = None,
            keychain_id: Optional[Any] = None):

        self.user = user
        self.owner_id = owner_id
        self.keychain_id = keychain_id

    @staticmethod
    def get_plugin_name(view_filepath: str):
        plugin = view_filepath[view_filepath.find(PLUGINS_DIR) + len(PLUGINS_DIR) + 1:]
        return plugin[:plugin.find('/')]


def check_authorization(action: str, when_denied: Optional[Any] = None, on_error: Optional[Callable] = None):
    def deco(func):
        def wrapper(obj: BaseProtectedResource, *args, **kwargs):
            try:
                owner = User.objects.get(id=obj.owner_id) if obj.owner_id else None
            except User.DoesNotExist:
                if on_error:
                    return on_error(f"Owner with ID {obj.owner_id} unknown")
                raise OwnerIDError("Owner unknown", obj.owner_id)

            try:
                act = Action.objects.get(name=action, plugin__name=obj.plugin)
            except Action.DoesNotExist:
                if on_error:
                    return on_error(f"Action with name {action} unknown")
                raise ActionError("Action unknown", action)

            is_owner = obj.user == owner if owner else None

            if obj.keychain_id:
                try:
                    permits = KeyChain.objects.get(id=obj.keychain_id).permissions
                except KeyChain.DoesNotExist:
                    if on_error:
                        return on_error(f"Keychain with ID {obj.owner_id} unknown")
                    raise KeyChainIDError("keychain unknown", obj.keychain_id)
            else:
                permits = Permit.objects.filter(
                    actions=act,
                    roles__in=Role.objects.filter(groups__in=obj.user.groups.all())
                )

            permissions = (
                {
                    permit.allows(
                        obj.user, act, by_owner=is_owner) for permit in permits if permit.affects_on(obj.user)
                }
            )

            if permissions and permissions != {None}:
                if False not in permissions:
                    return func(obj, *args, **kwargs)
            else:
                if act.default_permission is True:
                    return func(obj, *args, **kwargs)

            if when_denied:
                return when_denied

            raise AccessDeniedError('Access denied', obj.user.pk)

        return wrapper
    return deco
