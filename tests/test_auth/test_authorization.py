from django.apps import apps
from django.conf import settings

from rest_framework.test import APIClient

from rest.test import TestCase
from core.globals import global_vars

from rest_auth.models import User, Action, Plugin, Permit, AccessRule, Role, Group, IAuthCovered
from rest_auth.authorization import (
   auth_covered_method, auth_covered_func, AccessDeniedError
)

from rolemodel_test.models import SomePluginAuthCoveredModel

from utils import create_test_users


class TestSimpleAuthProtection(TestCase):
    databases = {'default', 'auth_db'}

    def setUp(self):
        self.admin_user, self.test_users = create_test_users(1)

        global_vars.set_current_user(self.test_users[0])

        self.plugin = Plugin(name='test_auth')
        self.plugin.save()

        self.action = Action(name='test_action', plugin=self.plugin, default_rule=False)
        self.action.save()

    def tearDown(self):
        global_vars.delete_all()

    def _create_access_to_action(self):
        user_group = Group(name='test_group')
        user_group.save()
        self.test_users[0].groups.add(user_group)
        self.test_users[0].save()

        user_role = Role(name='test_role')
        user_role.save()
        user_role.groups.add(user_group)

        permit = Permit(plugin=self.plugin)
        permit.save()

        # allow
        access_rule = AccessRule(
            action=self.action,
            permit=permit,
            rule=True,
        )
        access_rule.save()

        user_role.permits.add(permit)

    def test_allow_method(self):
        method_was_executed = False

        class ProtectedObject(IAuthCovered):
            @auth_covered_method(action_name='test_action')
            def protected_method(self):
                nonlocal method_was_executed
                method_was_executed = True
                return 0

            @property
            def keychain(self):
                return None

            @property
            def owner(self):
                return None

        test_obj = ProtectedObject()
        with self.assertRaises(AccessDeniedError) as err:
            test_obj.protected_method()

        self.assertFalse(method_was_executed)

        self._create_access_to_action()

        test_obj.protected_method()
        self.assertTrue(method_was_executed)

    def test_allow_func(self):
        func_was_executed = False

        @auth_covered_func('test_action')
        def test_func():
            nonlocal func_was_executed
            func_was_executed = True

        with self.assertRaises(AccessDeniedError):
            test_func()
        self.assertFalse(func_was_executed)

        self._create_access_to_action()

        test_func()
        self.assertTrue(func_was_executed)


class TestPluginAuthCoveredClass(TestCase):

    def setUp(self):
        rest_auth_app = apps.get_app_config('rest_auth')
        print('in setup')
        rest_auth_app.ready()
        self.admin, self.test_users = create_test_users(10)

        self._admin_permits()

        global_vars.set_current_user(self.admin)
        # create 10 plugin objects
        for i in range(10):
            obj = SomePluginAuthCoveredModel()
            obj.save()

    def _admin_permits(self):
        admin_group = Group(name='admin')
        admin_group.save()
        self.admin.groups.add(admin_group)
        admin_role = Role(name='admin')
        admin_role.save()
        admin_role.groups.add(admin_group)

        plugin = Plugin.objects.get(name='rolemodel_test')
        admin_permit = Permit(plugin=plugin)
        admin_permit.save()

        # for each action create access rule for admit permit
        for action in Action.objects.all():
            access_rule = AccessRule(
                action=action,
                permit=admin_permit,
                rule=True,
            )
            access_rule.save()

        admin_role.permits.add(admin_permit)

    def test_plugin_url(self):
        client = APIClient()
        response = client.get('/rolemodel_test/v1/hello/')

    def test_obj_exists(self):
        self.assertEqual(SomePluginAuthCoveredModel.objects.all().count(), 10)

    def test_role_model_init(self):
        self.assertListEqual(
            settings.ROLE_MODEL_AUTH_COVERED_CLASSES,
            ['rolemodel_test.models.SomePluginAuthCoveredModel', ]
        )

        self.assertListEqual(
            list(Action.objects.all().values_list('name', flat=True)),
            ['test.create', 'test.protected_action1', 'test.protected_action2']
        )
