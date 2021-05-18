"""
django settings for testing
"""
from .base import *
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'default_db.sqlite3',
    },
    'auth_db': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'auth_db.sqlite3',
    },
}

INSTALLED_APPS.remove('plugin_example1')
INSTALLED_APPS.remove('plugin_example2')
