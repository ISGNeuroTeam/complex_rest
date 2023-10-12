import json
import uuid
from jose.exceptions import JOSEError

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from logging import getLogger
from django.conf import settings
from rest_auth.models import Group, Role, User, KeycloakUser

from rest_framework import HTTP_HEADER_ENCODING, authentication
from keycloak.keycloak_openid import KeycloakOpenID

from core.globals import global_vars

from .exceptions import AuthenticationFailed, InvalidToken, TokenError
from .settings import api_settings
from .keycloak_client import KeycloakClient

log = getLogger('')

User = get_user_model()

AUTH_HEADER_TYPES = api_settings.AUTH_HEADER_TYPES


if not isinstance(api_settings.AUTH_HEADER_TYPES, (list, tuple)):
    AUTH_HEADER_TYPES = (AUTH_HEADER_TYPES,)

AUTH_HEADER_TYPE_BYTES = set(
    h.encode(HTTP_HEADER_ENCODING)
    for h in AUTH_HEADER_TYPES
)


class KeycloakAuthentication(authentication.BaseAuthentication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keycloak_client = KeycloakClient()
        self.keycloak_token_options = {
            "verify_signature": True, "verify_aud": False, "verify_exp": True
        }

    def authenticate(self, request):
        auth_header = request.META.get(api_settings.AUTH_HEADER_NAME)
        if isinstance(auth_header, str):
            # Work around django test client oddness
            auth_header = auth_header.encode(HTTP_HEADER_ENCODING)

        if not auth_header:
            return None
        try:
            token_type, access_token = auth_header.split()
        except ValueError:
            log.error('Got invalid authorization header')
            raise AuthenticationFailed(
                _('Authorization header must contain two space-delimited values'),
                code='bad_authorization_header',
            )

        keycloak_public_key = "-----BEGIN PUBLIC KEY-----\n" + self.keycloak_client.public_key() + "\n-----END PUBLIC KEY-----"
        try:
            keycloak_token = self.keycloak_client.decode_token(access_token, key=keycloak_public_key, options=self.keycloak_token_options)
        except JOSEError as err:
            return None

        user = self._fetch_user(user_info=keycloak_token)
        global_vars.set_current_user(user)
        return user, None # authentication successful

    def _keycloak_integration(self, user_info: dict) -> User:
        """
        Get user, groups and roles that don't exist from keycloak
        Args:
            user_info (dict): user info from token
        Returns User object
        """
        pass

    def _fetch_user(self, user_info: dict):
        """
        Create user from keycloak
        """
        username = user_info['preferred_username']
        first_name = user_info.get('given_name')
        last_name = user_info.get('family_name')
        email = user_info.get('email')
        guid = uuid.UUID(user_info['sub'])
        return KeycloakUser(guid, username, first_name, last_name, email, user_info['realm_access']['roles'])


    def _fetch_groups(self, user_group_info: dict):
        """
        Get user groups from keycloak if they don't exist locally
        """
        pass

    def _fetch_roles(self):
        """
        Get roles from keycloak if they don't exist locally
        """
        pass


class JWTAuthentication(authentication.BaseAuthentication):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header.
    """
    www_authenticate_realm = 'api'

    def authenticate(self, request):
        raw_token = None
        # if cookie is present, authenticate with cookie
        cookie = self.get_cookie(request)
        if cookie:
            raw_token = self.get_raw_token(cookie)
        if not raw_token:
            header = self.get_header(request)
            if header is None:
                return None
            raw_token = self.get_raw_token(header)
            if raw_token is None:
                return None
        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        global_vars.set_current_user(user)
        return user, validated_token

    def authenticate_header(self, request):
        return '{0} realm="{1}"'.format(
            AUTH_HEADER_TYPES[0],
            self.www_authenticate_realm,
        )

    def get_cookie(self, request):
        cookie = request.COOKIES.get('auth_token')
        if isinstance(cookie, str):
            cookie = cookie.encode('utf-8')
        return cookie

    def get_header(self, request):
        """
        Extracts the header containing the JSON web token from the given
        request.
        """
        header = request.META.get(api_settings.AUTH_HEADER_NAME)

        if isinstance(header, str):
            # Work around django test client oddness
            header = header.encode(HTTP_HEADER_ENCODING)

        return header

    def get_raw_token(self, header):
        """
        Extracts an unvalidated JSON web token from the given "Authorization"
        header value.
        """
        parts = header.split()

        if len(parts) == 0:
            # Empty AUTHORIZATION header sent
            return None

        if parts[0] not in AUTH_HEADER_TYPE_BYTES:
            # Assume the header does not contain a JSON web token
            return None

        if len(parts) != 2:
            raise AuthenticationFailed(
                _('Authorization header must contain two space-delimited values'),
                code='bad_authorization_header',
            )

        return parts[1]

    def get_validated_token(self, raw_token):
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        messages = []
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                messages.append({'token_class': AuthToken.__name__,
                                 'token_type': AuthToken.token_type,
                                 'message': e.args[0]})

        raise InvalidToken({
            'detail': _('Given token not valid for any token type'),
            'messages': messages,
        })

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(_('Token contained no recognizable user identification'))

        try:
            user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except User.DoesNotExist:
            raise AuthenticationFailed(_('User not found'), code='user_not_found')

        if not user.is_active:
            raise AuthenticationFailed(_('User is inactive'), code='user_inactive')

        return user


def default_user_authentication_rule(user):
    # Prior to Django 1.10, inactive users could be authenticated with the
    # default `ModelBackend`.  As of Django 1.10, the `ModelBackend`
    # prevents inactive users from authenticating.  App designers can still
    # allow inactive users to authenticate by opting for the new
    # `AllowAllUsersModelBackend`.  However, we explicitly prevent inactive
    # users from authenticating to enforce a reasonable policy and provide
    # sensible backwards compatibility with older Django versions.
    return True if user is not None and user.is_active else False
