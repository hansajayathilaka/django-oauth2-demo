"""
Demo views showing different ways to use JWT OAuth2 authentication.
"""
from functools import wraps
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from oauth2_provider.contrib.rest_framework import TokenHasScope, TokenHasReadWriteScope

from .jwt_auth import JWTAuthentication


# ============================================================================
# Example 1: Function-based view with decorator authentication
# ============================================================================

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def demo_simple_protected(request):
    """
    Simple protected endpoint using JWT authentication.
    Requires valid JWT token, no specific scope required.

    Usage:
        curl -X GET http://localhost:8000/api/demo/simple/ \
          -H "Authorization: Bearer YOUR_JWT_TOKEN"
    """
    return Response({
        'message': 'You are authenticated!',
        'user': str(request.user),
        'is_anonymous': request.user.is_anonymous,
        'auth_token_info': {
            'issuer': request.auth.get('iss') if request.auth else None,
            'client_id': request.auth.get('client_id') if request.auth else None,
            'scopes': request.auth.get('scope') if request.auth else None,
            'subject': request.auth.get('sub') if request.auth else None,
        }
    })


# ============================================================================
# Example 2: Function-based view with specific scope requirement
# ============================================================================

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, TokenHasScope])
def demo_read_scope(request):
    """
    Endpoint that requires 'read' scope.

    Add required_scopes attribute to the view function.

    Usage:
        curl -X GET http://localhost:8000/api/demo/read-scope/ \
          -H "Authorization: Bearer YOUR_JWT_TOKEN"
    """
    return Response({
        'message': 'You have read access!',
        'data': [
            {'id': 1, 'name': 'Product A', 'price': 29.99},
            {'id': 2, 'name': 'Product B', 'price': 49.99},
            {'id': 3, 'name': 'Product C', 'price': 19.99},
        ],
        'scopes_granted': request.auth.get('scope') if request.auth else None,
    })

# Set required scopes on the wrapped view class
demo_read_scope.cls.required_scopes = ['read']


# ============================================================================
# Example 3: Function-based view with write scope
# ============================================================================

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, TokenHasScope])
def demo_write_scope(request):
    """
    Endpoint that requires 'write' scope.

    Usage:
        curl -X POST http://localhost:8000/api/demo/write-scope/ \
          -H "Authorization: Bearer YOUR_JWT_TOKEN" \
          -H "Content-Type: application/json" \
          -d '{"name": "New Product", "price": 99.99}'
    """
    data = request.data
    return Response({
        'message': 'You have write access!',
        'created': True,
        'data': data,
        'scopes_granted': request.auth.get('scope') if request.auth else None,
    })

demo_write_scope.cls.required_scopes = ['write']


# ============================================================================
# Example 4: Function-based view with multiple scope options (OR)
# ============================================================================

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, TokenHasReadWriteScope])
def demo_read_or_write(request):
    """
    Endpoint that requires either 'read' OR 'write' scope.
    Uses TokenHasReadWriteScope which checks for read OR write.

    Usage:
        # With read scope:
        curl -X GET http://localhost:8000/api/demo/read-or-write/ \
          -H "Authorization: Bearer YOUR_JWT_TOKEN"

        # With write scope:
        curl -X POST http://localhost:8000/api/demo/read-or-write/ \
          -H "Authorization: Bearer YOUR_JWT_TOKEN" \
          -H "Content-Type: application/json" \
          -d '{"action": "update"}'
    """
    if request.method == 'GET':
        return Response({
            'message': 'Reading data (requires read or write scope)',
            'method': 'GET',
            'scopes': request.auth.get('scope') if request.auth else None,
        })
    else:
        return Response({
            'message': 'Writing data (requires read or write scope)',
            'method': 'POST',
            'data': request.data,
            'scopes': request.auth.get('scope') if request.auth else None,
        })


# ============================================================================
# Example 5: Function-based view with admin scope
# ============================================================================

@api_view(['GET', 'POST', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, TokenHasScope])
def demo_admin_scope(request):
    """
    Endpoint that requires 'admin' scope.
    Allows full CRUD operations.

    Usage:
        curl -X GET http://localhost:8000/api/demo/admin/ \
          -H "Authorization: Bearer YOUR_JWT_TOKEN"
    """
    actions = {
        'GET': 'View all system settings',
        'POST': 'Create new system configuration',
        'DELETE': 'Delete system resources',
    }

    return Response({
        'message': f'Admin access granted: {actions.get(request.method)}',
        'method': request.method,
        'admin_access': True,
        'scopes': request.auth.get('scope') if request.auth else None,
    })

demo_admin_scope.cls.required_scopes = ['admin']


# ============================================================================
# Example 6: Manual scope checking within the view
# ============================================================================

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def demo_manual_scope_check(request):
    """
    Endpoint with custom scope logic.
    Manually checks scopes and returns different data based on permissions.

    Usage:
        curl -X GET http://localhost:8000/api/demo/manual-scope/ \
          -H "Authorization: Bearer YOUR_JWT_TOKEN"
    """
    # Get token scopes
    token_scope = request.auth.get('scope', '') if request.auth else ''
    scopes = set(token_scope.split())

    response_data = {
        'message': 'Scope-based data access',
        'your_scopes': list(scopes),
    }

    # Different data based on scopes
    if 'admin' in scopes:
        response_data['access_level'] = 'admin'
        response_data['data'] = {
            'public': 'Everyone can see this',
            'internal': 'Only authenticated users see this',
            'sensitive': 'Only admins see this',
            'secrets': 'Top secret admin data',
        }
    elif 'write' in scopes:
        response_data['access_level'] = 'write'
        response_data['data'] = {
            'public': 'Everyone can see this',
            'internal': 'Only authenticated users see this',
            'sensitive': 'Only write/admin users see this',
        }
    elif 'read' in scopes:
        response_data['access_level'] = 'read'
        response_data['data'] = {
            'public': 'Everyone can see this',
            'internal': 'Only authenticated users see this',
        }
    else:
        response_data['access_level'] = 'basic'
        response_data['data'] = {
            'public': 'Everyone can see this',
        }

    return Response(response_data)


# ============================================================================
# Example 7: Multiple scopes required (AND logic)
# ============================================================================

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, TokenHasScope])
def demo_multiple_scopes(request):
    """
    Endpoint that requires BOTH 'read' AND 'write' scopes.

    Usage:
        # This requires a token with "read write" scopes:
        curl -X POST http://localhost:8000/api/demo/multi-scope/ \
          -H "Authorization: Bearer YOUR_JWT_TOKEN" \
          -H "Content-Type: application/json" \
          -d '{"operation": "complex"}'
    """
    return Response({
        'message': 'You have both read and write access!',
        'operation': 'Complex operation requiring multiple permissions',
        'data': request.data,
        'scopes': request.auth.get('scope') if request.auth else None,
    })

demo_multiple_scopes.cls.required_scopes = ['read', 'write']


# ============================================================================
# Example 8: Token information endpoint
# ============================================================================

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def demo_token_info(request):
    """
    Endpoint that displays all information from the JWT token.
    Useful for debugging and understanding token contents.

    Usage:
        curl -X GET http://localhost:8000/api/demo/token-info/ \
          -H "Authorization: Bearer YOUR_JWT_TOKEN"
    """
    if not request.auth:
        return Response({'error': 'No authentication token found'}, status=401)

    # Extract all token information
    token_data = dict(request.auth) if request.auth else {}

    return Response({
        'message': 'JWT Token Information',
        'token_claims': token_data,
        'user_info': {
            'username': request.user.username if not request.user.is_anonymous else None,
            'is_anonymous': request.user.is_anonymous,
            'is_authenticated': request.user.is_authenticated,
            'user_id': request.user.id if not request.user.is_anonymous else None,
        },
        'scope_details': {
            'raw_scope': token_data.get('scope', ''),
            'parsed_scopes': token_data.get('scope', '').split() if token_data.get('scope') else [],
            'has_read': 'read' in token_data.get('scope', ''),
            'has_write': 'write' in token_data.get('scope', ''),
            'has_admin': 'admin' in token_data.get('scope', ''),
        }
    })


# ============================================================================
# Example 9: Public endpoint (no authentication required)
# ============================================================================

@api_view(['GET'])
@permission_classes([])  # Override default permission classes - no authentication required
def demo_public(request):
    """
    Public endpoint that doesn't require authentication.
    No decorators for authentication or permissions.

    Usage:
        curl -X GET http://localhost:8000/api/demo/public/
    """
    return Response({
        'message': 'This is a public endpoint',
        'authentication_required': False,
        'anyone_can_access': True,
    })


# ============================================================================
# Example 10: Conditional authentication (optional JWT)
# ============================================================================

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([])  # Override default - authentication is optional
def demo_optional_auth(request):
    """
    Endpoint where authentication is optional.
    Returns different data based on whether user is authenticated.

    Note: No IsAuthenticated permission, so it accepts both authenticated
    and unauthenticated requests.

    Usage:
        # Without token:
        curl -X GET http://localhost:8000/api/demo/optional-auth/

        # With token:
        curl -X GET http://localhost:8000/api/demo/optional-auth/ \
          -H "Authorization: Bearer YOUR_JWT_TOKEN"
    """
    if request.user and request.user.is_authenticated:
        return Response({
            'message': 'Welcome authenticated user!',
            'authenticated': True,
            'user': str(request.user),
            'scopes': request.auth.get('scope') if request.auth else None,
            'special_data': 'This is only shown to authenticated users',
        })
    else:
        return Response({
            'message': 'Welcome anonymous user!',
            'authenticated': False,
            'hint': 'Provide a JWT token to see more data',
        })
