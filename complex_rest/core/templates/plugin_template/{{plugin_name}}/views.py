import logging

from cache import get_cache, cache_page

from rest.views import APIView
from rest.response import Response
from rest.permissions import IsAuthenticated, AllowAny

from .settings import ini_config

# you can use default logger for plugin
log = logging.getLogger('{{plugin_name}}')

# use ini_config dictionary to get config from {{plugin_name}}.conf
log.setLevel(ini_config['logging']['level'])

# several caches available
# cache in Redis
c = get_cache('RedisCache', namespace='{{plugin_name}}', timeout=300, max_entries=300)

# cache in default complex rest databse
# c = get_cache('DatabaseCache', namespace='{{plugin_name}}', timeout=300, max_entries=300)

# c = get_cache('FileCache', namespace='{{plugin_name}}', timeout=300, max_entries=300)
# c = get_cache('LocMemCache', namespace='{{plugin_name}}', timeout=300, max_entries=300)

# Cache using example:
c.set('var_name', 'Some value', timeout=200)
print(c.get('var_name'))


class ExampleView(APIView):
    permission_classes = (AllowAny, )

    def get(self, request):
        log.info('Request to {{plugin_name}}')
        return Response({'message': 'plugin with name {{plugin_name}} created successfully'})
