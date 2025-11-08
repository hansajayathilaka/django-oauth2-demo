# JWT OAuth2 Demo Functions - Usage Guide

This guide demonstrates how to use JWT OAuth2 authentication in Django REST Framework function-based views with various scope configurations.

## Table of Contents

1. [Basic Authentication](#1-basic-authentication)
2. [Scope-Based Access Control](#2-scope-based-access-control)
3. [Multiple Scopes](#3-multiple-scopes)
4. [Manual Scope Checking](#4-manual-scope-checking)
5. [Public and Optional Authentication](#5-public-and-optional-authentication)

---

## Prerequisites

First, create an OAuth2 client and get a token:

```bash
# 1. Create client in Django admin
# Go to: http://localhost:8000/admin/oauth2_provider/application/

# 2. Get JWT token
curl -X POST http://localhost:8000/o/token/ \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "scope=read write admin"

# Save the access_token (it's a JWT)
export JWT_TOKEN="<access_token_from_response>"
```

---

## 1. Basic Authentication

### Simple Protected Endpoint

**Code Pattern:**
```python
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from api.jwt_auth import JWTAuthentication

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def demo_simple_protected(request):
    return Response({
        'message': 'You are authenticated!',
        'user': str(request.user),
    })
```

**Usage:**
```bash
# ✅ With valid JWT token
curl -X GET http://localhost:8000/api/demo/simple/ \
  -H "Authorization: Bearer $JWT_TOKEN"

# ❌ Without token (will fail)
curl -X GET http://localhost:8000/api/demo/simple/
```

**Key Points:**
- `@authentication_classes([JWTAuthentication])` - Uses JWT for auth
- `@permission_classes([IsAuthenticated])` - Requires valid token
- Access `request.user` for user info
- Access `request.auth` for token claims

---

## 2. Scope-Based Access Control

### Single Scope Required

**Code Pattern:**
```python
from oauth2_provider.contrib.rest_framework import TokenHasScope

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, TokenHasScope])
def demo_read_scope(request):
    return Response({'message': 'You have read access!'})

# Set required scopes
demo_read_scope.required_scopes = ['read']
```

**Usage:**
```bash
# ✅ With 'read' scope
curl -X GET http://localhost:8000/api/demo/read-scope/ \
  -H "Authorization: Bearer $JWT_TOKEN"

# ❌ Without 'read' scope (will return 403)
```

**Available Scope Examples:**

1. **Read Scope:**
```bash
curl -X GET http://localhost:8000/api/demo/read-scope/ \
  -H "Authorization: Bearer $JWT_TOKEN"
```

2. **Write Scope:**
```bash
curl -X POST http://localhost:8000/api/demo/write-scope/ \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Item", "price": 99.99}'
```

3. **Admin Scope:**
```bash
curl -X GET http://localhost:8000/api/demo/admin/ \
  -H "Authorization: Bearer $JWT_TOKEN"

curl -X DELETE http://localhost:8000/api/demo/admin/ \
  -H "Authorization: Bearer $JWT_TOKEN"
```

---

## 3. Multiple Scopes

### OR Logic (Read OR Write)

**Code Pattern:**
```python
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, TokenHasReadWriteScope])
def demo_read_or_write(request):
    # Accepts tokens with 'read' OR 'write' scope
    return Response({'message': 'You have read or write access'})
```

**Usage:**
```bash
# ✅ Works with 'read' scope
curl -X GET http://localhost:8000/api/demo/read-or-write/ \
  -H "Authorization: Bearer $JWT_TOKEN"

# ✅ Works with 'write' scope
curl -X POST http://localhost:8000/api/demo/read-or-write/ \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "update"}'
```

### AND Logic (Read AND Write)

**Code Pattern:**
```python
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, TokenHasScope])
def demo_multiple_scopes(request):
    # Requires BOTH scopes
    return Response({'message': 'Complex operation'})

demo_multiple_scopes.required_scopes = ['read', 'write']
```

**Usage:**
```bash
# ✅ Works only with BOTH 'read' AND 'write' scopes
curl -X POST http://localhost:8000/api/demo/multi-scope/ \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"operation": "complex"}'

# ❌ Fails if token only has 'read' or only 'write'
```

---

## 4. Manual Scope Checking

### Custom Scope Logic

**Code Pattern:**
```python
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def demo_manual_scope_check(request):
    # Get token scopes
    token_scope = request.auth.get('scope', '') if request.auth else ''
    scopes = set(token_scope.split())

    # Custom logic based on scopes
    if 'admin' in scopes:
        data = {'level': 'admin', 'secrets': 'top secret'}
    elif 'write' in scopes:
        data = {'level': 'write', 'can_edit': True}
    elif 'read' in scopes:
        data = {'level': 'read', 'can_view': True}
    else:
        data = {'level': 'basic'}

    return Response(data)
```

**Usage:**
```bash
# Different responses based on scopes
curl -X GET http://localhost:8000/api/demo/manual-scope/ \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Response varies by scope:**
- **admin scope:** Full access including secrets
- **write scope:** Edit permissions
- **read scope:** View permissions
- **no scopes:** Basic access only

---

## 5. Public and Optional Authentication

### Public Endpoint (No Auth Required)

**Code Pattern:**
```python
@api_view(['GET'])
def demo_public(request):
    # No authentication decorators
    return Response({'message': 'Public endpoint'})
```

**Usage:**
```bash
# ✅ Works without token
curl -X GET http://localhost:8000/api/demo/public/

# ✅ Also works with token (but doesn't require it)
curl -X GET http://localhost:8000/api/demo/public/ \
  -H "Authorization: Bearer $JWT_TOKEN"
```

### Optional Authentication

**Code Pattern:**
```python
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
# Note: No IsAuthenticated permission
def demo_optional_auth(request):
    if request.user and request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'special_data': 'Only for authenticated users'
        })
    else:
        return Response({
            'authenticated': False,
            'message': 'Public data'
        })
```

**Usage:**
```bash
# Without token - gets public data
curl -X GET http://localhost:8000/api/demo/optional-auth/

# With token - gets enhanced data
curl -X GET http://localhost:8000/api/demo/optional-auth/ \
  -H "Authorization: Bearer $JWT_TOKEN"
```

---

## 6. Token Information

### Inspecting JWT Token Claims

**Usage:**
```bash
curl -X GET http://localhost:8000/api/demo/token-info/ \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Response:**
```json
{
  "message": "JWT Token Information",
  "token_claims": {
    "iss": "oauth2-server",
    "exp": 1704067200,
    "iat": 1704063600,
    "jti": "550e8400-e29b-41d4-a716-446655440000",
    "client_id": "your-client-id",
    "aud": "your-client-id",
    "scope": "read write",
    "sub": "your-client-id"
  },
  "user_info": {
    "username": null,
    "is_anonymous": true,
    "is_authenticated": false
  },
  "scope_details": {
    "raw_scope": "read write",
    "parsed_scopes": ["read", "write"],
    "has_read": true,
    "has_write": true,
    "has_admin": false
  }
}
```

---

## Quick Reference

### Decorator Combinations

| Pattern | Code | Use Case |
|---------|------|----------|
| **Protected** | `@authentication_classes([JWTAuthentication])`<br>`@permission_classes([IsAuthenticated])` | Require any valid token |
| **Single Scope** | `@permission_classes([IsAuthenticated, TokenHasScope])`<br>`view.required_scopes = ['read']` | Require specific scope |
| **OR Scopes** | `@permission_classes([IsAuthenticated, TokenHasReadWriteScope])` | Require read OR write |
| **AND Scopes** | `view.required_scopes = ['read', 'write']` | Require multiple scopes |
| **Public** | No decorators | Anyone can access |
| **Optional** | `@authentication_classes([JWTAuthentication])`<br>(no IsAuthenticated) | Enhanced data for auth users |

### Getting Token Data

```python
# User information
request.user.username
request.user.is_authenticated
request.user.is_anonymous

# Token claims
request.auth.get('iss')        # Issuer
request.auth.get('client_id')  # Client ID
request.auth.get('scope')      # Scopes
request.auth.get('sub')        # Subject
request.auth.get('exp')        # Expiration
request.auth.get('jti')        # Token ID

# Check specific scope
scopes = set(request.auth.get('scope', '').split())
if 'admin' in scopes:
    # Admin-only code
```

---

## Complete Test Workflow

```bash
# 1. Get token with all scopes
TOKEN_RESP=$(curl -s -X POST http://localhost:8000/o/token/ \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "scope=read write admin")

JWT_TOKEN=$(echo $TOKEN_RESP | jq -r '.access_token')

# 2. Test public endpoint (no auth)
curl -X GET http://localhost:8000/api/demo/public/

# 3. Test simple auth
curl -X GET http://localhost:8000/api/demo/simple/ \
  -H "Authorization: Bearer $JWT_TOKEN"

# 4. Test read scope
curl -X GET http://localhost:8000/api/demo/read-scope/ \
  -H "Authorization: Bearer $JWT_TOKEN"

# 5. Test write scope
curl -X POST http://localhost:8000/api/demo/write-scope/ \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# 6. Test admin scope
curl -X DELETE http://localhost:8000/api/demo/admin/ \
  -H "Authorization: Bearer $JWT_TOKEN"

# 7. View token details
curl -X GET http://localhost:8000/api/demo/token-info/ \
  -H "Authorization: Bearer $JWT_TOKEN"
```

---

## Troubleshooting

### 401 Unauthorized
- Check if JWT token is included in header
- Verify token hasn't expired
- Ensure `Authorization: Bearer <token>` format

### 403 Forbidden
- Token is valid but lacks required scope
- Check `required_scopes` attribute on view
- Request token with correct scopes

### Token Inspection
Use https://jwt.io to decode your JWT token and verify:
- Expiration time (`exp`)
- Granted scopes (`scope`)
- Client ID (`client_id`)
- Issuer (`iss`)
