import json

from typing import List
from functools import wraps
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest.views import APIView
from rest.response import Response, SuccessResponse, ErrorResponse

from rest_auth.models import Action

from . import serializers
from .apidoc import login_api_doc, logout_api_doc
from .authentication import AUTH_HEADER_TYPES
from .exceptions import InvalidToken, TokenError
from .settings import api_settings
from .models import Group, Permit, SecurityZone


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

    def get_queryset(self):
        return User.objects.all()


class GroupViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.GroupSerializer

    def get_queryset(self):
        return Group.objects.all()


class GroupUserViewSet(ViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.UserSerializer

    def get_query_set(self, group_id: int):
        return  Group.objects.get(pk=group_id).user_set.all()

    def list(self, request, group_id: int):
        users = Group.objects.get(pk=group_id).user_set.all()
        return Response(serializers.UserSerializer(users, many=True).data)

    def _group_users_id_decor(f):
        """
        Decorator extract group and user_ids
        """
        @wraps(f)
        def wrapper(self, request, group_id):
            body = json.loads(request.body)
            user_ids = body['user_ids']
            try:
                group = Group.objects.get(pk=group_id)
            except Group.DoesNotExist:
                return ErrorResponse(http_status=404, error_message='Group not found')
            return f(self, group, user_ids)
        return wrapper

    @_group_users_id_decor
    def update(self, group: Group, user_ids: List[int]):
        group.user_set.delete()
        group.user_set.add(*user_ids)
        return SuccessResponse()

    @action(detail=False, methods=['POST'])
    @_group_users_id_decor
    def add_users(self, group: Group, user_ids: List[int]):
        group.user_set.add(*user_ids)
        return SuccessResponse()

    @action(detail=False, methods=['DELETE'])
    @_group_users_id_decor
    def remove_users(self, group: Group, user_ids: List[int]):
        group.user_set.remove(*user_ids)
        return SuccessResponse()


class GroupRoleViewSet(ViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.RoleSerializer

    def list(self, request, group_id: int):
        roles = Group.objects.get(pk=group_id).roles.all()
        return Response(serializers.RoleSerializer(roles, many=True).data)

    def _group_roles_id_decor(f):
        """
        Decorator extract group and roles_ids
        """
        @wraps(f)
        def wrapper(self, request, group_id):
            body = json.loads(request.body)
            roles_ids = body['roles_ids']
            try:
                group = Group.objects.get(pk=group_id)
            except Group.DoesNotExist:
                return ErrorResponse(http_status=404, error_message='Group not found')
            return f(self, group, roles_ids)
        return wrapper

    @_group_roles_id_decor
    def update(self, group: Group, roles_ids: List[int]):
        group.roles.delete()
        group.roles.add(*roles_ids)
        return SuccessResponse()

    @action(detail=False, methods=['POST'])
    @_group_roles_id_decor
    def add_roles(self, group: Group, roles_ids: List[int]):
        group.roles.add(*roles_ids)
        return SuccessResponse()

    @action(detail=False, methods=['DELETE'])
    @_group_roles_id_decor
    def remove_roles(self, group: Group, roles_ids: List[int]):
        group.roles.remove(*roles_ids)
        return SuccessResponse()


class ActionView(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, plugin_name=None):
        if plugin_name:
            actions = Action.objects.filter(plugin__name=plugin_name)
        else:
            actions = Action.objects.all()
        action_serializers = serializers.ActionSerializer(actions, many=True)
        return Response(action_serializers.data)


class SecurityZoneViewSet(ModelViewSet):
    permission_classes = (AllowAny, )
    serializer_class = serializers.SecurityZoneSerializer

    def get_queryset(self):
        return SecurityZone.objects.all()


class PermitViewSet(ModelViewSet):
    serializer_class = serializers.PermitSerializer
    permission_classes = (AllowAny, )

    def get_queryset(self):
        return Permit.objects.all()


