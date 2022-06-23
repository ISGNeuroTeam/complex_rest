from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest.response import SuccessResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest.views import APIView
from rest.response import Response

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

from . import serializers
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

    @extend_schema(
        summary='login',
        request=serializers.AccessTokenSerializer,
        responses=serializers.TokenResponseSerializer,
        description="""
        Takes user login and password, returns user access token
        Sets cookie 'auth_token' with value 'Bearer <token>'
        """,
        examples=[
            OpenApiExample(
                name='Login request',
                value={
                    "login": "admin",
                    "password": "admin"
                },
                request_only=True,
   
            ),
            OpenApiExample(
                name="Success response",
                value={
                    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjU2MDE1NjQ3LCJpYXQiOjE2NTU5NzI0NDcsImp0aSI6ImNkNTlmMDgxYzM5YzQ5OTBhNGU3NWU1NzM2NzYxNDQ0IiwiZ3VpZCI6IjMxNjk5OWFmLWU3NTctNDE2ZC1hZjQ2LTliNDJhNDY5ZjYwNiIsImxvZ2luIjoiYWRtaW4ifQ.xyJrmq7dSCnV3pnFFKUjj_jf4Md1rCb9pcFIq-61ZWE",
                    "status": "success",
                    "status_code": 200,
                    "error": ""
                },
                response_only=True
            ),
            OpenApiExample(
                name='Login failed',
                value={
                    "detail": "No active account found with the given credentials",
                    "status_code": 401,
                    "status": "error",
                    "error": "Unauthorized"
                },
                response_only=True
            )
        ]
    )
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

    @extend_schema(
        summary='logout',
        description="logout by removing http only cookie",
        responses={
            200: OpenApiResponse(
                response=serializers.LogoutResponseSerializer,
                description='User logged out'
            )

        },
        examples=[
            OpenApiExample(
                name='Success response',
                value={
                    "message": "admin logged out",
                    "status": "success",
                    "status_code": 200,
                    "error": ""
                },
                response_only=True
            ),
        ]
    )
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
