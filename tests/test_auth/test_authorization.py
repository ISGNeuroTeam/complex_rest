from django.test import TestCase

from rest.globals import global_vars

from rest_auth.models import User, Action, Plugin, Permit, AccessRule, Role
from rest_auth.authorization import (
    auth_covered_class, auth_covered_method, _get_obj_keychain_id, AccessDeniedError
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

    def test_deny_method(self):

        @auth_covered_class
        class ProtectedObject:
            @auth_covered_method(action_name='test_action')
            def protected_method(self):
                return 0

        test_obj = ProtectedObject()
        with self.assertRaises(AccessDeniedError) as err:
            test_obj.protected_method()

    def test_allow_method(self):

        @auth_covered_class
        class ProtectedObject:
            @auth_covered_method(action_name='test_action')
            def protected_method(self):
                return 0
