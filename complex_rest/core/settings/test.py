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

# change database engine for testing to sqlite for plugins databases
for database_name, database_config in plugin_databases.items():
    database_config['ENGINE'] = 'django.db.backends.sqlite3'
    database_config['NAME'] = BASE_DIR / f'{database_name}.sqlite3'

DATABASES.update(plugin_databases)


INSTALLED_APPS.remove('plugin_example1')
INSTALLED_APPS.remove('plugin_example2')
