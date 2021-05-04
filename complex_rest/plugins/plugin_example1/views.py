from rest.views import APIView
from rest.response import Response
from rest.permissions import IsAuthenticated


class HelloView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        content = {'msg': 'Hello plugin_example1'}
        return Response(content)


