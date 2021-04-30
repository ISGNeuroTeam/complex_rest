from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from . import serializers
from .authentication import AUTH_HEADER_TYPES
from .exceptions import InvalidToken, TokenError


class Login(generics.GenericAPIView):
    """
    Takes a set of user credentials and returns JSON web token
    """
    permission_classes = ()
    authentication_classes = ()

    serializer_class = serializers.AccessTokenSerializer

    www_authenticate_realm = 'api'

    def get_authenticate_header(self, request):
        return '{0} realm="{1}"'.format(
            AUTH_HEADER_TYPES[0],
            self.www_authenticate_realm,
        )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


User = get_user_model()


class UserViewSet(ModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()
