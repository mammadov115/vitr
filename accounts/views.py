from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from accounts.models import User, Achievement
from accounts.serializers import UserProfileSerializer, RegisterSerializer, AchievementSerializer
from core.permissions import IsOwnerOrReadOnly
from rest_framework_simplejwt.views import TokenObtainPairView



class RegisterView(generics.CreateAPIView):
    """View for user registration"""
    
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
            operation_summary="Register a new user", 
            operation_description="Endpoint for user registration."
    )
    def post(self, request, *args, **kwargs):
        """Handle user registration requests."""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": RegisterSerializer(user).data,
            "message": "User registered successfully.",
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    User login (Login) endpoint.
    Email and password are sent to return 'access' and 'refresh' tokens.
    """
    @swagger_auto_schema(
        operation_summary="User login (Login)",
        operation_description="Email and password are sent to return 'access' and 'refresh' tokens."
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    

class MyProfileView(generics.RetrieveUpdateAPIView):
    """
    View for retrieving and updating the authenticated user's own profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # For the authenticated user, return their own profile.
        # request.user is the authenticated user instance.
        return self.request.user

    @swagger_auto_schema(operation_summary="Get personal profile information")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update personal profile")
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @swagger_auto_schema(auto_schema=None)
    def put(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class PublicProfileView(generics.RetrieveAPIView):
    """
    View for retrieving public profiles of users by username.
    For example: /api/v1/accounts/profile/user99/
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'username'

    @swagger_auto_schema(operation_summary="View public profile")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AchievementListView(generics.ListAPIView):
    """
    View for listing all achievements.
    """
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_summary="List all achievements")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
