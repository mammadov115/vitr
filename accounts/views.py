from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserProfileSerializer
from .permissions import IsOwnerOrReadOnly

class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """View for retrieving and updating user profiles"""

    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'username' # Lookup by username in URL