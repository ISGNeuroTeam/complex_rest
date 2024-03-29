"""
Django settings for complex_rest project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import logging
import sys
from pathlib import Path
from datetime import timedelta

from core import load_plugins
from .ini_config import ini_config




# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-v5acbm731on7ef(%$74iehd%yo#ek@8^6ctk_pr+yf)x$!tguz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

SESSION_COOKIE_HTTPONLY = True  # SECURITY: JavaScript won't be able to access cookies

# Application definition

INSTALLED_APPS = [
    'core.override_admin.RestAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mptt',
    'rest_framework',
    'django_celery_beat',
    'drf_spectacular',
    'drf_spectacular_sidecar',
]

LOCAL_APPS = [
    'core',
    'rest_auth'
]

INSTALLED_APPS = INSTALLED_APPS + LOCAL_APPS

PLUGINS_DIR = str(ini_config['plugins']['plugins_dir'])
PLUGIN_DEV_DIR = str(ini_config['plugins']['plugin_dev_dir'])

sys.path.append(PLUGINS_DIR)
PLUGINS = load_plugins.get_plugins_names(ini_config['plugins']['plugins_dir'])

# Add plugins to INSTALLED_APPS
INSTALLED_APPS = INSTALLED_APPS + PLUGINS

# Add plugins virtual environment to sys path
load_plugins.add_plugins_env_dirs_to_sys_path(PLUGINS_DIR, PLUGINS)


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

AUTH_USER_MODEL = 'rest_auth.User'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": 'django.db.backends.postgresql',
        "NAME": ini_config['default_db']['database'],
        "USER": ini_config['default_db']['user'],
        "PASSWORD": ini_config['default_db']['password'],
        "HOST": ini_config['default_db']['host'],
        "PORT": ini_config['default_db']['port']
    },
    'auth_db': {
        "ENGINE": 'django.db.backends.postgresql',
        "NAME": ini_config['auth_db']['database'],
        "USER": ini_config['auth_db']['user'],
        "PASSWORD": ini_config['auth_db']['password'],
        "HOST": ini_config['auth_db']['host'],
        "PORT": ini_config['auth_db']['port']
    }
}

# Add plugin databases
plugin_databases = load_plugins.get_plugins_databases(PLUGINS)

PLUGINS_WITH_DATABASES = set(plugin_databases.keys())

DATABASES.update(
    plugin_databases
)


DATABASE_ROUTERS = ['core.db_routers.AuthRouter', 'core.db_routers.PluginRouter', ]

# redis connection parameters
REDIS_CONFIG = ini_config['redis']

REDIS_CONNECTION_STRING = f"redis://{REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}"

redis_cache_config_dict = {
    'BACKEND': 'cache.RedisCache',
    'LOCATION': REDIS_CONNECTION_STRING,
    'OPTIONS': {
        'DB': REDIS_CONFIG['db'],
        'PASSWORD': REDIS_CONFIG['password'],
        'CLIENT_CLASS': "django_redis.client.DefaultClient",
    },
    'TIMEOUT': ini_config['caches']['default_timeout'],
    'MAX_ENTRIES': ini_config['caches']['default_max_entries'],
}
CACHES = {
    'default': redis_cache_config_dict,
    'RedisCache': redis_cache_config_dict,
    'FileCache': {
        'BACKEND': 'cache.FileCache',
        'LOCATION': ini_config['caches']['file_cache_dir'],
        'TIMEOUT': ini_config['caches']['default_timeout'],
        'MAX_ENTRIES': ini_config['caches']['default_max_entries'],
    },
    'LocMemCache': {
        'BACKEND': 'cache.LocMemCache',
        'TIMEOUT': ini_config['caches']['default_timeout'],
        'MAX_ENTRIES': ini_config['caches']['default_max_entries'],
    },
    'DatabaseCache': {
        'BACKEND': 'cache.DatabaseCache',
        'LOCATION': 'complex_rest_cache_table',
        'TIMEOUT': ini_config['caches']['default_timeout'],
        'MAX_ENTRIES': ini_config['caches']['default_max_entries'],
    },
    'AuthDatabaseCache': {
        'BACKEND': 'cache.AuthDatabaseCache',
        'LOCATION': 'auth_cache_table',
        'TIMEOUT': ini_config['caches']['default_timeout'],
        'MAX_ENTRIES': ini_config['caches']['default_max_entries'],
    },
}


SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR.parent / 'static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.parent / 'media'


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOG_DIR = Path(ini_config['logging']['log_dir'])
LOG_DIR.mkdir(exist_ok=True)

LOG_LEVEL = ini_config['logging']['level']

LOG_ROTATION = ini_config['logging']['rotate'] == 'True'


"""
For every plugin will be generated handler config and logger config. Example:
'handlers': {
                'plugin_example1_handler': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'maxBytes': 10485760,
                    'backupCount': 5,
                    'level': 'INFO',
                    'formatter': 'default',
                    'filename': '/complex_rest/logs/plugin_example1/plugin_example1.log'
                }
}
'loggers': {
    'plugin_example1': {
        'propagate': False,
        'level': 'INFO',
        'handlers': ['plugin_example1_handler'],
    }
}
"""

if LOG_ROTATION:
    plugin_log_handler_config = {
        'class': 'logging.handlers.RotatingFileHandler',
        'maxBytes': 1024 * 1024 * int(ini_config['logging']['rotation_size']),
        'backupCount': int(ini_config['logging']['keep_files']),
    }
else:
    plugin_log_handler_config = {
        'class': 'logging.FileHandler',
}

plugin_log_handler_config.update(
    {
        'level': LOG_LEVEL,
        'formatter': 'default',
    }
)

plugin_logger_config = {
    'propagate': True,
    'level': LOG_LEVEL,
}

# construct handlers config and loggers config for every plugin
plugins_log_handlers = load_plugins.get_plugins_handlers_config(PLUGINS, LOG_DIR, plugin_log_handler_config)
plugins_loggers = load_plugins.get_plugins_loggers(PLUGINS, plugin_logger_config)

kafka_log_dir = LOG_DIR / 'kafka'
kafka_log_dir.mkdir(parents=True, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
        'simple': {
            'format': '%(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': LOG_LEVEL
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': logging.WARNING,
            'filename': str(LOG_DIR / 'rest.log'),
            'formatter': 'default',

        },
        'rotate': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': logging.WARNING,
            'filename': str(LOG_DIR / 'rest.log'),
            'maxBytes': 1024 * 1024 * int(ini_config['logging']['rotation_size']),
            'backupCount': int(ini_config['logging']['keep_files']),
            'formatter': 'default',
        },
        'kafka': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': ini_config['message_broker']['log_level'],
            'filename': str(kafka_log_dir / 'kafka.log'),
            'maxBytes': 1024 * 1024 * int(ini_config['logging']['rotation_size']),
            'backupCount': int(ini_config['logging']['keep_files']),
            'formatter': 'default',
        },
        **plugins_log_handlers,
    },
    'root': {
        'handlers': ['rotate', ] if LOG_ROTATION else ['file', ],
        'level': logging.WARNING,  # rest.log contains warning and errors
    },
    'loggers': {
        'kafka': {
            'handlers': ['kafka', ],
            'level': ini_config['message_broker']['log_level'],
        },
        **plugins_loggers,
    },
}

DEFAULT_RENDERER_CLASSES = (
    'rest_framework.renderers.JSONRenderer',
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissions',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_auth.authentication.JWTAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': DEFAULT_RENDERER_CLASSES,
    'EXCEPTION_HANDLER': 'rest.exception_handler.custom_exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


period = int(ini_config['auth']['period'])
TOKEN_SETTINGS = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=period//2),
    'SIGNING_KEY_LIFETIME': timedelta(hours=period),
    'USER_ID_FIELD': 'guid',
    'USER_ID_CLAIM': 'guid',
    'USER_TOKEN_PAYLOAD': [
        ('login', 'username'),
    ],
}

# Celery Configuration Options
CELERY_TIMEZONE = 'Europe/Moscow'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

CELERY_BEAT_SCHEDULE = {
    # for complex rest scheduled tasks
}
CELERY_BEAT_SCHEDULE.update(
    load_plugins.get_plugins_celery_schedule(PLUGINS)
)

SPECTACULAR_SETTINGS = {
    'TITLE': 'Complex rest API',
    'DESCRIPTION': 'Complex rest API',
    'VERSION': '1.0.3',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_DIST': 'SIDECAR',  # shorthand to use the sidecar instead
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
}
