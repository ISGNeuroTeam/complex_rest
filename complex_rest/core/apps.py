from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = "Core application"

    def ready(self):
        # initialize celery app and autodiscover tasks
        from core.celeryapp import app