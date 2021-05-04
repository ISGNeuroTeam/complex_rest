import time

from datetime import timedelta
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from cache import get_cache
from rest_auth.models import User
from rest_auth.exceptions import TokenError

test_token_settings = {
    'ACCESS_TOKEN_LIFETIME': timedelta(seconds=4),
    'SIGNING_KEY_LIFETIME': timedelta(seconds=8),
    'USER_ID_FIELD': 'guid',
    'USER_ID_CLAIM': 'guid',
}

with override_settings(TOKEN_SETTINGS=test_token_settings):
    from rest_auth.tokens import AccessToken


    class TestAccessToken(TestCase):
        databases = {'default', 'auth_db'}

        def setUp(self):
            self.admin_user = User(username='admin', is_staff=True, is_active=True)
            self.admin_user.set_password('admin')
            self.admin_user.save()
            self.test_user1 = User(username='test_user1')
            self.test_user1.set_password('user11q2w3e4r5t')
            self.test_user1.save()

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


class TestAuthentication(TestCase):
    databases = {'default', 'auth_db'}

    def setUp(self):
        self.admin_user = User(username='admin', is_staff=True, is_active=True)
        self.admin_user.set_password('admin')
        self.admin_user.save()
        self.test_user1 = User(username='test_user1')
        self.test_user1.set_password('user11q2w3e4r5t')
        self.test_user1.save()

    def test_admin_token_required(self):
        client = APIClient()
        response = client.post('/auth/login/', data={'login': 'test_user1', 'password': 'user11q2w3e4r5t'})
        ordinary_user_token = response.data['token']

        client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(ordinary_user_token))
        response = client.get('/auth/users/')
        self.assertEqual(response.status_code, 403, 'Access for ordinary user is forbidden')

        client.credentials()

        response = client.post('/auth/login/', data={'login': 'admin', 'password': 'admin'})
        admin_token = response.data['token']

        client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(admin_token))
        response = client.get('/auth/users/')
        self.assertEqual(response.status_code, 200, 'Access for admin')






