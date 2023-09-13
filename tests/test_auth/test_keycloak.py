from uuid import UUID
from rest_framework.test import APIClient
from django.test import TestCase
from django.test import override_settings
from django.conf import settings
from urllib.parse import urlencode
from importlib import reload, import_module
from rolemodel_test.models import SomePluginAuthCoveredModelUUID
from rest_auth.authorization import has_perm_on_keycloak
from rest_auth.exceptions import AccessDeniedError

import requests


KEYCLOAK_SETTINGS = {
        'enabled': True,
        'server_url': 'http://keycloak:8090',
        'client_id': 'complex_rest',
        'client_secret_key': 'MeD8Vyu1I44XvGeI7C9hIJQEhx87aETD',
        'realm_name': 'wdcplatform',
        'authorization': True,
    }
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissions',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_auth.authentication.KeycloakAuthentication', 'rest_auth.authentication.JWTAuthentication'
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'EXCEPTION_HANDLER': 'rest.exception_handler.custom_exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


with override_settings(REST_FRAMEWORK=REST_FRAMEWORK, KEYCLOAK_SETTINGS=KEYCLOAK_SETTINGS):
    # override_settings don't change rest framework settings
    # so some modules must be reloaded manualy
    rest_conf_settings = import_module('rest_framework.settings')
    reload(rest_conf_settings)
    rest_framework_view = import_module('rest_framework.views')
    reload(rest_framework_view)

    class KeycloakTestCase(TestCase):
        databases = "__all__"
        client_class = APIClient

        def _get_token_url(self):
            token_urn = '/realms/wdcplatform/protocol/openid-connect/token'
            keycloak_url = settings.KEYCLOAK_SETTINGS['server_url']
            return keycloak_url + token_urn

        def _get_keycloak_access_token(self):
            data = urlencode({
                'grant_type': 'password',
                'client_id': 'dtcd',
                'username': 'test_user',
                'password': '1q2w3e4r5t',
            })
            keycloak_token_url = self._get_token_url()
            response = requests.post(
                keycloak_token_url,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
            )
            resp_data = response.json()
            access_token = resp_data['access_token']
            return access_token

        def test_keycloak_token_auth(self):
            resp = self.client.get('/hello/')
            self.assertEqual(resp.status_code, 403)
            access_token = self._get_keycloak_access_token()
            self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access_token))
            resp = self.client.get('/hello/')

            # Access to authentication required view
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.data['message'], 'secret message')

        def test_keycloak_authorization(self):
            # create 10 plugin objects
            objs = []
            for i in range(3):
                obj = SomePluginAuthCoveredModelUUID(id=UUID(f'00000000-0000-0000-0000-00000000000{i}'))
                obj.save()
                objs.append(obj)
            access_token = self._get_keycloak_access_token()
            self.assertFalse(
                has_perm_on_keycloak(f'Bearer {access_token}', 'test.protected_action1', objs[0].auth_id)
            )
            self.assertFalse(
                has_perm_on_keycloak(f'Bearer {access_token}', 'test.protected_action1', objs[1].auth_id)
            )
            self.assertTrue(
                has_perm_on_keycloak(f'Bearer {access_token}', 'test.protected_action1', objs[2].auth_id)
            )
