import requests
import uuid
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

    def authorization_request(self, auth_header, action: str, resource_id: str = None, resource_unique_name: str = None):
        if resource_id is None and resource_unique_name is None:
            resource_id = ''

        if resource_id is None:
            keycloak_resources = KeycloakResources()
            resource_id = keycloak_resources.get_resource_id(resource_unique_name)

        payload = {
            "grant_type": "urn:ietf:params:oauth:grant-type:uma-ticket",
            "permission": f'{resource_id}#{action}',
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
    user_url = '/admin/realms/{realm_name}/users/{user_uuid}'
    user_roles_url = '/admin/realms/{realm_name}/users/{user_uuid}/role-mappings/realm'

    def __init__(self):
        self.openid_connection = KeycloakOpenIDConnection(
            server_url=settings.KEYCLOAK_SETTINGS['server_url'],
            client_id=settings.KEYCLOAK_SETTINGS['client_id'],
            client_secret_key=settings.KEYCLOAK_SETTINGS['client_secret_key'],
            realm_name=settings.KEYCLOAK_SETTINGS['realm_name']
        )
        self.keycloak_uma = KeycloakUMA(self.openid_connection)

    def get_user(self, user_uuid: uuid.UUID) -> dict:
        data_raw = self.openid_connection.raw_get(
            self.user_url.format(user_uuid=user_uuid, realm_name=self.openid_connection.realm_name)
        )
        data = raise_error_from_response(data_raw, KeycloakError)
        return data

    def get_user_roles_names(self, user_uuid) -> List[str]:
        data_raw = self.openid_connection.raw_get(
            self.user_roles_url.format(user_uuid=user_uuid, realm_name=self.openid_connection.realm_name)
        )
        data = raise_error_from_response(data_raw, KeycloakError)
        return list(map(lambda role: role['name'], data))

    def create(
            self, _id: str, unique_resource_name: str, resource_type: str, owner_name: str=None,
            scopes: List[str] = None,
            additional_attrs: Dict[str, List[str]] = None
    ):
        """
        Args:
            _id (str): unique id, max length is 36
            unique_resource_name (str): unique resource name
            resource_type (str): resource type
            owner_name (str): owner_name
            scopes (str): list of strings (action names)
            additional_attrs (dict): any additional attributes
        """
        payload = self._form_payload(_id, unique_resource_name, resource_type, owner_name, scopes, additional_attrs)
        resource = self.keycloak_uma.resource_set_create(payload)
        return resource

    def update(
            self, _id: str, unique_resource_name: str, resource_type: str, owner_name: str=None,
            scopes: List[str] = None,
            additional_attrs: Dict[str, List[str]] = None
    ):
        """
        Args:
            _id (str): unique id, max length is 36
            unique_resource_name (str): unique resource name
            resource_type (str): resource type
            owner_name (str): owner_name
            scopes (str): list of strings (action names)
            additional_attrs (dict): any additional attributes
        """
        payload = self._form_payload(_id, unique_resource_name, resource_type, owner_name, scopes, additional_attrs)
        resource = self.keycloak_uma.resource_set_update(_id, payload)
        return resource

    def delete(self, _id: str):
        return self.keycloak_uma.resource_set_delete(_id)

    @staticmethod
    def _form_payload(
            _id: str, unique_resource_name: str, resource_type: str, owner_name: str,
            scopes: List[str] = None,
            additional_attrs: Dict[str, List[str]] = None
    ):
        """
        Args:
            _id (str): unique id, max length is 36
            unique_resource_name (str): unique resource name
            resource_type (str): resource type
            owner_name (str): owner_name
            scopes (str): list of strings (action names)
            additional_attrs (dict): any additional attributes
        """
        payload = {
            '_id': _id,
            'name': unique_resource_name,
            'type': resource_type,
            'owner': owner_name,
            'ownerManagedAccess': True,
        }
        if additional_attrs:
            payload['attributes'] = additional_attrs

        if scopes:
            payload['resource_scopes'] = scopes

        return payload

    def get_resource_id(self, unique_resource_name: str):
        ids_list = self.keycloak_uma.resource_set_list_ids(exact_name=True, name=unique_resource_name)
        return ids_list[0]

    def get_by_name(self, unique_resource_name: str):
        resource_id = self.get_resource_id(unique_resource_name)
        resource = self.keycloak_uma.resource_set_read(resource_id=resource_id)
        return resource

    def get(self, resource_id: str):
        resource = self.keycloak_uma.resource_set_read(resource_id=resource_id)
        return resource



