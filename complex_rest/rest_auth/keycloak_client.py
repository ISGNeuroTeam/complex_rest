import requests
from typing import List, Dict
from django.conf import settings
from keycloak.keycloak_openid import KeycloakOpenID
from keycloak.connection import ConnectionManager
from keycloak.urls_patterns import (
    URL_TOKEN,
)
from urllib.parse import urlencode
from keycloak.exceptions import raise_error_from_response, KeycloakPostError, KeycloakError
from keycloak.openid_connection import KeycloakOpenIDConnection
from keycloak.keycloak_uma import KeycloakUMA
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
        self.host_header_authz_req = settings.KEYCLOAK_SETTINGS['host_header_for_authorization_request']

    def authorization_request(self, auth_header, action: str, resource_unique_name: str = ''):
        payload = {
            "grant_type": "urn:ietf:params:oauth:grant-type:uma-ticket",
            "permission": f'{resource_unique_name}#{action}',
            "response_mode": "decision",
            "audience": self.client_id,
        }

        # Everyone always has the null set of permissions
        # However keycloak cannot evaluate the null set
        if len(payload["permission"]) == 0:
            return True

        connection = ConnectionManager(self.connection.base_url)
        connection.add_param_headers("Authorization", auth_header)
        connection.add_param_headers("Content-Type", "application/x-www-form-urlencoded")
        connection.add_param_headers("Host", self.host_header_authz_req)
        data_raw = connection.raw_post(URL_TOKEN.format(**{"realm-name": self.realm_name}), data=payload)
        try:
            data = raise_error_from_response(data_raw, KeycloakPostError)
        except KeycloakPostError:
            return False
        return data.get("result", False)


class KeycloakResources:
    def __init__(self):
        openid_connection = KeycloakOpenIDConnection(
            server_url=settings.KEYCLOAK_SETTINGS['server_url'],
            client_id=settings.KEYCLOAK_SETTINGS['client_id'],
            client_secret_key=settings.KEYCLOAK_SETTINGS['client_secret_key'],
            realm_name=settings.KEYCLOAK_SETTINGS['realm_name']
        )
        self.keycloak_uma = KeycloakUMA(openid_connection)

    def create(
            self, unique_resource_name: str, resource_type: str, owner_name: str,
            scopes: List[str] = None,
            additional_attrs: Dict[str, List[str]] = None
    ):
        payload = {
            'name': unique_resource_name,
            'type': resource_type,
            'owner': owner_name,
            'ownerManagedAccess': True,
        }
        if additional_attrs:
            payload['attributes'] = additional_attrs

        if scopes:
            payload['resource_scopes'] = scopes

        resource = self.keycloak_uma.resource_set_create(payload)
        return resource

    def get_by_name(self, unique_resource_name: str):
        ids_list = self.keycloak_uma.resource_set_list_ids(exact_name=True, name=unique_resource_name)
        resource_id = ids_list[0]
        resource = self.keycloak_uma.resource_set_read(resource_id=resource_id)
        return resource



