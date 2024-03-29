import time

from datetime import timedelta
from importlib import import_module, reload
from django.test import override_settings

from cache import get_cache

from rest.test import create_test_users, APITestCase, TEST_USER_PASSWORD, TestCase

test_token_settings = {
    'ACCESS_TOKEN_LIFETIME': timedelta(seconds=4),
    'SIGNING_KEY_LIFETIME': timedelta(seconds=8),
    'USER_ID_FIELD': 'guid',
    'USER_ID_CLAIM': 'guid',
}

with override_settings(TOKEN_SETTINGS=test_token_settings):

    # to rewrite token settings with test settings
    auth_settings_module = import_module('rest_auth.settings')
    reload(auth_settings_module)
    AccessToken = import_module('rest_auth.tokens').AccessToken

    from rest_auth.exceptions import TokenError


    class TestAccessToken(TestCase):
        databases = {'default', 'auth_db'}

        def setUp(self):
            self.admin_user, test_users = create_test_users(1)
            self.test_user1 = test_users[0]

        def test_access_token(self):
            token = AccessToken()
            token['guid'] = self.test_user1.guid.hex
            encoded_token = str(token)
            token2 = AccessToken(encoded_token)
            self.assertEqual(token['guid'], token2['guid'], 'guids must be equal')

        def test_access_token_with_old_key(self):
            auth_cache = get_cache('AuthDatabaseCache', namespace='api_keys')
            auth_cache.delete('signing_key')
            auth_cache.delete('old_signing_key')
            token1 = AccessToken()
            token1['guid'] = self.test_user1.guid.hex
            encoded_token1 = str(token1)

            first_signing_key = auth_cache.get('signing_key')
            self.assertIsNotNone(first_signing_key, 'Signing key must be generated')
            time.sleep(6)

            token2 = AccessToken()
            token2['guid'] = self.test_user1.guid.hex

            encoded_token2 = str(token2)
            time.sleep(3)

            # second must be decoded with old key
            decoded_token2 = AccessToken(encoded_token2)
            self.assertEqual(token2['guid'], decoded_token2['guid'])

            # first key must expire
            first_signing_key = auth_cache.get('signing_key')
            self.assertEqual(first_signing_key, None, 'Signing key must be expired')

            # first token must expire
            with self.assertRaises(TokenError):
                AccessToken(encoded_token1)


class TestAuthentication(APITestCase):
    databases = {'default', 'auth_db'}

    def setUp(self):
        self.admin_user, test_users = create_test_users(1)
        self.test_user1 = test_users[0]

    def test_admin_token_required(self):
        self.login('test_user1', TEST_USER_PASSWORD)
        response = self.client.get('/auth/users/')
        self.assertEqual(response.status_code, 403, 'Access for ordinary user is forbidden')

        self.client.credentials()

        self.login('admin', 'admin')
        response = self.client.get('/auth/users/')
        self.assertEqual(response.status_code, 200, 'Access for admin')