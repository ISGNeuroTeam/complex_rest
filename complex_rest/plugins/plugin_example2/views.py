from rest.response import Response
from rest.decorators import api_view, permission_classes
from rest import permissions


@api_view(['GET', ])
@permission_classes((permissions.AllowAny,))
def hello(request):
    return Response({'msg': 'Hello plugin_example2'})
