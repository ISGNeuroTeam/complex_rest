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

from rest_auth.models import Action, IAuthCovered, IKeyChain

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
        auth_covered_objects: Iterable[IAuthCovered] = auth_covered_class.get_objects()
        result_keychain_dict = dict()

        for auth_covered_object in auth_covered_objects:
            keychain = auth_covered_object.keychain
            if keychain.id in result_keychain_dict:
                # add object
                result_keychain_dict[keychain.id]['auth_covered_objects'].append(auth_covered_object.id)
            else:
                # add keychain object
                result_keychain_dict[keychain.id] = {
                    'permits':    serializers.PermitSerializer(keychain.permissions, many=True).data,
                    'security_zone': keychain.zone if keychain.zone else None,
                    'id': keychain.id,
                    'auth_covered_objects': [auth_covered_object.id, ]
                }

        result_data = serializers.KeyChainSerializer(
            map(
                lambda x: result_keychain_dict[x],
                result_keychain_dict.keys()
            ), many=True
        ).data
        return Response(data=result_data)

    def _update_keychain(
            self, keychain, auth_covered_class,
            permits: Iterable[Permit] = None, security_zone: SecurityZone=None,
            auth_covered_objects_ids: Iterable = None
    ):

        if auth_covered_objects_ids is None:
            auth_covered_objects_ids = []

        for auth_covered_object_id in auth_covered_objects_ids:
            auth_covered_object = auth_covered_class.get_object(auth_covered_object_id)
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
                for auth_covered_object_id in auth_covered_objects_ids:
                    auth_covered_object = auth_covered_class.get_object(auth_covered_object_id)
                    auth_covered_object.keychain = new_keychain

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

        return Response(
            data={
                'id': new_keychain.id,
                'permits': map(lambda p: p.id, permits) if permits else [],
                'auth_covered_objects': auth_covered_objects_ids,
                'security_zone': new_keychain.zone.id
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
        auth_covered_objects: Iterable[IAuthCovered] = auth_covered_class.get_objects()

        try:
            keychain = auth_covered_class.keychain_model.get_object(pk)
        except Exception:
            return ErrorResponse(
                http_status=status.HTTP_404_NOT_FOUND,
                error_message=f'Keychain with id={pk} not found'
            )

        keychain_auth_covered_objects_ids = []
        for auth_covered_object in auth_covered_objects:
            if auth_covered_object.keychain and str(auth_covered_object.keychain.id) == pk:
                keychain_auth_covered_objects_ids.append(auth_covered_object.id)

        return Response(
            data={
                    'permits': map(
                        lambda p: p.id,
                        keychain.permissions
                    ),
                    'security_zone': keychain.zone.id if keychain.zone else None,
                    'id': keychain.id,
                    'auth_covered_objects': keychain_auth_covered_objects_ids
                }
        )

    def partial_update(self, request, auth_covered_class: str, pk=None):
        try:
            auth_covered_class = import_string(auth_covered_class)
        except ImportError as err:
            return ErrorResponse(error_message=str(err))

        keychain = auth_covered_class.keychain_model.get_object(pk)

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
                for auth_covered_object_id in auth_covered_objects_ids:
                    auth_covered_object = auth_covered_class.get_object(auth_covered_object_id)
                    auth_covered_object.keychain = keychain

            # remove keychain from objects than is not in the list
            if auth_covered_objects_ids:
                for obj in auth_covered_class.get_objects():
                    if obj.keychain and obj.keychain.id == keychain.id and obj.id not in auth_covered_objects_ids:
                        obj.keychain = None

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

        return Response(
            data={
                'id': keychain.id,
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

        keychain = auth_covered_class.keychain_model.get_object(pk)

        key_chain_serializer = serializers.KeyChainSerializer(data=request.data)
        if not key_chain_serializer.is_valid():
            return ErrorResponse(
                error_message=str(key_chain_serializer.error_messages), http_status=status.HTTP_400_BAD_REQUEST
            )
        # remove keychain from objects than is not in the list
        for obj in auth_covered_class.get_objects():
            if obj.keychain and obj.keychain.id == keychain.id:
                obj.keychain = None

        if 'auth_covered_objects' in key_chain_serializer.validated_data:
            auth_covered_objects_ids = key_chain_serializer.validated_data['auth_covered_objects']
            if auth_covered_objects_ids is None:
                auth_covered_objects_ids = []
            for auth_covered_object_id in auth_covered_objects_ids:
                auth_covered_object = auth_covered_class.get_object(auth_covered_object_id)
                auth_covered_object.keychain = keychain
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

        return Response(
            data={
                'id': keychain.id,
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
        for obj in auth_covered_class.get_objects():
            if obj.keychain and obj.keychain.id == pk:
                obj.keychain = None
        return SuccessResponse(http_status=status.HTTP_200_OK)

