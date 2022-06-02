from .base import *
DEBUG = True

if DEBUG:
    DEFAULT_RENDERER_CLASSES = DEFAULT_RENDERER_CLASSES + (
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = DEFAULT_RENDERER_CLASSES

if not DEBUG:
    # remove plugin examples from installed apps if not debug mode
    INSTALLED_APPS.remove('plugin_example1')
    INSTALLED_APPS.remove('plugin_example2')
