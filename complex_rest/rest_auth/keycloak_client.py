from django.conf import settings
from keycloak.keycloak_openid import KeycloakOpenID
from keycloak.urls_patterns import (
    URL_TOKEN,
)
from keycloak.exceptions import raise_error_from_response, KeycloakPostError, KeycloakError
from urllib.parse import urljoin


class KeycloakClient(KeycloakOpenID):
    def __new__(cls):
        """
        Making singleton
        """
        if not hasattr(cls, 'instance'):
            cls.instance = super(KeycloakClient, cls).__new__(cls)
        return cls.instance

    def __init__(self, *args, **kwargs):
        """
        Get initial parameters from settings
        """
        kwargs.update({
            'server_url': settings.KEYCLOAK_SETTINGS['server_url'],
            'client_id': settings.KEYCLOAK_SETTINGS['client_id'],
            'client_secret_key': settings.KEYCLOAK_SETTINGS['client_secret_key'],
            'realm_name': settings.KEYCLOAK_SETTINGS['realm_name']
        })
        super(KeycloakClient, self).__init__(*args, **kwargs)

    def authorization_request(self, auth_header, action: str, resource_unique_name: str = ''):
        params_path = {"realm-name": self.realm_name}
        payload = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:uma-ticket',
            'response_mode': 'decision',
            'permission': f'{resource_unique_name}#{action}',
            'audience': self.client_id
        }

        payload = self._add_secret_key(payload)
        self.connection.headers.update({'Authorization': auth_header})
        data_raw = self.connection.raw_post(URL_TOKEN.format(**params_path), data=payload)
        data = raise_error_from_response(data_raw, KeycloakPostError)
        if 'result' in data and data['result'] is True:
            return True
        else:
            return False


