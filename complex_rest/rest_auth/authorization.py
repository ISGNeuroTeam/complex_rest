import logging

from typing import Any
from django.core.exceptions import ObjectDoesNotExist
from rest.globals import global_vars
from .exceptions import AccessDeniedError
from .models import User, KeyChain, Action, Role, Permit, Plugin


log = logging.getLogger('root')


def has_perm(user: User, action: Action, keychain: KeyChain = None, object_owner: User=None) -> bool:
    """
    Returns True if user has right to do action on object with specified keychain, otherwise return False
    """
    is_owner = user == object_owner if object_owner else None

    if keychain:
        permits = keychain.permissions
    else:
        permits = Permit.objects.filter(
            actions=action,
            roles_in=Role.objects.filter(groups__in=user.groups.all())
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


def check_authorisation(obj: Any, action_name: str):
    """
    Checks if action can be done with object
    If not allowed raises AccessDeniedError
    """
    user = global_vars.get_current_user()
    plugin_name = obj.__class__.__module__.split('.')[0]

    try:
        plugin = Plugin.objects.get(name=plugin_name)
        action = Action.objects.get(plugin=plugin, name=action_name)

        if hasattr(obj, 'owner_guid'):
            obj_owner = User.objects.get(guid=obj.owner_guid)
        else:
            obj_owner = None

        if hasattr(obj, 'keychain_id'):
            key_chain = KeyChain.objects.get(id=obj.keychain_id)
        else:
            key_chain = None

    except ObjectDoesNotExist as err:
        log.error(f'Error occurred while authorization: {err}')
        raise AccessDeniedError(f'Error occurred while authorization: {err}')

    if not has_perm(user, action, key_chain, obj_owner):
        raise AccessDeniedError(
            f'Access denied. Action {action_name} on object {str(obj)} for user {user.username} is not allowed'
        )


def _generate_default_keychain_id(class_obj):
    return f'{class_obj.__module__}.{class_obj.__name__}'


def _transform_auth_covered_obj(class_obj, default_keychain_id=None):
    """
    Makes class transform. Adds attribute 'default_keychain_id'.
    """
    if default_keychain_id is None:
        default_keychain_id = _generate_default_keychain_id(class_obj)
    setattr(class_obj, 'default_keychain_id', default_keychain_id)
    return class_obj


def auth_covered_object(obj: Any):
    # obj - either a class object when decorator called without parentheses or default_keychain_id
    if isinstance(obj, str):
        default_keychain_id = obj

        def decorator(class_obj):
            _transform_auth_covered_obj(class_obj, default_keychain_id)
            return class_obj

        return decorator
    else:  # decorator called without parentheses
        return _transform_auth_covered_obj(obj)


def auth_covered_method(action_name: str):
    def decorator(class_method):
        def wrapper(*args, **kwargs):
            has_perm(args[0], action_name)
            return class_method(*args, **kwargs)
        return wrapper
    return decorator

