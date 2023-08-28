from rest_framework.views import APIView as DjangoAPIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest.response import Response


class APIView(DjangoAPIView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HelloView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return Response(data={'message': 'secret message '})
