import uuid

import requests
import os
from uuid import UUID
from rest_framework.test import APIClient
from django.test import TestCase
from django.test import override_settings
from django.conf import settings
from keycloak.exceptions import KeycloakGetError
from urllib.parse import urlencode
from importlib import reload, import_module
from rest_auth.authorization import has_perm_on_keycloak
from rest_auth.keycloak_client import KeycloakResources
from rest_auth.apps import on_ready_actions as rest_auth_on_ready_actions
from unittest import skipIf
from rest_auth.exceptions import AccessDeniedError
from rest_auth.models import User
from rest_auth.models import KeycloakUser

from rolemodel_test.models import SomePluginAuthCoveredModelUUID

test_user_name='test_user'
test_user_guid = UUID('2e4656fc-6ee0-4d46-a500-60d150f97cd2')


class KeycloakTestCase(TestCase):
    databases = "__all__"
    client_class = APIClient

    def setUp(self):
        rest_auth_on_ready_actions()

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

    @skipIf(settings.KEYCLOAK_SETTINGS['authorization'] is False, 'Skip keycloak test because of settings')
    def test_keycloak_token_auth(self):
        resp = self.client.get('/hello/')
        self.assertEqual(resp.status_code, 403)
        access_token = self._get_keycloak_access_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access_token))
        resp = self.client.get('/hello/')

        # Access to authentication required view
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['message'], 'secret message')

    @skipIf(settings.KEYCLOAK_SETTINGS['authorization'] is False, 'Skip keycloak test because of settings')
    def test_keycloak_authorization(self):
        objs = []
        for i in range(3):
            obj = SomePluginAuthCoveredModelUUID(
                id=UUID(f'00000000-0000-0000-0000-00000000000{i}'), name='test_name' + str(uuid.uuid4())
            )
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

    @skipIf(settings.KEYCLOAK_SETTINGS['authorization'] is False, 'Skip keycloak test because of settings')
    def test_create_resource(self):
        keycloak_resources = KeycloakResources()
        resource = keycloak_resources.create(str(uuid.uuid4()), 'test_name', 'test_type', 'test_user', ['read', 'write'], {'some_attr': 4})
        resource2 = keycloak_resources.create(str(uuid.uuid4()), 'test_name2', 'test_type', 'test_user', ['read', 'write'], {'some_attr': 4})
        resource_get = keycloak_resources.get_by_name('test_name')
        self.assertEqual(resource['name'], resource_get['name'])
        self.assertListEqual(resource['resource_scopes'], resource2['resource_scopes'])

    @skipIf(settings.KEYCLOAK_SETTINGS['authorization'] is False, 'Skip keycloak test because of settings')
    def test_crud_sync(self):
        rest_authorization = import_module('rest_auth.authorization')
        reload(rest_authorization)
        test_model = import_module('rolemodel_test.models')
        reload(test_model)
        test_user = User.get_user(test_user_guid)
        obj = SomePluginAuthCoveredModelUUID.create(owner=test_user)
        keycloak_resources = KeycloakResources()
        resource = keycloak_resources.get(obj.auth_id)
        self.assertEqual(str(obj.auth_id), resource['_id'])
        obj.update(name='new_name')
        resource = keycloak_resources.get(obj.auth_id)
        self.assertEqual('new_name', resource['name'])
        obj.delete()
        with self.assertRaises(KeycloakGetError):
            resource = keycloak_resources.get(obj.auth_id)

