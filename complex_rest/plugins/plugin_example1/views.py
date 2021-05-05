from rest.views import APIView
from rest.response import Response
from rest.permissions import IsAuthenticated, AllowAny

from .models import Person


class HelloView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        content = {'msg': 'Hello plugin_example1'}
        return Response(content)


class Persons(APIView):
    permission_classes = (AllowAny, )

    def get(self, request):
        return Response({'names': Person.objects.all().values_list('name', flat=True)})




