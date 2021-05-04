from datetime import timedelta

from django.conf import settings
from rest_framework.settings import APISettings
from cache import get_cache

USER_SETTINGS = settings.TOKEN_SETTINGS


DEFAULTS = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),

    'SIGNING_KEY_LIFETIME': timedelta(hours=24),
    'SIGNING_KEY_LENGTH': 32,
    'SIGNING_KEY_CHARS':
        '!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~',

    'UPDATE_LAST_LOGIN': True,


    'ALGORITHM': 'HS256',

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_TOKEN_PAYLOAD': [
        ('username', 'username'),
    ],
    'USER_AUTHENTICATION_RULE': 'rest_auth.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_auth.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',
}

DEFAULTS.update(
    SIGNING_KEY_CACHE=get_cache(
        'AuthDatabaseCache', namespace='api_keys',
        timeout=int(DEFAULTS['SIGNING_KEY_LIFETIME'].total_seconds()), max_entries=2,
    )
)


IMPORT_STRINGS = (
    'AUTH_TOKEN_CLASSES',
)


api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)


