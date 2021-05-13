from .base import *
DEBUG = True

if DEBUG:
    DEFAULT_RENDERER_CLASSES = DEFAULT_RENDERER_CLASSES + (
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = DEFAULT_RENDERER_CLASSES
