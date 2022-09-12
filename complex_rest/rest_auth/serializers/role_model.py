from  rest_framework import serializers
from rest_auth.models import User, Group, Role, Permit


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), source='user_set'
    )

    class Meta:
        model = Group
        fields = ['name', 'users']



