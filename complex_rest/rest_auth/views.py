from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest.response import SuccessResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest.views import APIView
from rest.response import Response


from . import serializers
from .apidoc import login_api_doc, logout_api_doc
from .authentication import AUTH_HEADER_TYPES
from .exceptions import InvalidToken, TokenError
from .settings import api_settings


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

    @login_api_doc
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        response = SuccessResponse(serializer.validated_data)
        response.set_cookie('auth_token', f'Bearer {serializer.validated_data["token"]}',
                            httponly=True, max_age=api_settings.ACCESS_TOKEN_LIFETIME.total_seconds())
        return response


class Logout(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.LogoutSerializer

    @logout_api_doc
    def delete(self, request):
        """logout by removing http only cookie"""
        current_user = request.user.username
        response = SuccessResponse(
            {
                'message': f'{current_user} logged out',
            }
        )
        response.delete_cookie('auth_token')
        request.session.flush()  # clear session
        return response


class IsLoggedIn(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        """checks if the user is logged in."""
        return Response(
            {
                'status': request.user.is_authenticated
            },
            status.HTTP_200_OK
        )


User = get_user_model()


class UserViewSet(ModelViewSet):
    permission_classes = (IsAdminUser, )
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()
