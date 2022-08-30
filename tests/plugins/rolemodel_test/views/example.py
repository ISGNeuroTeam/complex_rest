import logging

from cache import get_cache, cache_page

from rest.views import APIView
from rest.response import SuccessResponse, status, ErrorResponse
from rest.permissions import IsAuthenticated, AllowAny

from rolemodel_test.settings import ini_config

# you can use default logger for plugin
log = logging.getLogger('rolemodel_test')

# use ini_config dictionary to get config from rolemodel_test.conf
log.setLevel(ini_config['logging']['level'])


class ExampleView(APIView):
    # add permission classes AllowAny, IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
    permission_classes = (AllowAny, )

    # choose http methods you need
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get(self, request):
        # To get url params use request.GET dictionary
        # Example: request.GET.get('some param', None)

        log.info('Get request to rolemodel_test')

        # if some error occured return
        # return ErrorResponse(
        #     error_message='Some error message',
        #     http_status=status.HTTP_400_BAD_REQUEST
        # )

        return SuccessResponse(
            {
                'message': 'plugin with name rolemodel_test created successfully. This is get request',
                'url_params': dict(request.GET)
            },
            status.HTTP_200_OK
        )

    def post(self, request):
        # To get body fields use request.data dictionary
        # request.data.get('some_field', None)

        log.info('Post request to rolemodel_test')
        return SuccessResponse(
            {
                'message': 'plugin with name rolemodel_test created successfully. This is post request',
                'body_params': request.data
            },
            status.HTTP_200_OK
        )



