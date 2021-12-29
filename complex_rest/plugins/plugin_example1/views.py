import logging

from rest.views import APIView
from rest.response import Response
from rest.permissions import IsAuthenticated, AllowAny

from .models import Person

log = logging.getLogger('plugin_example1')


class HelloView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        content = {'msg': 'Hello plugin_example1'}
        log.info('Hello view request')
        return Response(content)


class Persons(APIView):
    permission_classes = (AllowAny, )

    def get(self, request):
        log.info('Person view request')
        return Response({'names': Person.objects.all().values_list('name', flat=True)})




