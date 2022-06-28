from rest_framework.views import APIView as DjangoAPIView



class APIView(DjangoAPIView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
