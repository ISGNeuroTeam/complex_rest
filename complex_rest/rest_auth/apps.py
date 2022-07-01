import logging

from importlib import import_module
from django.apps import AppConfig
from typing import Dict, List


log = logging.getLogger('root')


class RestAuthConfig(AppConfig):
    name = 'rest_auth'
    verbose_name = "Authentication and authorization"

    def ready(self):
        from django.conf import settings
        plugin_names = settings.PLUGINS
        for plugin_name in plugin_names:
            try:
                plugin = self._create_plugin_in_db(plugin_name)
                plugin_settings = import_module(f'{plugin_name}.settings')
                plugin_actions = getattr(plugin_settings, 'ROLE_MODEL_ACTIONS', None)
                if plugin_actions is not None:
                    self._create_actions_in_db(plugin, plugin_actions)
            except Exception as err:  # ignore all other errors. Otherwise, it is not possible to do migrations
                log.error(str(err))

    @staticmethod
    def _create_plugin_in_db(plugin_name: str):
        from rest_auth.models import Plugin
        return Plugin.objects.get_or_create(name=plugin_name)[0]

    @staticmethod
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
