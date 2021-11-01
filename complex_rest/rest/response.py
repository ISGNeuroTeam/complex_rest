from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException


class SuccessResponse(Response):
    def __init__(self, data=None, http_status=status.HTTP_200_OK):
        data = data or {}
        data.update({
            'status': 'success',
            'status_code': http_status,
            'error': ''
        })
        super().__init__(data, http_status)


class ErrorResponse(Response):
    def __init__(self, data=None, http_status=status.HTTP_400_BAD_REQUEST, error_message=''):
        data = data or {}
        data.update({
            'status': 'error',
            'status_code': http_status,
            'error': error_message
        })
        super().__init__(data, http_status)

