"""
JWT Token Generator for django-oauth-toolkit.
Generates JWT tokens as access tokens instead of random strings.
"""
import time
import uuid
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone


def generate_token(request=None):
    """
    Generate a JWT token to be used as an OAuth2 access token.

    This function is called by django-oauth-toolkit's ACCESS_TOKEN_GENERATOR setting.
    It must return a string token.

    :param request: OAuth2 request object (may be None in some contexts)
    :return: JWT token string
    """
    # Generate unique token ID
    jti = str(uuid.uuid4())

    # Calculate expiration time
    expires_in = settings.OAUTH2_PROVIDER.get('ACCESS_TOKEN_EXPIRE_SECONDS', 3600)
    now = datetime.utcnow()
    exp_time = now + timedelta(seconds=expires_in)

    # Build JWT payload with standard claims
    payload = {
        # Standard JWT claims (RFC 7519)
        'iss': settings.JWT_ISSUER,  # Issuer
        'exp': int(exp_time.timestamp()),  # Expiration time
        'iat': int(now.timestamp()),  # Issued at
        'jti': jti,  # JWT ID (unique identifier)
    }

    # Add OAuth2-specific claims if request is available
    if request:
        # Get client_id from request
        client_id = getattr(request, 'client_id', None)
        if not client_id and hasattr(request, 'client'):
            client_id = request.client.client_id

        if client_id:
            payload['client_id'] = client_id
            payload['aud'] = client_id  # Audience

        # Get scopes
        scopes = getattr(request, 'scopes', [])
        if scopes:
            scope_string = ' '.join(scopes) if isinstance(scopes, list) else str(scopes)
            payload['scope'] = scope_string

        # Get user if available (for non-client_credentials flows)
        user = getattr(request, 'user', None)
        if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
            payload['sub'] = str(user.id)  # Subject (user ID)
            payload['username'] = user.username
            if hasattr(user, 'email') and user.email:
                payload['email'] = user.email
        elif client_id:
            # For client_credentials grant, use client_id as subject
            payload['sub'] = client_id

    # Get the algorithm and private key
    algorithm = getattr(settings, 'JWT_ENC_ALGORITHM', 'RS256')
    issuer_upper = settings.JWT_ISSUER.upper().replace('-', '_')
    private_key_name = f'JWT_PRIVATE_KEY_{issuer_upper}'
    private_key = getattr(settings, private_key_name, None)

    if not private_key:
        raise ValueError(f'Missing JWT private key setting: {private_key_name}')

    # Encode and sign the JWT
    token = jwt.encode(payload, private_key, algorithm=algorithm)

    # PyJWT 2.x returns string directly
    if isinstance(token, bytes):
        return token.decode('utf-8')

    return token
