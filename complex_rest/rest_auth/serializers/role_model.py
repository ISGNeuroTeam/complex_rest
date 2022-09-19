from  rest_framework import serializers
from rest_auth.models import User, Group, Role, Permit, Action, AccessRule, SecurityZone


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "is_superuser", "username", "first_name", "last_name",
            "is_staff", "is_active", "guid", "email", "phone", "photo", "groups",
        )


class GroupSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), source='user_set', allow_null=True
    )

    roles = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Role.objects.all(), allow_null=True
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'users', 'roles']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class ActionSerializer(serializers.ModelSerializer):
    plugin_name = serializers.CharField(source='plugin.name')

    class Meta:
        model = Action
        fields = ('id', 'name', 'default_rule', 'plugin_name', )


class AccessRuleSerializer(serializers.ModelSerializer):
    action = serializers.PrimaryKeyRelatedField(
        queryset=Action.objects.all()
    )

    class Meta:
        model = AccessRule
        fields = ('id', 'action', 'rule', 'by_owner_only')


class PermitSerializer(serializers.ModelSerializer):
    roles = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Role.objects.all()
    )
    access_rules = AccessRuleSerializer(many=True)

    security_zone_name = serializers.CharField(default=None, allow_null=True)

    keychain_plugin = serializers.CharField(default=None, allow_null=True)
    keychain_id = serializers.CharField(default=None, allow_null=True)

    def create(self, validated_data):
        permit_instance = super().create(validated_data)

        # save access rules for permit
        for access_rule in validated_data['access_rules']:
            access_rule_model = AccessRule(**access_rule)
            access_rule_model.permit = permit_instance
            access_rule_model.save()

        security_zone_name = validated_data.get('security_zone_name', None)
        if security_zone_name:
            security_zone = SecurityZone.objects.get(name=security_zone_name)
            security_zone.permits.add(permit_instance)




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