from core.globals import global_vars
from rest_auth.settings import api_settings


class GlobalSetMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global_vars.set_current_user(request.user)
        auth_header = request.META.get(api_settings.AUTH_HEADER_NAME)
        global_vars['auth_header'] = auth_header
        response = self.get_response(request)
        # when response is done delete all global vars
        global_vars.delete_all()
        return response

    @staticmethod
    def process_exception(request, exception):
        try:
            global_vars.delete_all()
        except KeyError:
            pass
