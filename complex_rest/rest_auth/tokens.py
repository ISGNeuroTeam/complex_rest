import jwt

from jwt import InvalidAlgorithmError, InvalidTokenError
from datetime import timedelta
from uuid import uuid4
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string

from .exceptions import TokenError
from .settings import api_settings
from .utils import (
    aware_utcnow, datetime_from_epoch, datetime_to_epoch, format_lazy,
)


class Token:
    """
    A class which validates and wraps an existing JWT or can be used to build a
    new JWT.
    """
    token_type = None
    lifetime = None

    def __init__(self, token=None, verify=True):
        """
        !!!! IMPORTANT !!!! MUST raise a TokenError with a user-facing error
        message if the given token is invalid, expired, or otherwise not safe
        to use.
        """
        if self.token_type is None or self.lifetime is None:
            raise TokenError(_('Cannot create token with no type or lifetime'))

        self.token = token
        self.current_time = aware_utcnow()

        # Set up token
        if token is not None:
            # An encoded token was provided
            # Decode token
            self.payload = self.decode(token)

            if verify:
                self.verify()
        else:
            # New token.  Skip all the verification steps.
            self.payload = {api_settings.TOKEN_TYPE_CLAIM: self.token_type}

            # Set "exp" claim with default value
            self.set_exp(from_time=self.current_time, lifetime=self.lifetime)

            # Set "iat" claim
            self.set_iat(self.current_time)

            # Set "jti" claim
            self.set_jti()

    def __repr__(self):
        return repr(self.payload)

    def __getitem__(self, key):
        return self.payload[key]

    def __setitem__(self, key, value):
        self.payload[key] = value

    def __delitem__(self, key):
        del self.payload[key]

    def __contains__(self, key):
        return key in self.payload

    def get(self, key, default=None):
        return self.payload.get(key, default)

    def __str__(self):
        """
        Signs and returns a token as a base64 encoded string.
        """
        return self.encode(self.payload)

    def verify(self):
        """
        Performs additional validation steps which were not performed when this
        token was decoded.  This method is part of the "public" API to indicate
        the intention that it may be overridden in subclasses.
        """
        # According to RFC 7519, the "exp" claim is OPTIONAL
        # (https://tools.ietf.org/html/rfc7519#section-4.1.4).  As a more
        # correct behavior for authorization tokens, we require an "exp"
        # claim.  We don't want any zombie tokens walking around.
        self.check_exp()

        # Ensure token id is present
        if api_settings.JTI_CLAIM not in self.payload:
            raise TokenError(_('Token has no id'))

        self.verify_token_type()

    def verify_token_type(self):
        """
        Ensures that the token type claim is present and has the correct value.
        """
        try:
            token_type = self.payload[api_settings.TOKEN_TYPE_CLAIM]
        except KeyError:
            raise TokenError(_('Token has no type'))

        if self.token_type != token_type:
            raise TokenError(_('Token has wrong type'))

    def set_jti(self):
        """
        Populates the configured jti claim of a token with a string where there
        is a negligible probability that the same string will be chosen at a
        later time.

        See here:
        https://tools.ietf.org/html/rfc7519#section-4.1.7
        """
        self.payload[api_settings.JTI_CLAIM] = uuid4().hex

    def set_exp(self, claim='exp', from_time=None, lifetime=None):
        """
        Updates the expiration time of a token.
        """
        if from_time is None:
            from_time = self.current_time

        if lifetime is None:
            lifetime = self.lifetime

        self.payload[claim] = datetime_to_epoch(from_time + lifetime)

    def set_iat(self, issue_time=None, claim='iat', ):
        """
        Updates issue time
        """
        if issue_time is None:
            issue_time = self.current_time

        self.payload[claim] = datetime_to_epoch(issue_time)

    def check_exp(self, claim='exp', current_time=None):
        """
        Checks whether a timestamp value in the given claim has passed (since
        the given datetime value in `current_time`).  Raises a TokenError with
        a user-facing error message if so.
        """
        if current_time is None:
            current_time = self.current_time

        try:
            claim_value = self.payload[claim]
        except KeyError:
            raise TokenError(format_lazy(_("Token has no '{}' claim"), claim))

        claim_time = datetime_from_epoch(claim_value)

        print(claim_time)
        print(current_time)
        if claim_time <= current_time:
            raise TokenError(format_lazy(_("Token '{}' claim has expired"), claim))

    @classmethod
    def for_user(cls, user):
        """
        Returns an authorization token for the given user that will be provided
        after authenticating the user's credentials.
        """
        user_id = getattr(user, api_settings.USER_ID_FIELD)
        if not isinstance(user_id, int):
            user_id = str(user_id)

        token = cls()
        token[api_settings.USER_ID_CLAIM] = user_id

        return token

    @staticmethod
    def generate_secret_key():
        return get_random_string(api_settings.SIGNING_KEY_LENGTH, api_settings.SIGNING_KEY_CHARS)

    @staticmethod
    def get_signing_key():
        """
        Generates signing key if it expires and puts in cache
        Updates old signing key in cache  and returns actual signing key
        """

        key_cache = api_settings.SIGNING_KEY_CACHE
        signing_key = key_cache.get('signing_key')
        if signing_key is None:
            signing_key = Token.generate_secret_key()
            key_cache.set('signing_key', signing_key, timeout=api_settings.SIGNING_KEY_LIFETIME.total_seconds())

        if 'old_signing_key' not in key_cache:
            # assumption that token lifetime two times smaller than signing key lifetime
            key_cache.set(
                'old_signing_key', key_cache.get('signing_key'),
                timeout=api_settings.SIGNING_KEY_LIFETIME.total_seconds()//2
            )
        return signing_key

    @staticmethod
    def get_verification_keys():
        key_cache = api_settings.SIGNING_KEY_CACHE
        return key_cache.get('signing_key'), key_cache.get('old_signing_key')

    @staticmethod
    def decode(token):
        """
        Performs a validation of the given token and returns its payload
        dictionary.

        Raises a `TokenBackendError` if the token is malformed, if its
        signature check fails, or if its 'exp' claim indicates it has expired.
        """
        key, old_key = Token.get_verification_keys()
        try:
            if key:
                return jwt.decode(
                    token, key, algorithms=api_settings.ALGORITHM, verify=True,
                )
            else:
                raise InvalidTokenError
        except InvalidAlgorithmError as ex:
            raise TokenError(_('Invalid algorithm specified')) from ex
        except InvalidTokenError:
            # try to decode with old key
            if old_key:
                try:
                    return jwt.decode(
                        token, old_key, algorithms=api_settings.ALGORITHM, verify=True,
                    )
                except InvalidTokenError:
                    raise TokenError(_('Token is invalid or expired'))
            else:
                raise TokenError(_('Token is invalid or expired'))

    @staticmethod
    def encode(payload):
        """
        Returns an encoded token for the given payload dictionary.
        """

        token = jwt.encode(payload, Token.get_signing_key(), algorithm=api_settings.ALGORITHM)
        if isinstance(token, bytes):
            # For PyJWT <= 1.7.1
            return token.decode('utf-8')
        # For PyJWT >= 2.0.0a1
        return token


class AccessToken(Token):
    token_type = 'access'
    lifetime = api_settings.ACCESS_TOKEN_LIFETIME


class UntypedToken(Token):
    token_type = 'untyped'
    lifetime = timedelta(seconds=0)

    def verify_token_type(self):
        """
        Untyped tokens do not verify the "token_type" claim.  This is useful
        when performing general validation of a token's signature and other
        properties which do not relate to the token's intended use.
        """
        pass
