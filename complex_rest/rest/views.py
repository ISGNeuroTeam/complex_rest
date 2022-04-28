from rest_framework.views import APIView

superclass = APIView


class APIView(superclass):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
