from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope


class HelloWorldView(APIView):
    """
    Public endpoint that doesn't require authentication.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "message": "Hello, World!",
            "description": "This is a public endpoint that doesn't require authentication."
        })


class ProtectedView(APIView):
    """
    Protected endpoint that requires OAuth2 authentication.
    """
    # Uses default OAuth2Authentication from settings.py

    def get(self, request):
        return Response({
            "message": "You have successfully authenticated!",
            "user": str(request.user) if request.user else "Anonymous",
            "client_id": request.auth.application.client_id if hasattr(request.auth, 'application') else None,
            "scopes": request.auth.scope if hasattr(request.auth, 'scope') else None,
        })


class ScopedReadView(APIView):
    """
    Endpoint that requires 'read' scope.
    """
    permission_classes = [TokenHasScope]
    required_scopes = ['read']

    def get(self, request):
        return Response({
            "message": "You have read access!",
            "data": [
                {"id": 1, "name": "Item 1"},
                {"id": 2, "name": "Item 2"},
                {"id": 3, "name": "Item 3"},
            ]
        })


class ScopedWriteView(APIView):
    """
    Endpoint that requires 'write' scope.
    """
    permission_classes = [TokenHasScope]
    required_scopes = ['write']

    def post(self, request):
        return Response({
            "message": "You have write access!",
            "created": True,
            "data": request.data
        })

    def get(self, request):
        return Response({
            "message": "This endpoint requires write scope. Use POST to create data.",
        })
