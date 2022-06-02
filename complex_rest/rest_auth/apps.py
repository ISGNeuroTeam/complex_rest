from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'rest_auth'
    verbose_name = "Authentication and authorization"

    def ready(self):
        try:
            from django.conf import settings
            from rest_auth.models import Plugin
            plugin_names = settings.PLUGINS
            for plugin_name in plugin_names:
                try:
                    plugin = Plugin.objects.get(name=plugin_name)
                except Plugin.DoesNotExist:
                    plugin = Plugin(name=plugin_name)
                    plugin.save()

        except Exception:  # ignore all other errors. Otherwise, it is not possible to do migrations
            pass
