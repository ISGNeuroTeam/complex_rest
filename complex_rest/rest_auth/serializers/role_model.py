from  rest_framework import serializers
from rest_auth.models import User, Group, Role, Permit


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "is_superuser", "username", "first_name", "last_name",
            "is_staff", "is_active", "guid", "email", "phone", "photo", "groups",
        )


class GroupSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), source='user_set'
    )

    class Meta:
        model = Group
        fields = ['name', 'users']



