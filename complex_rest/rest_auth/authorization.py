import logging

from typing import Any
from django.core.exceptions import ObjectDoesNotExist
from core.globals import global_vars
from rest_auth.models.abc import IKeyChain
from .exceptions import AccessDeniedError
from .models import User, Action, Role, Permit, Plugin
from .models.abc import IAuthCovered


log = logging.getLogger('root')


def has_perm(user: User, action: Action, obj: IAuthCovered) -> bool:
    """
    Returns True if user has right to do action on object with specified keychain, otherwise return False
    """
    is_owner = user == obj.owner if obj.owner else None

    if obj.keychain:
        key_chain_permits = obj.keychain.permissions

        # union with security zone permissions
        return key_chain_permits.permits.all().union(
            obj.keychain.zone.effective_permissions if obj.keychain.zone else Permit.objects.none()
        )

    else:
        permits = Permit.objects.filter(
            actions=action,
            roles__in=Role.objects.filter(groups__in=user.groups.all())
        )

    permissions = (
        {
            permit.allows(user, action, by_owner=is_owner)
            for permit in permits if permit.affects_on(user)
        }
    )
    if permissions and permissions != {None}:
        if False not in permissions:
            return True
    else:
        return action.default_rule


def check_authorization(obj: IAuthCovered, action_name: str):
    """
    Checks if action can be done with object
    If not allowed raises AccessDeniedError
    """
    user = global_vars.get_current_user()
    plugin_name = _plugin_name(obj)

    try:

        plugin = Plugin.objects.get(name=plugin_name)
        action = Action.objects.get(plugin=plugin, name=action_name)

    except ObjectDoesNotExist as err:
        log.error(f'Error occurred while authorization: {err}')
        raise AccessDeniedError(f'Error occurred while authorization: {err}')

    if not has_perm(user, action, obj):
        raise AccessDeniedError(
            f'Access denied. Action {action_name} on object {str(obj)} for user {user.username} is not allowed'
        )


def _plugin_name(obj):
    """
    Returns plugin name for object
    """
    return obj.__module__.split('.')[0]


def auth_covered_method(action_name: str):
    def decorator(class_method):
        """
        Decorator returns method that do the same but checks authorization
        """
        def wrapper(*args, **kwargs):
            # args[0] = self
            check_authorization(args[0], action_name)
            return class_method(*args, **kwargs)
        return wrapper
    return decorator


def auth_covered_func(action_name: str):
    def decorator(func):
        """
        Decorator return function that do the same but checks authorization
        """

        def wrapper(*args, **kwargs):
            func.owner = None
            func.keychain = None
            check_authorization(func, action_name)
            return func(*args, **kwargs)

        return wrapper
    return decorator
