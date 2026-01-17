import pytest
from accounts.serializers import UserProfileSerializer, RegisterSerializer
from accounts.models import Profile, UserAchievement
from django.contrib.auth import get_user_model


User = get_user_model()


@pytest.mark.django_db
class TestUserProfileSerializer:
    """For testing UserProfileSerializer functionality"""

    def test_serializer_output_structure(self, active_user, sample_achievement):
        # 1. This is the setup phase: Create necessary related objects
        profile, _ = Profile.objects.get_or_create(user=active_user, level=10)
        UserAchievement.objects.create(user=active_user, achievement=sample_achievement)

        # 2. Execution: Serialize the user instance
        serializer = UserProfileSerializer(instance=active_user)
        data = serializer.data

        # 3. Verification: Check the serialized data structure and content
        assert data['username'] == active_user.username
        assert data['email'] == active_user.email
        assert data['profile']['level'] == 10
        
        # Check earned achievements
        assert len(data['earned_achievements']) == 1
        assert data['earned_achievements'][0]['achievement']['name'] == sample_achievement.name

    def test_time_played_display_logic(self, active_user):
        """Test the time_played_display field formatting in ProfileSerializer. (e.g., "2h 30m")"""
        from datetime import timedelta
        profile, _ = Profile.objects.get_or_create(
            user=active_user, 
            time_played=timedelta(hours=2, minutes=30)
        )
        
        serializer = UserProfileSerializer(instance=active_user)
        # Verify the formatted time played display
        assert serializer.data['profile']['time_played_display'] == "2h 30m"


@pytest.mark.django_db
class TestRegisterSerializer:
    """For testing RegisterSerializer functionality"""

    def test_register_serializer_valid_data(self):
        """Test successful user registration with valid data."""

        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!"
        }
        
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        
        user = serializer.save()
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("StrongPassword123!")
        assert User.objects.count() == 1

    def test_register_serializer_passwords_mismatch(self):
        """Test registration fails when passwords do not match."""
        
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "ComplexPassword99!@#",
            "password_confirm": "DifferentPassword456"
        }
        
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors
        # Check the specific error message
        assert serializer.errors["password"][0] == "Password fields didn't match."

    def test_register_serializer_duplicate_email(self, active_user):
        """Test registration fails when using an email that already exists."""

        data = {
            "username": "newuser",
            "email": active_user.email,  # Duplicate email
            "password": "Password123!",
            "password_confirm": "Password123!"
        }
        
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_register_serializer_weak_password(self):
        """Test registration fails with a weak password."""

        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123", # Weak password
            "password_confirm": "123"
        }
        
        serializer = RegisterSerializer(data=data)
        # Django's standard validate_password rules will be applied
        assert not serializer.is_valid()
        assert "password" in serializer.errors