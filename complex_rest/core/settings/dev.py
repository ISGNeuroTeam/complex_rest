from .base import *
DEBUG = True

if DEBUG:
    DEFAULT_RENDERER_CLASSES = DEFAULT_RENDERER_CLASSES + (
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = DEFAULT_RENDERER_CLASSES


    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': ['/'],
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


if not DEBUG:
    # remove plugin examples from installed apps if not debug mode
    INSTALLED_APPS.remove('plugin_example1')
    INSTALLED_APPS.remove('plugin_example2')
