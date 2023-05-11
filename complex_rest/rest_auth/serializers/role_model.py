from  rest_framework import serializers
from rest_auth.models import User, Group, Role, Permit, Action, AccessRule, SecurityZone, AuthCoveredClass
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError
from core.load_plugins import import_string


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class AuthCoveredClassSerializer(serializers.ModelSerializer):
    plugin = serializers.SerializerMethodField('plugin_name')

    def plugin_name(self, acc):
        return acc.plugin.name

    class Meta:
        model = AuthCoveredClass
        fields = ['id', 'plugin', 'class_import_str']


class GroupSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), source='user_set', allow_null=True
    )
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'users', 'roles']
        extra_kwargs = {'users': {'required': False}, 'roles': {'required': False}}


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    @staticmethod
    def _make_password_hash(validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])

    def create(self, validated_data):
        self._make_password_hash(validated_data)
        return super(UserSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        self._make_password_hash(validated_data)
        return super(UserSerializer, self).update(instance, validated_data)

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'groups': {'required': False}}


class ActionSerializer(serializers.ModelSerializer):
    plugin_name = serializers.CharField(source='plugin.name')

    class Meta:
        model = Action
        fields = ('id', 'name', 'default_rule', 'plugin_name', )


class AccessRuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccessRule
        fields = ('id', 'action', 'rule', 'by_owner_only')
        extra_kwargs = {'action': {'required': True}}


class PermitSerializer(serializers.ModelSerializer):
    access_rules = AccessRuleSerializer(many=True)
    roles = serializers.PrimaryKeyRelatedField(many=True, queryset=Role.objects.all())
    keychain_ids = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)
    security_zone_name = serializers.CharField(default=None, allow_null=True)

    def create(self, validated_data):

        access_rules_data = validated_data.pop('access_rules')
        security_zone_name = validated_data.pop('security_zone_name')
        if 'keychain_ids' in validated_data:
            keychain_ids = validated_data.pop('keychain_ids')
        else:
            keychain_ids = None

        if keychain_ids and security_zone_name:
            raise ValidationError('Only keychain id or security zone')

        permit_instance = super().create(validated_data)

        # save access rules for permit
        for access_rule in access_rules_data:
            access_rule_model = AccessRule(**access_rule)
            access_rule_model.permit = permit_instance
            access_rule_model.save()

        auth_covered_class = self.context['auth_covered_class']
        try:
            auth_covered_class = import_string(auth_covered_class)
        except ImportError as err:
            raise ValidationError(error_message=str(err))

        if keychain_ids:
            for keychain_id in keychain_ids:
                keychain = auth_covered_class.keychain_model.get_object(keychain_id)
                keychain.add_permission(permit_instance)

        if security_zone_name:
            security_zone = SecurityZone.objects.get(name=security_zone_name)
            security_zone.permits.add(permit_instance)

        return permit_instance

    def update(self, instance, validated_data):
        access_rules_data = validated_data.pop('access_rules', None)
        keychain_ids = validated_data.pop('keychain_ids', None)
        security_zone_name = validated_data.pop('keychain_ids', None)
        super().update(instance, validated_data)
        permit_instance = instance

        if access_rules_data is not None:
            permit_instance.access_rules.all().delete()
            # save access rules for permit
            for access_rule in access_rules_data:
                access_rule_model = AccessRule(**access_rule)
                access_rule_model.permit = permit_instance
                access_rule_model.save()

        auth_covered_class = self.context['auth_covered_class']
        try:
            auth_covered_class = import_string(auth_covered_class)
        except ImportError as err:
            raise ValidationError(error_message=str(err))

        if keychain_ids is not None:
            permit_instance.delete_keychains()

        if keychain_ids:
            for keychain_id in keychain_ids:
                keychain = auth_covered_class.keychain_model.get_object(keychain_id)
                keychain.add_permission(permit_instance)

        if security_zone_name is not None:
            security_zone = SecurityZone.objects.get(name=security_zone_name)
            security_zone.permits.add(permit_instance)

        return permit_instance

    class Meta:
        model = Permit
        fields = '__all__'


class SecurityZoneSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=SecurityZone.objects.all(), allow_null=True
    )

    class Meta:
        model = SecurityZone
        fields = ('id', 'name', 'parent')


class KeyChainSerializer(serializers.Serializer):
    id = serializers.CharField(allow_null=True, default=None)
    security_zone = serializers.PrimaryKeyRelatedField(
        queryset=SecurityZone.objects.all(), required=False, allow_null=True
    )
    permits = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Permit.objects.all(), required=False, allow_null=True,
    )
    auth_covered_objects = serializers.ListField(child=serializers.CharField(), allow_empty=True, required=False)


