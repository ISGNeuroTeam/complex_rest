from rest.views import APIView
from rest.response import Response
from rest.permissions import  AllowAny


class HelloView(APIView):
    permission_classes = (AllowAny, )

    def get(self, request):
        return Response(
            {
                'message': 'Hello',
            }
        )


