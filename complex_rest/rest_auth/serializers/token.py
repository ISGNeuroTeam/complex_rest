import importlib

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import update_last_login
from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions, serializers

from rest.serializers import ResponseSerializer

from ..settings import api_settings
from ..tokens import AccessToken


User = get_user_model()
rule_package, user_eligible_for_login = api_settings.USER_AUTHENTICATION_RULE.rsplit('.', 1)
login_rule = importlib.import_module(rule_package)


class PasswordField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('style', {})

        kwargs['style']['input_type'] = 'password'
        kwargs['write_only'] = True

        super().__init__(*args, **kwargs)


class TokenSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = PasswordField()

    default_error_messages = {
        'no_active_account': _('No active account found with the given credentials')
    }

    def validate(self, attrs):
        authenticate_kwargs = {
            User.USERNAME_FIELD: attrs['login'],
            'password': attrs['password'],
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass
        self.user = authenticate(**authenticate_kwargs)
        if not getattr(login_rule, user_eligible_for_login)(self.user):
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )

        return {}

    @classmethod
    def get_token(cls, user):
        raise NotImplementedError('Must implement `get_token` method for `TokenObtainSerializer` subclasses')


class AccessTokenSerializer(TokenSerializer):
    @classmethod
    def get_token(cls, user):
        return AccessToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        data['token'] = str(self.get_token(self.user))

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data



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


class TokenResponseSerializer(ResponseSerializer):
    token = serializers.CharField()


class LogoutResponseSerializer(ResponseSerializer):
    message = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    pass

