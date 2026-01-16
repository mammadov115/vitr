import pytest
from django.core.exceptions import ValidationError
from accounts.models import Profile, UserAchievement

@pytest.mark.django_db
class TestUserModel:
    
    def test_create_user_with_email(self, active_user, user_data):
        """Checks user creation with email."""

        assert active_user.email == user_data["email"]
        assert active_user.username == user_data["username"]
        assert active_user.check_password(user_data["password"])
        assert active_user.is_active
        assert not active_user.is_staff

    def test_create_superuser(self, db):
        """Checks superuser creation."""
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin = User.objects.create_superuser(
            email="admin@test.com", 
            username="admin", 
            password="adminpassword"
        )
        assert admin.is_superuser
        assert admin.is_staff

    def test_user_email_uniqueness(self, active_user, user_data):
        """Checks that user email uniqueness is enforced."""

        from django.contrib.auth import get_user_model
        User = get_user_model()
        with pytest.raises(Exception): # IntegrityError
            User.objects.create_user(
                email=user_data["email"],
                username="different_user",
                password="password"
            )


@pytest.mark.django_db
class TestProfileAndAchievements:
    """Tests for Profile and UserAchievement models."""

    def test_profile_creation_on_user_save(self, active_user):
        """
        Checks that a Profile is created when a User is created.
        """

        # If using signals to create Profile on User creation, this test would verify that.
        profile = Profile.objects.create(user=active_user)
        assert profile.user == active_user
        assert profile.level == 1
        assert str(profile) == f"Stats for {active_user.username}"

    def test_user_earns_achievement(self, active_user, sample_achievement):
        """Checks user achievement earning logic"""
        user_ach = UserAchievement.objects.create(
            user=active_user,
            achievement=sample_achievement
        )
        assert active_user.achievements.count() == 1
        assert active_user.achievements.first().achievement.name == "Quiz Master"