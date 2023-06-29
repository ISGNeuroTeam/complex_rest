import json

from typing import List, Iterable
from functools import wraps
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated

from core.load_plugins import import_string
from rest.views import APIView
from rest.response import Response, SuccessResponse, ErrorResponse, status

from rest_auth.models import Action, IAuthCovered, IKeyChain, AuthCoveredClass

from .. import serializers
from ..models import Group, Permit, SecurityZone, Role

User = get_user_model()


class UserViewSet(ModelViewSet):
    permission_classes = (IsAdminUser, )
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        return User.objects.all()


class GroupViewSet(ModelViewSet):
    permission_classes = (IsAdminUser,)
    serializer_class = serializers.GroupSerializer

    def get_queryset(self):
        return Group.objects.all()


class RoleViewSet(ModelViewSet):
    permission_classes = (IsAdminUser, )
    serializer_class = serializers.RoleSerializer

    def get_queryset(self):
        return Role.objects.all()


class GroupUserViewSet(ViewSet):
    permission_classes = (IsAdminUser,)
    serializer_class = serializers.UserSerializer

    def get_query_set(self, group_id: int):
        return Group.objects.get(pk=group_id).user_set.all()

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
    permission_classes = (IsAdminUser, )
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
    permission_classes = (IsAdminUser, )

    def get(self, request, plugin_name=None, action_id=None):
        if plugin_name:
            actions = Action.objects.filter(plugin__name=plugin_name)
        else:
            actions = Action.objects.all()
        action_serializers = serializers.ActionSerializer(actions, many=True)
        return Response(action_serializers.data)

    def post(self, request, action_id):
        action_serializer = serializers.ActionSerializer(data=request.data, partial=True)
        if not action_serializer.is_valid():
            return ErrorResponse(http_status=status.HTTP_400_BAD_REQUEST)
        try:
            action = Action.objects.get(id=action_id)
        except Action.DoesNotExist:
            return ErrorResponse(
                status=status.HTTP_404_NOT_FOUND, error_message=f'Action with id {action_id} not found'
            )
        action.default_rule = action_serializer.validated_data['default_rule']
        action.save()
        return Response(data=serializers.ActionSerializer(action).data, status=status.HTTP_200_OK)


class AuthCoveredClassView(APIView):
    permission_classes = (IsAdminUser, )

    def get(self, request, plugin_name=None):
        if plugin_name:
            acc = AuthCoveredClass.objects.filter(plugin__name=plugin_name)
        else:
            acc = AuthCoveredClass.objects.all()
        acc_serializres = serializers.AuthCoveredClassSerializer(acc, many=True)
        return Response(acc_serializres.data)


class SecurityZoneViewSet(ModelViewSet):
    permission_classes = (IsAdminUser, )
    serializer_class = serializers.SecurityZoneSerializer

    def get_queryset(self):
        return SecurityZone.objects.all()


class PermitViewSet(ModelViewSet):
    serializer_class = serializers.PermitSerializer
    permission_classes = (IsAdminUser, )

    def get_serializer_context(self):
        """
        pass kwargs from url to permit serializer
        """
        context = super().get_serializer_context()
        context.update(self.kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        return Permit.objects.all()


class KeychainViewSet(ViewSet):
    """
    Keychain crud
    obj_class - string that specify object class
    """
    permission_classes = (IsAdminUser, )

    def list(self, request, auth_covered_class: str):
        """
        Args:
            obj_class - dotted path to class
        Returns list of keychain ids
        """
        try:
            auth_covered_class = import_string(auth_covered_class)
        except ImportError as err:
            return ErrorResponse(error_message=str(err))

        keychains = auth_covered_class.keychain_model.get_keychains()

        keychain_serializer = serializers.KeyChainSerializer(
            list(
                map(
                    lambda keychain: {
                        'permits':    keychain.permissions,
                        'security_zone': keychain.zone if keychain.zone else None,
                        'id': keychain.auth_id,
                        'name': keychain.name,
                        'auth_covered_objects': list(map(lambda x: x.auth_id, keychain.get_auth_objects()))
                    },
                    keychains
                ),
            ),
            many=True
        )
        return Response(data=keychain_serializer.data)

    def _update_keychain(
            self, keychain, auth_covered_class,
            permits: Iterable[Permit] = None, security_zone: SecurityZone=None,
            auth_covered_objects_ids: Iterable = None
    ):

        if auth_covered_objects_ids is None:
            auth_covered_objects_ids = []

        for auth_covered_object_id in auth_covered_objects_ids:
            auth_covered_object = auth_covered_class.get_auth_object(auth_covered_object_id)
            auth_covered_object.keychain = keychain

        # add permissions to keychain
        if permits:
            for permit in permits:
                keychain.add_permission(permit)

        if security_zone:
            keychain.zone = security_zone

    def create(self, request, auth_covered_class: str, *args, **kwargs):
        """
        Create new keychain
        """
        try:
            auth_covered_class = import_string(auth_covered_class)
        except ImportError as err:
            return ErrorResponse(error_message=str(err))
        key_chain_serializer = serializers.KeyChainSerializer(data=request.data)
        if not key_chain_serializer.is_valid():
            return ErrorResponse(
                error_message=str(key_chain_serializer.error_messages), http_status=status.HTTP_400_BAD_REQUEST
            )

        new_keychain: IKeyChain = auth_covered_class.keychain_model()
        auth_covered_objects_ids = None
        if 'auth_covered_objects' in key_chain_serializer.validated_data:
            auth_covered_objects_ids = key_chain_serializer.validated_data['auth_covered_objects']
            if auth_covered_objects_ids:
                auth_covered_objects = list(
                    map(
                        lambda auth_id: auth_covered_class.get_auth_object(auth_id),
                        auth_covered_objects_ids
                    )
                )
                new_keychain.add_auth_object(auth_covered_objects)

        permits = None
        if 'permits' in key_chain_serializer.validated_data:
            permits = key_chain_serializer.validated_data['permits']
            # add permissions to keychain
            if permits:
                for permit in permits:
                    new_keychain.add_permission(permit)
        security_zone = None
        if 'security_zone' in key_chain_serializer.validated_data:
            security_zone = key_chain_serializer.validated_data['security_zone']
            new_keychain.zone = security_zone

        if 'name' in key_chain_serializer.validated_data:
            new_keychain.name = key_chain_serializer.validated_data['name']

        return Response(
            data={
                'id': new_keychain.auth_id,
                'permits': map(lambda p: p.id, permits) if permits else [],
                'auth_covered_objects': auth_covered_objects_ids,
                'security_zone': new_keychain.zone.id if new_keychain.zone else None,
                'name': new_keychain.name if new_keychain.name else None
            },
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, auth_covered_class: str, pk=None):
        """
        Returns keychain with id and with objects ids
        """
        try:
            auth_covered_class = import_string(auth_covered_class)
        except ImportError as err:
            return ErrorResponse(error_message=str(err))

        try:
            keychain = auth_covered_class.keychain_model.get_keychain(pk)
        except Exception:
            return ErrorResponse(
                http_status=status.HTTP_404_NOT_FOUND,
                error_message=f'Keychain with id={pk} not found'
            )
        keychain_auth_covered_objects_ids = list(
            map(
                lambda auth_obj: auth_obj.auth_id,
                keychain.get_auth_objects()
            )
        )
        return Response(
            data={
                    'permits': map(
                        lambda p: p.id,
                        keychain.permissions
                    ),
                    'security_zone': keychain.zone.id if keychain.zone else None,
                    'id': str(keychain.auth_id),
                    'name': keychain.name,
                    'auth_covered_objects': keychain_auth_covered_objects_ids
                }
        )

    def partial_update(self, request, auth_covered_class: str, pk=None):
        try:
            auth_covered_class = import_string(auth_covered_class)
        except ImportError as err:
            return ErrorResponse(error_message=str(err))

        keychain = auth_covered_class.keychain_model.get_keychain(pk)

        key_chain_serializer = serializers.KeyChainSerializer(data=request.data)
        if not key_chain_serializer.is_valid():
            return ErrorResponse(
                error_message=str(key_chain_serializer.error_messages), http_status=status.HTTP_400_BAD_REQUEST
            )

        if 'auth_covered_objects' in key_chain_serializer.validated_data:
            auth_covered_objects_ids = key_chain_serializer.validated_data['auth_covered_objects']
            if auth_covered_objects_ids is None:
                auth_covered_objects_ids = []

            if auth_covered_objects_ids:
                auth_covered_objects = list(map(
                    lambda auth_obj_id: auth_covered_class.get_auth_object(auth_obj_id),
                    auth_covered_objects_ids
                ))
                keychain.add_auth_object(auth_covered_objects, replace=True)

        # add permissions to keychain
        if 'permits' in key_chain_serializer.validated_data:
            permits = key_chain_serializer.validated_data['permits']
            keychain.remove_permissions()
            if permits:
                for permit in permits:
                    keychain.add_permission(permit)

        if 'security_zone' in key_chain_serializer.validated_data:
            security_zone = key_chain_serializer.validated_data['security_zone']
            keychain.zone = security_zone

        if 'name' in key_chain_serializer.validated_data:
            keychain.name = key_chain_serializer.validated_data['name']

        return Response(
            data={
                'id': keychain.auth_id,
                'name': keychain.name,
                'permits': map(lambda p: p.id, keychain.permissions),
                'auth_covered_objects': auth_covered_objects_ids,
                'security_zone': keychain.zone.id if keychain.zone else None
            },
            status=status.HTTP_200_OK
        )

    def update(self, request, auth_covered_class, pk=None):
        try:
            auth_covered_class = import_string(auth_covered_class)
        except ImportError as err:
            return ErrorResponse(error_message=str(err))

        keychain = auth_covered_class.keychain_model.get_keychain(pk)

        key_chain_serializer = serializers.KeyChainSerializer(data=request.data)
        if not key_chain_serializer.is_valid():
            return ErrorResponse(
                error_message=str(key_chain_serializer.error_messages), http_status=status.HTTP_400_BAD_REQUEST
            )

        if 'auth_covered_objects' in key_chain_serializer.validated_data:
            auth_covered_objects_ids = key_chain_serializer.validated_data['auth_covered_objects']
            if auth_covered_objects_ids is None:
                auth_covered_objects_ids = []
            auth_covered_objects = list(map(
                lambda auth_covered_object_id: auth_covered_class.get_auth_object(auth_covered_object_id),
                auth_covered_objects_ids
            ))
            keychain.add_auth_object(auth_covered_objects, replace=True)
        else:
            auth_covered_objects_ids = []

        # add permissions to keychain
        keychain.remove_permissions()
        if 'permits' in key_chain_serializer.validated_data:
            permits = key_chain_serializer.validated_data['permits']
            if permits:
                for permit in permits:
                    keychain.add_permission(permit)
        else:
            permits = []

        if 'security_zone' in key_chain_serializer.validated_data:
            security_zone = key_chain_serializer.validated_data['security_zone']
        else:
            security_zone = None

        keychain.zone = security_zone

        if 'name' in key_chain_serializer.validated_data:
            keychain.name = key_chain_serializer.validated_data['name']
        else:
            keychain.name = None

        return Response(
            data={
                'id': keychain.auth_id,
                'name': keychain.name,
                'permits': map(lambda p: p.id, permits) if permits else [],
                'auth_covered_objects': auth_covered_objects_ids,
                'security_zone': keychain.zone.id if keychain.zone else None
            },
            status=status.HTTP_200_OK
        )

    def destroy(self, request, auth_covered_class: str, pk=None):
        try:
            auth_covered_class = import_string(auth_covered_class)
        except ImportError as err:
            return ErrorResponse(error_message=str(err))
        auth_covered_class.keychain_model.delete_object(pk)
        return SuccessResponse(http_status=status.HTTP_200_OK)

