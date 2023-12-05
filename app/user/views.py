"""
Views for api
"""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, TokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Create user in view"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create new toke"""
    serializer_class = TokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Get"""
        return self.request.user
