from django.apps import apps
from django.conf import settings

from rest_framework.test import APIClient

from rest.test import TestCase
from core.globals import global_vars

from rest_auth.models.abc import IKeyChain
from rest_auth.models import User, Action, Plugin, Permit, AccessRule, Role, Group, IAuthCovered, SecurityZone
from rest_auth.authorization import (
   auth_covered_method, auth_covered_func, AccessDeniedError
)

from rolemodel_test.models import SomePluginAuthCoveredModel, PluginKeychain

from rest.test import create_test_users, APITestCase, TEST_USER_PASSWORD


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


class TestPluginAuthCoveredModelClass(APITestCase):

    def setUp(self):
        # to make action and plugin objects
        rest_auth_app = apps.get_app_config('rest_auth')
        rest_auth_app.ready()
        self.plugin = Plugin.objects.get(name='rolemodel_test')
        self.admin, self.test_users = create_test_users(10)

        # make admin to have access to all actions
        self._admin_permits()

        # create 10 plugin objects
        for i in range(10):
            obj = SomePluginAuthCoveredModel()
            obj.save()

    def _admin_permits(self):
        admin_role = self._create_role('admin')

        self._add_role_to_user(self.admin, 'admin')

        admin_permit = Permit(plugin=self.plugin)
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

    def _create_role(self, name):

        group = Group(name=name)
        group.save()
        role = Role(name=name)
        role.save()
        role.groups.add(group)
        return role

    def _add_role_to_user(self, user, role_name: str):
        """
        adds group to user
        """
        g, created = Group.objects.get_or_create(name=role_name)
        user.groups.add(g)

    def _create_permission_for_role_and_actions(self, role_name, *action_names, allow=True, keychain: 'IKeyChain'=None):
        r = Role.objects.get(name=role_name)

        permit = self._create_permission_for_actions(*action_names, allow=allow)

        r.permits.add(permit)
        if keychain:
            keychain.add_permission(permit)

    def _create_permission_for_actions(self, *action_names, allow=True) -> Permit:
        permit = Permit(plugin=self.plugin)
        permit.save()

        for action_name in action_names:
            action = Action.objects.get(name=action_name)
            access_rule = AccessRule(
                action=action,
                permit=permit,
                rule=allow,
            )
            access_rule.save()
        return permit

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

    def test_access_without_keychain(self):
        test_user = self.test_users[1]
        global_vars.set_current_user(test_user)
        obj = SomePluginAuthCoveredModel.objects.all().first()

        # user has no access
        with self.assertRaises(AccessDeniedError):
            obj.test_method1()

        # admin has access
        global_vars.set_current_user(self.admin)
        obj.test_method1()

        global_vars.set_current_user(test_user)
        # add access to user role
        user_role = self._create_role('test_user')
        self._add_role_to_user(test_user, 'test_user')
        self._create_permission_for_role_and_actions('test_user', 'test.protected_action1')

        # now user has access
        obj.test_method1()
        global_vars.set_current_user(self.test_users[2])
        with self.assertRaises(AccessDeniedError):
            obj.test_method1()

    def test_access_with_keychain_permissions(self):
        # add user permission
        test_user = self.test_users[1]
        global_vars.set_current_user(test_user)
        obj = SomePluginAuthCoveredModel.objects.all().first()

        with self.assertRaises(AccessDeniedError):
            obj.test_method1()

        user_role = self._create_role('test_user')
        self._add_role_to_user(test_user, 'test_user')

        self._create_permission_for_role_and_actions('test_user', 'test.protected_action1')

        obj.test_method1()

        keychain = PluginKeychain()
        keychain.save()
        self._create_permission_for_role_and_actions('test_user', 'test.protected_action1', allow=False, keychain=keychain)
        obj.keychain = keychain
        obj.save()

        # now obj has keychain with no access
        with self.assertRaises(AccessDeniedError):
            obj.test_method1()

    def test_security_zone_permissions(self):
        test_user = self.test_users[1]
        global_vars.set_current_user(test_user)
        obj = SomePluginAuthCoveredModel.objects.all().first()

        with self.assertRaises(AccessDeniedError):
            obj.test_method1()

        zone = SecurityZone(name='test_zone1')
        zone.save()

        permit = self._create_permission_for_actions('test.protected_action1', allow=True)
        zone.permits.add(permit)
        keychain = PluginKeychain()
        keychain.zone = zone
        keychain.save()
        role = self._create_role('test_role1')
        role.permits.add(permit)
        self._add_role_to_user(test_user, 'test_role1')

        obj.test_method1()
