import logging

from importlib import import_module
from django.apps import AppConfig
from typing import Dict, List


log = logging.getLogger('root')


def _create_auth_covered_classes_in_db(plugin: 'Plugin', classes_import_str: Dict[str, list[str]]):
    from rest_auth.models import AuthCoveredClass
    from rest_auth.models import Action
    for class_import_str in classes_import_str.keys():
        auth_covered_class, created = AuthCoveredClass.objects.get_or_create(
            class_import_str=class_import_str, plugin=plugin
        )
        # suppose that actions already created
        for action_name in classes_import_str[class_import_str]:
            action = Action.objects.get(name=action_name, plugin=plugin)
            auth_covered_class.actions.add(action)


def _create_plugin_in_db(plugin_name: str):
    from rest_auth.models import Plugin
    return Plugin.objects.get_or_create(name=plugin_name)[0]


def _create_actions_in_db(plugin, actions: List[Dict]):
    from rest_auth.models import Action
    for action_name, action_dict in actions.items():
        try:
            Action.objects.get_or_create(
                name=action_name, plugin=plugin,
                defaults=action_dict
            )
        except TypeError as err:
            log.error(f'Improperly configured ROLE_MODEL_ACTION in plugin settings.py: {err}')


def on_ready_actions():
    from django.conf import settings
    plugin_names = settings.PLUGINS
    for plugin_name in plugin_names:
        try:
            plugin = _create_plugin_in_db(plugin_name)
            plugin_settings = import_module(f'{plugin_name}.settings')
            plugin_actions = getattr(plugin_settings, 'ROLE_MODEL_ACTIONS', None)
            if plugin_actions is not None:
                _create_actions_in_db(plugin, plugin_actions)
            auth_covered_classes = getattr(plugin_settings, 'ROLE_MODEL_AUTH_COVERED_CLASSES')
            _create_auth_covered_classes_in_db(plugin, auth_covered_classes)
        except Exception as err:  # ignore all other errors. Otherwise, it is not possible to do migrations
            log.error(str(err))


class RestAuthConfig(AppConfig):
    name = 'rest_auth'
    verbose_name = "Authentication and authorization"

    def ready(self):
        on_ready_actions()



