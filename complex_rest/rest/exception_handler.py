from rest_framework.views import exception_handler
from rest_auth.exceptions import AccessDeniedError
from rest.response import ForbiddenResponse


def custom_exception_handler(exc, context):
    # custom AccessDeniedError handling
    if isinstance(exc, AccessDeniedError):
        response = ForbiddenResponse(str(exc))
        return response

    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code
        response.data['status'] = 'error'
        response.data['error'] = response.status_text

    return response