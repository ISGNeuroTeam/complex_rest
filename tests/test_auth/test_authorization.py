from django.test import TestCase

from rest.globals import global_vars

from rest_auth.models import User, Action, Plugin, Permit, AccessRule, Role, Group
from rest_auth.authorization import (
    auth_covered_class, auth_covered_method, auth_covered_func, _get_obj_keychain_id, AccessDeniedError
)


class TestKeyChain(TestCase):

    def test_default_keychain_id(self):
        @auth_covered_class
        class ProtectedObject:
            pass

        test_object = ProtectedObject()
        self.assertEqual(_get_obj_keychain_id(test_object), 'ProtectedObject')

    def test_user_specified_default_keychain_id(self):
        user_specified_keychain_id = 'UserSpecifiedKeychainId'

        @auth_covered_class(user_specified_keychain_id)
        class ProtectedObject:
            pass

        test_object = ProtectedObject()
        self.assertEqual(_get_obj_keychain_id(test_object), user_specified_keychain_id)

    def test_keychain_property(self):
        @auth_covered_class('default_keychain')
        class ProtectedObject:
            @property
            def keychain_id(self):
                return 10

        test_object = ProtectedObject()
        self.assertEqual(_get_obj_keychain_id(test_object), 'default_keychain.10')

    def test_keychain_property_without_common_keychain(self):
        @auth_covered_class
        class ProtectedObject:
            @property
            def keychain_id(self):
                return 10

        test_object = ProtectedObject()
        self.assertEqual(_get_obj_keychain_id(test_object), 'ProtectedObject.10')


class TestAuthProtection(TestCase):
    databases = {'default', 'auth_db'}

    def setUp(self):
        self.test_user1 = User(username='test_user1')
        self.test_user1.set_password('user11q2w3e4r5t')
        self.test_user1.save()
        global_vars.set_current_user(self.test_user1)

        self.plugin = Plugin(name='test_auth')
        self.plugin.save()

        self.action = Action(name='test_action', plugin=self.plugin, default_rule=False)
        self.action.save()

    def tearDown(self):
        global_vars.delete_all()

    def _create_access_to_action(self):
        user_group = Group(name='test_group')
        user_group.save()
        self.test_user1.groups.add(user_group)
        self.test_user1.save()

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

        @auth_covered_class
        class ProtectedObject:
            @auth_covered_method(action_name='test_action')
            def protected_method(self):
                nonlocal method_was_executed
                method_was_executed = True
                return 0

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
