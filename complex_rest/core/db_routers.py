from django.conf import settings


class AuthRouter:
    """
    A router to control all database operations on models in the
    auth and contenttypes applications.
    """
    route_app_labels = {'rest_auth', 'auth', 'contenttypes', 'admin', 'sessions'}

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'auth_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'auth_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth or contenttypes apps is
        involved.
        """
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth and contenttypes apps only appear in the
        'auth_db' database.
        """
        if app_label in self.route_app_labels:
            return db == 'auth_db'
        return None


class PluginRouter:
    """
    A router to control all database operations on models in the
    plugin applications. Plugin database name equals plugin name (app_label)
    """

    def db_for_read(self, model, **hints):
        if model._meta.app_label in settings.PLUGINS_WITH_DATABASES:
            return model._meta.app_label
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in settings.PLUGINS_WITH_DATABASES:
            return model._meta.app_label
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label in settings.PLUGINS_WITH_DATABASES or
            obj2._meta.app_label in settings.PLUGINS_WITH_DATABASES
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in settings.PLUGINS_WITH_DATABASES:
            return db == app_label
        return None
