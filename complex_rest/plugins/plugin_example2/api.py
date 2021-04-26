from django.http import JsonResponse

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions


def simple_hello(request):
    return JsonResponse({'msg': 'Simple hello'})


@api_view(['GET', ])
@permission_classes((permissions.AllowAny,))
def hello(request):
    return Response({'msg': 'Hello plugin_example2'})
