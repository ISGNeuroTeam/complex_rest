from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest.response import SuccessResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

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
        response = SuccessResponse(serializer.validated_data)
        response.set_cookie('auth_token', f'Bearer {serializer.validated_data["token"]}', httponly=True)
        return response


User = get_user_model()


class UserViewSet(ModelViewSet):
    permission_classes = (IsAdminUser, )
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()
