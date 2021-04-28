"""
Django settings for complex_rest project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import sys
from pathlib import Path
from datetime import timedelta

from .ini_config import ini_config


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-v5acbm731on7ef(%$74iehd%yo#ek@8^6ctk_pr+yf)x$!tguz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core'
]

# Add plugins to INSTALLED_APPS
sys.path.append(str(ini_config['plugins']['plugins_dir']))
PLUGINS = [full_plugin_path.name for full_plugin_path in Path(ini_config['plugins']['plugins_dir']).iterdir()]
INSTALLED_APPS = INSTALLED_APPS + PLUGINS


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

DATABASE_ROUTERS = ['core.db_routers.AuthRouter', ]


redis_cache_config_dict = {
    'BACKEND': 'cache.RedisCache',
    'LOCATION': f'redis://{ini_config["redis"]["host"]}:{ini_config["redis"]["port"]}',
    'OPTIONS': {
        'DB': ini_config['redis']['DB'],
        'PASSWORD': ini_config['redis']['password'],
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
    }
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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
    },
}


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissions',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}