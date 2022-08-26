from rest.globals import global_vars


class GlobalSetMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global_vars.set_current_user(request.user)
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
