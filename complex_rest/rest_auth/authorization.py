import logging

from typing import Optional, Any, Callable
from django.core.exceptions import ObjectDoesNotExist
from rest.globals import global_vars
from .exceptions import OwnerIDError, KeyChainIDError, ActionError, AccessDeniedError
from .models import User, KeyChain, Action, Role, Permit, Plugin


log = logging.getLogger('root')


def has_perm(user: User, action: Action, obj: Any):
    pass


def check_authorisation(obj, action_name):
    user = global_vars.get_current_user()
    plugin_name = obj.__class__.__module__.split('.')[0]

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


# def check_authorization(action: str, when_denied: Optional[Any] = None, on_error: Optional[Callable] = None):
#     def deco(func):
#         def wrapper(obj: BaseProtectedResource, *args, **kwargs):
#             try:
#                 owner = User.objects.get(id=obj.owner_id) if obj.owner_id else None
#             except User.DoesNotExist:
#                 if on_error:
#                     return on_error(f"Owner with ID {obj.owner_id} unknown")
#                 raise OwnerIDError("Owner unknown", obj.owner_id)
#
#             try:
#                 act = Action.objects.get(name=action, plugin__name=obj.plugin)
#             except Action.DoesNotExist:
#                 if on_error:
#                     return on_error(f"Action with name {action} unknown")
#                 raise ActionError("Action unknown", action)
#
#             is_owner = obj.user == owner if owner else None
#
#             if obj.keychain_id:
#                 try:
#                     permits = KeyChain.objects.get(id=obj.keychain_id).permissions
#                 except KeyChain.DoesNotExist:
#                     if on_error:
#                         return on_error(f"Keychain with ID {obj.owner_id} unknown")
#                     raise KeyChainIDError("keychain unknown", obj.keychain_id)
#             else:
#                 permits = Permit.objects.filter(
#                     actions=act,
#                     roles__in=Role.objects.filter(groups__in=obj.user.groups.all())
#                 )
#
#             permissions = (
#                 {
#                     permit.allows(
#                         obj.user, act, by_owner=is_owner) for permit in permits if permit.affects_on(obj.user)
#                 }
#             )
#
#             if permissions and permissions != {None}:
#                 if False not in permissions:
#                     return func(obj, *args, **kwargs)
#             else:
#                 if act.default_rule is True:
#                     return func(obj, *args, **kwargs)
#
#             return when_denied
#
#         return wrapper
#     return deco

