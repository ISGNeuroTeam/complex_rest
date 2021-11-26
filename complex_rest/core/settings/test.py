"""
django settings for testing
"""
from .base import *

DEBUG = False

default_database_name = str(BASE_DIR / 'default_db.sqlite3')
auth_database_name = str(BASE_DIR / 'auth_db.sqlite3')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': default_database_name,
        'TEST': {
            'NAME': default_database_name,
        },
    },
    'auth_db': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': auth_database_name,
        'TEST': {
            'NAME': auth_database_name,
        },
    },
}

# change database engine for testing to sqlite for plugins databases
for database_name, database_config in plugin_databases.items():
    plugin_database_name = str(BASE_DIR / f'{database_name}.sqlite3')

    database_config['ENGINE'] = 'django.db.backends.sqlite3'
    database_config['NAME'] = plugin_database_name
    database_config['TEST'] = {
        'NAME': plugin_database_name,
    }

DATABASES.update(plugin_databases)

INSTALLED_APPS.remove('plugin_example1')
INSTALLED_APPS.remove('plugin_example2')
