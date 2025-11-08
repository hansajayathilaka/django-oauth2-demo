"""
JWT Authentication for Django REST Framework.
Validates JWT tokens that are used as OAuth2 access tokens.
"""
import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.utils.encoding import smart_str
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header


def decode_jwt_token(jwt_value):
    """
    Decode and verify a JWT token.

    :param jwt_value: JWT token string
    :return: Decoded payload dictionary
    """
    # Get issuer from token without verification (to get issuer name)
    unverified = jwt.decode(jwt_value, options={"verify_signature": False})
    issuer = unverified.get('iss', settings.JWT_ISSUER)

    # Get the public key for this issuer
    issuer_upper = issuer.upper().replace('-', '_')
    public_key_name = f'JWT_PUBLIC_KEY_{issuer_upper}'
    public_key = getattr(settings, public_key_name, None)

    if not public_key:
        raise jwt.InvalidTokenError(f'Missing public key setting: {public_key_name}')

    # Get allowed algorithms
    algorithms = getattr(settings, 'JWT_JWS_ALGORITHMS', ['RS256'])

    # Decode and verify the JWT
    decoded = jwt.decode(
        jwt_value,
        public_key,
        algorithms=algorithms,
        options={
            'verify_signature': True,
            'verify_exp': True,
            'verify_iat': True,
        }
    )
    return decoded


class JwtToken(dict):
    """
    Mimics the structure of `AbstractAccessToken` so you can use standard
    Django OAuth Toolkit permissions like `TokenHasScope`.
    """
    def __init__(self, payload):
        super(JwtToken, self).__init__(**payload)

    def __getattr__(self, item):
        return self.get(item)

    def is_valid(self, scopes=None):
        """
        Checks if the access token is valid.

        :param scopes: An iterable containing the scopes to check or None
        """
        return not self.is_expired() and self.allow_scopes(scopes)

    def is_expired(self):
        """
        Check token expiration.
        Expiration is already verified during JWT decode.
        """
        return False

    def allow_scopes(self, scopes):
        """
        Check if the token allows the provided scopes.

        :param scopes: An iterable containing the scopes to check
        """
        if not scopes:
            return True

        token_scope = self.get('scope', '')
        provided_scopes = set(token_scope.split()) if token_scope else set()
        resource_scopes = set(scopes)

        return resource_scopes.issubset(provided_scopes)


class JWTAuthentication(BaseAuthentication):
    """
    JWT token authentication for Django REST Framework.

    Validates JWT tokens that are used as OAuth2 access tokens.
    Clients should authenticate using:
        Authorization: Bearer <jwt_token>
    """
    www_authenticate_realm = 'api'

    def authenticate(self, request):
        """
        Returns a two-tuple of (User, token) if valid JWT is provided.
        Returns None if no JWT is found.
        """
        jwt_value = self._get_jwt_value(request)
        if jwt_value is None:
            return None

        try:
            payload = decode_jwt_token(jwt_value)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Error decoding token')
        except jwt.InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(f'Invalid token: {str(e)}')

        user = self.authenticate_credentials(payload)
        return user, JwtToken(payload)

    def authenticate_credentials(self, payload):
        """
        Returns an active user from the JWT payload.
        For client_credentials tokens (no user), returns AnonymousUser.
        """
        if getattr(settings, 'JWT_AUTH_DISABLED', False):
            return AnonymousUser()

        # Check if this is a user-authenticated token
        user_id = payload.get('sub')
        username = payload.get('username')

        # If no user information, this is a client_credentials token
        if not user_id or not username:
            return AnonymousUser()

        User = get_user_model()

        try:
            user = User.objects.get(id=user_id, username=username)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('User account is disabled')

        return user

    def _get_jwt_value(self, request):
        """
        Extract JWT token from Authorization header.
        """
        auth = get_authorization_header(request).split()
        auth_header_prefix = getattr(settings, 'JWT_AUTH_HEADER_PREFIX', 'Bearer')

        if not auth:
            return None

        if smart_str(auth[0]) != auth_header_prefix:
            return None

        if len(auth) == 1:
            raise exceptions.AuthenticationFailed('Invalid Authorization header. No credentials provided.')
        elif len(auth) > 2:
            raise exceptions.AuthenticationFailed('Invalid Authorization header. Credentials string should not contain spaces.')

        jwt_value = auth[1]
        if isinstance(jwt_value, bytes):
            jwt_value = jwt_value.decode('utf-8')

        return jwt_value

    def authenticate_header(self, _request):
        """
        Return WWW-Authenticate header value for 401 responses.
        """
        auth_header_prefix = getattr(settings, 'JWT_AUTH_HEADER_PREFIX', 'Bearer')
        return f'{auth_header_prefix} realm="{self.www_authenticate_realm}"'
