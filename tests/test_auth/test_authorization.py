from django.test import TestCase

from core.globals import global_vars

from rest_auth.models import User, Action, Plugin, Permit, AccessRule, Role, Group, IAuthCovered
from rest_auth.authorization import (
   auth_covered_method, auth_covered_func, AccessDeniedError
)

from utils import create_test_users


class TestAuthProtection(TestCase):
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
