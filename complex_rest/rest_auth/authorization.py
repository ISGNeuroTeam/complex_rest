import logging
import uuid
import hashlib

from typing import Any, List, Callable

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from core.globals import global_vars
from rest_auth.models.abc import IKeyChain
from rest_auth.keycloak_client import KeycloakClient, KeycloakError, KeycloakResources
from .exceptions import AccessDeniedError
from .models import User, Action, Role, Permit, Plugin, AccessRule, AuthCoveredClass
from .models.abc import IAuthCovered


log = logging.getLogger('main')


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


def has_perm(user: User, action: Action, obj: IAuthCovered = None) -> bool:
    """
    Returns True if user has right to do action on object with specified keychain, otherwise return False
    """
    log.debug(f'Check permissions for user: {user.username}, action: {action.name}, object: {obj.auth_name}')
    if global_vars['disable_authorization']:
        return True

    if settings.KEYCLOAK_SETTINGS['authorization']:
        return has_perm_on_keycloak(
            global_vars['auth_header'], action.name,
            _get_unique_resource_name_for_keycloak(obj) if obj else '',
            f'{_get_resource_type_for_keycloak(obj)}:default_resource',
        )

    is_owner = user == obj.owner if obj.owner else None

    if obj is not None and obj.keychain:
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


def has_perm_on_keycloak(auth_header, action_name: str, object_auth_id: str, default_resource_name=None) -> bool:
    """
    Sends request to keycloak
    Returns True if user has right to do action on object
    Raises AccessDeniedError if some error occurred with keycloak
    """
    keycloak_client = KeycloakClient()
    try:
        return keycloak_client.authorization_request(
            auth_header, action_name, object_auth_id if object_auth_id else '',
            default_resource_name=default_resource_name
        )
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


def authz_integration(
        authz_action: str, id_attr: str = None,
        type_name_func: Callable = None, unique_name_func: Callable = None
):
    """
    Decorator for Create, update, delete records in keycloak.
    Args:
        authz_action (str): action in authorization model which requires integration
            - create
            - update
            - delete
        id_attr (str): attribute name for id in keycloak, default is 'auth_id'. If id_attr is UUID instance then it used. Else md5 hash of type and id_attr is used.
        type_name_func (Callable): function to generate type for object
            Default function is f'{_plugin_name(instance)}.{type(instance).__name__}'
        unique_name_func (Callable): function to generate unique name for object.
            Default function is  f'{instance_type}.{instance.auth_name}
    """
    if not id_attr:
        id_attr = 'auth_id'

    if not unique_name_func:
        unique_name_func = _get_unique_resource_name_for_keycloak

    if not type_name_func:
        type_name_func = _get_resource_type_for_keycloak

    def decorator(class_method):
        # if keycloak authorization disabled do nothing
        if not settings.KEYCLOAK_SETTINGS['authorization']:
            return class_method
        keycloak_resources = KeycloakResources()

        def wrapper(*args, **kwargs):
            # authorization disabled by global variables
            if global_vars['disable_authorization_integration']:
                return class_method(*args, **kwargs)
            
            # make assumption that create method returns instance
            if authz_action == 'create':
                instance: IAuthCovered = class_method(*args, **kwargs)
                returned = instance
            else:    
                # first argument in method is self
                instance = args[0]

            # after invoke delete method id may be None
            instance_type = type_name_func(instance)
            instance_id_for_keycloak = _get_id_for_keycloak(instance, id_attr, instance_type)

            # invoke method for update or delete
            if authz_action != 'create':
                returned = class_method(*args, **kwargs)

            # after update unique name may be changed
            instance_unique_name = unique_name_func(instance)

            # make integration with keycloak    
            if authz_action == 'create':
                try:
                    keycloak_record = keycloak_resources.create(
                        instance_id_for_keycloak,
                        instance_unique_name,
                        instance_type,
                        instance.owner.username if instance.owner else None,
                        instance.get_actions_for_auth_obj()
                    )
                except KeycloakError as err:
                    log.error(f'Error occured while creating resource {str(err)}')

            if authz_action == 'update':
                try:
                    keycloak_record = keycloak_resources.update(
                        instance_id_for_keycloak,
                        instance_unique_name,
                        instance_type,
                        instance.owner.username,
                        instance.get_actions_for_auth_obj()
                    )
                except KeycloakError as err:
                    log.error(f'Error occured while updating resource {str(err)}')

            if authz_action == 'delete':
                try:
                    keycloak_resources.delete(
                        instance_id_for_keycloak,
                    )
                except KeycloakError as err:
                    log.error(f'Error occured while deleting resource {str(err)}')

            return returned

        return wrapper
    return decorator


def _plugin_name(obj):
    """
    Returns plugin name for object
    """
    return obj.__module__.split('.')[0]

def _get_id_for_keycloak(instance: IAuthCovered, id_attr: str, instance_type):
    obj_id_attr = getattr(instance, id_attr)
    if isinstance(obj_id_attr, uuid.UUID):
        instance_id_for_keycloak = str(obj_id_attr)
    else:
        id_hash = hashlib.md5(
            (instance_type + str(obj_id_attr)).encode()
        )
        instance_id_for_keycloak = str(uuid.UUID(id_hash.hexdigest()))
    return instance_id_for_keycloak

def _get_resource_type_for_keycloak(obj: IAuthCovered):
    return f'{_plugin_name(obj)}.{type(obj).__name__}'


def _get_unique_resource_name_for_keycloak(obj: IAuthCovered):
    if not isinstance(obj, IAuthCovered):
        return ''
    obj_type = _get_resource_type_for_keycloak(obj)
    instance_unique_name = f'{obj_type}:{obj.auth_name}'
    return instance_unique_name


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
            # check_permissions_in_auth_covered_methods - flag on class args[0] - instance of class
            if not ignore_authorization and args[0].check_permissions_in_auth_covered_methods:
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
            func.auth_id = None
            func.auth_name = None
            check_authorization(func, action_name)
            return func(*args, **kwargs)

        return wrapper
    return decorator


def ignore_authorization_decorator(f):

    def wrapper(*args, **kwargs):
        ignore_auth_state = global_vars['disable_authorization']
        global_vars['disable_authorization'] = True
        result = f(*args, **kwargs)
        global_vars['disable_authorization'] = ignore_auth_state
        return result

    return wrapper