from rest_framework.test import APITestCase
from django.conf import settings
from urllib.parse import urlencode
import requests


class KeycloakTestCase(APITestCase):
    databases = "__all__"

    def _get_token_url(self):
        token_urn = '/realms/wdcplatform/protocol/openid-connect/token'
        keycloak_url = settings.KEYCLOAK_SETTINGS['server_url']
        return keycloak_url + token_urn

    def test_keycloak_token_auth(self):
        resp = self.client.get('/hello/')
        self.assertEqual(resp.status_code, 403)
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
        print(resp_data)
        access_token = resp_data['access_token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access_token))
        resp = self.client.get('/hello/')

        # Access to authentication required view
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['message'], 'secret message')

