from rest.test import TransactionTestCase
from rest_auth.apps import on_ready_actions as rest_auth_on_ready_actions
from rest_auth.models import AuthCoveredClass


class SettingsApiTest(TransactionTestCase):
    def setUp(self):
        rest_auth_on_ready_actions()

    def test_auth_covered_class_created(self):
        class_import_string = AuthCoveredClass.objects.all().first().class_import_str
        self.assertEquals(class_import_string, 'rolemodel_test.models.SomePluginAuthCoveredModel')

