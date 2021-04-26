from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers


from django.contrib.auth.models import User


@api_view(['GET', ])
@permission_classes((permissions.AllowAny,))
def hello(request):
    return Response({'msg': 'Hello world'})


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


