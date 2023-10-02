import logging

from typing import Any, List, Callable

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from core.globals import global_vars
from rest_auth.models.abc import IKeyChain
from rest_auth.keycloak_client import KeycloakClient, KeycloakError, KeycloakResources
from .exceptions import AccessDeniedError
from .models import User, Action, Role, Permit, Plugin, AccessRule, AuthCoveredClass
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


def has_perm(user: User, action: Action, obj: IAuthCovered = None) -> bool:
    """
    Returns True if user has right to do action on object with specified keychain, otherwise return False
    """
    if global_vars['disable_authorization']:
        return True

    if settings.KEYCLOAK_SETTINGS['authorization']:
        return has_perm_on_keycloak(
            global_vars['auth_header'], action.name,
            _get_unique_resource_name_for_keycloak(obj) if obj else ''
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


def has_perm_on_keycloak(auth_header, action_name: str, object_auth_id: str = None) -> bool:
    """
    Sends request to keycloak
    Returns True if user has right to do action on object
    Raises AccessDeniedError if some error occurred with keycloak
    """
    keycloak_client = KeycloakClient()
    try:
        return keycloak_client.authorization_request(
            auth_header, action_name, object_auth_id if object_auth_id else ''
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
        id_attr (str): attribute name for id, default is 'id'
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
            # authorization disabled by args or global variables
            if global_vars['disable_authorization']:
                return class_method(*args, **kwargs)
            if kwargs.get('ignore_authorization'):
                return class_method(*args, **kwargs)

            # make assumption that create method returns instance
            if authz_action == 'create':
                instance: IAuthCovered = class_method(*args, **kwargs)
                instance_type = type_name_func(instance)
                instance_unique_name = unique_name_func(instance)
                keycloak_record = keycloak_resources.create(
                    str(getattr(instance, id_attr)),
                    instance_unique_name,
                    instance_type,
                    instance.owner.username,
                    _get_actions_for_auth_obj(instance)
                )
                return instance

            if authz_action == 'update':
                returned = class_method(*args, **kwargs)
                # first argument in class method is self
                instance = args[0]
                instance_type = type_name_func(instance)
                instance_unique_name = unique_name_func(instance)
                keycloak_record = keycloak_resources.update(
                    str(getattr(instance, id_attr)),
                    instance_unique_name,
                    instance_type,
                    instance.owner.username,
                    _get_actions_for_auth_obj(instance)
                )
                return returned
            if authz_action == 'delete':
                returned = class_method(*args, **kwargs)
                # first argument in class method is self
                instance = args[0]
                keycloak_resources.delete(
                    str(getattr(instance, id_attr)),
                )
                return returned

            return class_method(*args, **kwargs)

        return wrapper
    return decorator


def _plugin_name(obj):
    """
    Returns plugin name for object
    """
    return obj.__module__.split('.')[0]


def _get_actions_for_auth_obj(auth_obj: IAuthCovered) -> List[str]:
    """
    Returns list of action names for auth instance
    """
    # find class that inherits IAuthCovered
    auth_cls = type(auth_obj)
    auth_covered_class = auth_cls.__mro__[auth_cls.__mro__.index(IAuthCovered)-1]
    cls_import_str = f'{auth_covered_class.__module__}.{auth_covered_class.__name__}'
    auth_covered_class = AuthCoveredClass.objects.get(class_import_str=cls_import_str)
    return list(auth_covered_class.actions.all().values_list('name', flat=True))


def _get_resource_type_for_keycloak(obj: IAuthCovered):
    return f'{_plugin_name(obj)}.{type(obj).__name__}'


def _get_unique_resource_name_for_keycloak(obj: IAuthCovered):
    if not isinstance(obj, IAuthCovered):
        return ''
    obj_type = f'{_plugin_name(obj)}.{type(obj).__name__}'
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
            func.auth_id = None
            func.auth_name = None
            check_authorization(func, action_name)
            return func(*args, **kwargs)

        return wrapper
    return decorator
