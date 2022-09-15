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

    def create(self, validated_data):
        pass

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