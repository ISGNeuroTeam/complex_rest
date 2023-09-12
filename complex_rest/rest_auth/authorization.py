import logging

from typing import Any, List

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from core.globals import global_vars
from rest_auth.models.abc import IKeyChain
from rest_auth.keycloak_client import KeycloakClient, KeycloakError
from .exceptions import AccessDeniedError
from .models import User, Action, Role, Permit, Plugin, AccessRule
from .models.abc import IAuthCovered


log = logging.getLogger('root')


def _get_permissions_for_user_and_action(user: User, action: Action):
    return Permit.objects.filter(
        actions=action,
        roles__in=Role.objects.filter(groups__in=user.groups.all())
    )


def _get_keychain_permissions(keychain: IKeyChain):
    key_chain_permits = keychain.permissions
    # union with security zone permissions
    if keychain.zone:
        return list(key_chain_permits) + list(keychain.zone.effective_permissions)
    else:
        return list(key_chain_permits)


def _user_allowed_to_do_action(permits, action, user):
    """
    Returns true if user allowed to do action
    """
    # filter if they affects on user
    permits = map(
        lambda permit: permit.affects_on(user),
        permits
    )

    rules = AccessRule.objects.filter(action=action, permit__in=permits)

    # if deny rule exist action not allowed
    if rules.filter(rule=False):
        return False

    # if allow rule exist or default rule is allow then action allowed
    if rules.filter(rule=True) or action.default_rule:
        return True


def has_perm(user: User, action: Action, obj: IAuthCovered) -> bool:
    """
    Returns True if user has right to do action on object with specified keychain, otherwise return False
    """
    is_owner = user == obj.owner if obj.owner else None

    if obj.keychain:
        permits = _get_keychain_permissions(obj.keychain)
    else:
        permits = _get_permissions_for_user_and_action(user, action)

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


def has_perm_on_keycloak(auth_header, action_name: str, object_auth_id: str) -> bool:
    """
    Sends request to keycloak
    Returns True if user has right to do action on object
    Raises AccessDeniedError if some error occurred with keycloak
    """
    keycloak_client = KeycloakClient()
    try:
        return keycloak_client.authorization_request(auth_header, action_name, object_auth_id)
    except KeycloakError as err:
        log.error(f'Error with keycloak: {str(err)}')
        raise AccessDeniedError(f'Error with keycloak {str(err)}')


def get_allowed_object_ids_list(user: User, action: Action, obj_class):
    """
    Return list of objects id allowed for User to do action
    """
    objects_with_keychain = obj_class.get_keychains(keychain=True)
    keychain_ids = set()
    allowed_objects_ids = set()
    for obj in objects_with_keychain:
        keychain = obj.keychain
        if [keychain.id] in keychain_ids:
            allowed_objects_ids.add(obj.id)
            continue
        permits: List[Permit] = _get_keychain_permissions(keychain)

        if not _user_allowed_to_do_action(permits, action, user):
            continue
        else:
            allowed_objects_ids.add(obj.id)
            keychain_ids.add(keychain.id)

    objects_without_keychain = obj_class.get_keychains(keychain=False)
    objects_without_keychain_ids = map(
        lambda x: x.id, objects_without_keychain
    )
    permits = _get_permissions_for_user_and_action(user, action)
    if _user_allowed_to_do_action(permits, action, user):
        allowed_objects_ids.union(set(objects_without_keychain_ids))

    # todo exclude objects which not allowed with access rules for owner
    return list(allowed_objects_ids)


def check_authorization(obj: IAuthCovered, action_name: str):
    """
    Checks if action can be done with object
    If not allowed raises AccessDeniedError
    """
    if settings.KEYCLOAK_SETTINGS['authorization']:
        return has_perm_on_keycloak(global_vars['auth_header'], action_name, obj.auth_id)
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
            if 'ignore_authorization' in kwargs:
                ignore_authorization = kwargs['ignore_authorization']
                del kwargs['ignore_authorization']
            else:
                ignore_authorization = False
            if not ignore_authorization:
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
