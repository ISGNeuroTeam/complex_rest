import logging

from cache import get_cache, cache_page

from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated, AllowAny

from {{plugin_name}}.settings import ini_config

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
    # add permission classes AllowAny, IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
    permission_classes = (AllowAny, )

    # choose http methods you need
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get(self, request):
        # To get url params use request.GET dictionary
        # Example: request.GET.get('some param', None)

        log.info('Get request to {{plugin_name}}')
        return Response(
            {
                'message': 'plugin with name {{plugin_name}} created successfully. This is get request',
                'url_params': dict(request.GET)
            },
            status.HTTP_200_OK
        )

    def post(self, request):
        # To get body fields use request.data dictionary
        # request.data.get('some_field', None)

        log.info('Post request to {{plugin_name}}')
        return Response(
            {
                'message': 'plugin with name {{plugin_name}} created successfully. This is post request',
                'body_params': request.data
            },
            status.HTTP_200_OK
        )



